import json
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="DocPilot AI", page_icon="📄", layout="wide")

MODEL = st.secrets.get("OPENAI_MODEL", "gpt-5.4-nano")
TOP_K = 4
MAX_ANSWER_CHARS = int(st.secrets.get("MAX_ANSWER_CHARS", 180))
TEACHING_BUG_MODE = str(st.secrets.get("TEACHING_BUG_MODE", "true")).strip().lower() in {"1", "true", "yes", "on"}
TARGET_TESTS = 15
TARGET_BUGS = 3
PASS_THRESHOLD = 70

TEST_CATEGORIES = [
    "Happy Path",
    "Negative / Out-of-Scope",
    "Hallucination / Grounding",
    "Retrieval",
    "Edge Case / Prompt Robustness",
    "Other",
]
BUG_TYPES = [
    "Hallucination",
    "Wrong Answer",
    "Retrieval Failure",
    "Incomplete Answer",
    "Out-of-Scope Handling",
    "Evidence / Citation Issue",
    "UI / UX",
    "Other",
]
SEVERITIES = ["Low", "Medium", "High", "Critical"]


def get_client():
    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        st.error("OPENAI_API_KEY is missing from Streamlit Secrets.")
        st.stop()
    return OpenAI(api_key=key)


client = get_client()

DEFAULTS = {
    "student_name": "",
    "student_id": "",
    "pdf_name": None,
    "chunks": [],
    "vectorizer": None,
    "matrix": None,
    "messages": [],
    "last_question": "",
    "last_answer": "",
    "tests": [],
    "bugs": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def extract_pages(file):
    file.seek(0)
    reader = PdfReader(file)
    pages = []
    for n, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((n, text))
    return pages


def chunk_pages(pages, size=1200, overlap=200):
    chunks = []
    for page_no, text in pages:
        start = 0
        idx = 1
        while start < len(text):
            end = min(start + size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append({"page": page_no, "id": f"p{page_no}_c{idx}", "text": piece})
            if end >= len(text):
                break
            start = end - overlap
            idx += 1
    return chunks


def index_chunks(chunks):
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=25000)
    matrix = vectorizer.fit_transform([c["text"] for c in chunks])
    return vectorizer, matrix


def retrieve(question):
    q = st.session_state.vectorizer.transform([question])
    scores = cosine_similarity(q, st.session_state.matrix).flatten()
    order = scores.argsort()[::-1][:TOP_K]
    return [{**st.session_state.chunks[i], "score": float(scores[i])} for i in order]


def compact_answer(text, max_chars=180):
    """Keep replies chatbot-like: direct, short, and readable."""
    text = " ".join((text or "").split())
    if not text:
        return "I don't know based on the uploaded document."
    if len(text) <= max_chars:
        return text

    for marker in [". ", "? ", "! "]:
        if marker in text:
            first = text.split(marker, 1)[0] + marker.strip()
            if len(first) <= max_chars:
                return first

    clipped = text[: max_chars - 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return clipped + "…"


def corrupt_numeric_answer(answer):
    """Change the first numeric fact so the result is clearly wrong for QA practice."""
    match = re.search(r"\b(\d+(?:\.\d+)?)\b", answer)
    if not match:
        return None

    original = match.group(1)
    if "." in original:
        wrong = str(round(float(original) + 5, 2))
    else:
        wrong = str(int(original) + 5)
    return answer[:match.start()] + wrong + answer[match.end():]


def training_defect(question_number, answer, evidence):
    """Make exactly every second answer defective when teaching mode is enabled."""
    if not TEACHING_BUG_MODE or question_number % 2 == 1:
        return answer, evidence

    # Even questions are intentionally defective: 2, 4, 6, 8, ...
    defect_slot = (question_number // 2) % 3

    # Wrong factual value when the answer contains a number; otherwise false negative.
    if defect_slot == 1:
        wrong_answer = corrupt_numeric_answer(answer)
        if wrong_answer:
            return wrong_answer, evidence
        return "I don't know based on the uploaded document.", evidence

    # Retrieval / false-negative defect.
    if defect_slot == 2:
        return "I don't know based on the uploaded document.", evidence

    # Incomplete-answer defect; fall back to false negative if answer is too short.
    if len(answer) > 35:
        short = answer[:35].rsplit(" ", 1)[0].rstrip(" ,;:-") + "…"
        return short, evidence
    return "I don't know based on the uploaded document.", evidence


def ask_pdf(question, question_number):
    evidence = retrieve(question)
    context = "\n\n---\n\n".join(
        f"[Page {x['page']} | {x['id']}]\n{x['text']}" for x in evidence
    )
    prompt = f"""
You are DocPilot AI, a friendly PDF question-answering chatbot.

RULES:
1. Answer only from the supplied PDF context.
2. Never use outside knowledge.
3. If the answer is not supported, reply exactly: "I don't know based on the uploaded document."
4. Give the direct answer first. Sound natural, like a chatbot.
5. Keep the entire answer to 1-2 short sentences and ideally under {MAX_ANSWER_CHARS} characters.
6. Do not quote long document passages.
7. Do not include page numbers in the answer; source details are shown separately in the UI.
8. Include an important condition only when leaving it out would make the answer misleading.
9. Never invent facts, dates, numbers, names, policies, or conditions.

PDF CONTEXT:
{context}

QUESTION:
{question}
""".strip()
    response = client.responses.create(model=MODEL, input=prompt)
    answer = compact_answer(response.output_text.strip(), MAX_ANSWER_CHARS)
    answer, evidence = training_defect(question_number, answer, evidence)
    return answer, evidence


def test_score():
    tests = st.session_state.tests
    if not tests:
        return 0.0
    volume = min(len(tests) / TARGET_TESTS, 1) * 25
    fields = ["id", "scenario", "category", "question", "expected", "actual", "status"]
    completeness = sum(
        sum(bool(str(t.get(f, "")).strip()) for f in fields) / len(fields)
        for t in tests
    ) / len(tests) * 35
    wanted = {"Happy Path", "Negative / Out-of-Scope", "Hallucination / Grounding", "Retrieval", "Edge Case / Prompt Robustness"}
    coverage = len(wanted & {t["category"] for t in tests}) / len(wanted) * 20
    execution = sum(
        (bool(t["actual"].strip()) + (t["status"] in {"PASS", "FAIL"}) + (len(t["notes"].strip()) >= 10)) / 3
        for t in tests
    ) / len(tests) * 20
    return round(volume + completeness + coverage + execution, 1)


def bug_score():
    bugs = st.session_state.bugs
    if not bugs:
        return 0.0
    volume = min(len(bugs) / TARGET_BUGS, 1) * 20
    fields = ["id", "title", "severity", "type", "steps", "expected", "actual"]
    completeness = sum(
        sum(bool(str(b.get(f, "")).strip()) for f in fields) / len(fields)
        for b in bugs
    ) / len(bugs) * 50
    repro = sum(1 if len(b["steps"].strip()) >= 30 else 0.5 for b in bugs) / len(bugs) * 15
    failed = {t["id"] for t in st.session_state.tests if t["status"] == "FAIL"}
    linkage = sum(bool(b["linked"] and b["linked"] in failed) for b in bugs) / len(bugs) * 15
    return round(volume + completeness + repro + linkage, 1)


st.title("📄 DocPilot AI")
st.caption("Document Intelligence Agent • AI QA Student Testing Lab")

with st.container(border=True):
    c1, c2 = st.columns(2)
    st.session_state.student_name = c1.text_input("Student Name *", value=st.session_state.student_name)
    st.session_state.student_id = c2.text_input("Student ID / Email", value=st.session_state.student_id)

uploaded = st.file_uploader("Upload a text-based PDF", type=["pdf"])
if uploaded and st.button("Process PDF", type="primary"):
    pages = extract_pages(uploaded)
    chunks = chunk_pages(pages)
    if not chunks:
        st.error("No extractable text found. Use a text-based PDF, not a scanned image-only PDF.")
    else:
        vectorizer, matrix = index_chunks(chunks)
        st.session_state.pdf_name = uploaded.name
        st.session_state.chunks = chunks
        st.session_state.vectorizer = vectorizer
        st.session_state.matrix = matrix
        st.session_state.messages = []
        st.session_state.last_question = ""
        st.session_state.last_answer = ""
        st.success(f"Ready: {uploaded.name} • {len(chunks)} searchable chunks")

if st.session_state.pdf_name:
    st.info(f"Active PDF: **{st.session_state.pdf_name}**")

tab_chat, tab_tests, tab_bugs, tab_score = st.tabs(["💬 Chatbot", "📝 Test Cases", "🐞 Bugs", "🎓 Score"])

with tab_chat:
    st.subheader("Test the PDF agent")
    st.caption("Ask normal, negative, edge-case, and grounding questions. Use Show source when you want to inspect retrieval evidence.")
    if not st.session_state.pdf_name:
        st.warning("Upload and process a PDF first.")
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if m.get("evidence"):
                    with st.expander("Show source"):
                        for e in m["evidence"]:
                            st.caption(f"Page {e['page']}")
                            st.write(e["text"])
        question = st.chat_input("Ask a question about the PDF...")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            question_number = sum(1 for m in st.session_state.messages if m["role"] == "user")
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Answering from the PDF..."):
                    answer, evidence = ask_pdf(question, question_number)
                st.markdown(answer)
                with st.expander("Show source"):
                    for e in evidence:
                        st.caption(f"Page {e['page']}")
                        st.write(e["text"])
            st.session_state.messages.append({"role": "assistant", "content": answer, "evidence": evidence})
            st.session_state.last_question = question
            st.session_state.last_answer = answer

with tab_tests:
    st.subheader("Write test cases")
    st.caption(f"Recommended target: {TARGET_TESTS} test cases across multiple AI QA categories.")
    with st.form("test_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        tc_id = c1.text_input("Test Case ID *", value=f"TC-{len(st.session_state.tests)+1:03d}")
        scenario = c1.text_input("Scenario / Title *")
        category = c1.selectbox("Category *", TEST_CATEGORIES)
        status = c2.selectbox("Status *", ["PASS", "FAIL"])
        question = c2.text_area("Question / Input *", value=st.session_state.last_question)
        expected = st.text_area("Expected Result *")
        actual = st.text_area("Actual Result *", value=st.session_state.last_answer)
        notes = st.text_area("Tester Notes")
        save = st.form_submit_button("Add Test Case", type="primary")
    if save:
        if not st.session_state.student_name.strip():
            st.error("Enter Student Name first.")
        elif not all(x.strip() for x in [tc_id, scenario, question, expected, actual]):
            st.error("Complete all required fields.")
        else:
            st.session_state.tests.append({"id": tc_id.strip(), "scenario": scenario.strip(), "category": category, "question": question.strip(), "expected": expected.strip(), "actual": actual.strip(), "status": status, "notes": notes.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
            st.success(f"{tc_id} added.")
    if st.session_state.tests:
        df = pd.DataFrame(st.session_state.tests)
        st.dataframe(df[["id", "scenario", "category", "status", "question"]], use_container_width=True, hide_index=True)
        st.download_button("Download Test Cases CSV", df.to_csv(index=False).encode(), f"{st.session_state.student_name or 'student'}_test_cases.csv", "text/csv")

with tab_bugs:
    st.subheader("Submit bugs separately")
    failed_ids = [t["id"] for t in st.session_state.tests if t["status"] == "FAIL"]
    with st.form("bug_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        bug_id = c1.text_input("Bug ID *", value=f"BUG-{len(st.session_state.bugs)+1:03d}")
        title = c1.text_input("Bug Title *")
        severity = c1.selectbox("Severity *", SEVERITIES)
        bug_type = c2.selectbox("Bug Type *", BUG_TYPES)
        linked = c2.selectbox("Link to Failed Test", [""] + failed_ids)
        steps = st.text_area("Steps to Reproduce *", placeholder="1. Upload PDF\n2. Ask the question\n3. Observe the response")
        expected = st.text_area("Expected Behaviour *")
        actual = st.text_area("Actual Behaviour *", value=st.session_state.last_answer)
        save_bug = st.form_submit_button("Add Bug", type="primary")
    if save_bug:
        if not st.session_state.student_name.strip():
            st.error("Enter Student Name first.")
        elif not all(x.strip() for x in [bug_id, title, steps, expected, actual]):
            st.error("Complete all required fields.")
        else:
            st.session_state.bugs.append({"id": bug_id.strip(), "title": title.strip(), "severity": severity, "type": bug_type, "linked": linked, "steps": steps.strip(), "expected": expected.strip(), "actual": actual.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
            st.success(f"{bug_id} added.")
    if st.session_state.bugs:
        df = pd.DataFrame(st.session_state.bugs)
        st.dataframe(df[["id", "title", "severity", "type", "linked"]], use_container_width=True, hide_index=True)
        st.download_button("Download Bugs CSV", df.to_csv(index=False).encode(), f"{st.session_state.student_name or 'student'}_bugs.csv", "text/csv")

with tab_score:
    st.subheader("Assignment Score")
    ts = test_score()
    bs = bug_score()
    overall = round(ts * 0.70 + bs * 0.30, 1)
    result = "PASS" if overall >= PASS_THRESHOLD else "FAIL"
    q_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Questions Asked", q_count)
    m2.metric("Test Cases", len(st.session_state.tests), f"Target {TARGET_TESTS}")
    m3.metric("Bugs", len(st.session_state.bugs), f"Target {TARGET_BUGS}")
    m4.metric("Pass Threshold", f"{PASS_THRESHOLD}%")
    c1, c2, c3 = st.columns(3)
    c1.metric("Test Case Score", f"{ts}%")
    c2.metric("Bug Report Score", f"{bs}%")
    c3.metric("Overall Score", f"{overall}%")
    st.success(f"✅ {result} — {overall}%") if result == "PASS" else st.error(f"❌ {result} — {overall}%")
    report = {"student_name": st.session_state.student_name, "student_id": st.session_state.student_id, "pdf": st.session_state.pdf_name, "questions_asked": q_count, "test_case_score": ts, "bug_score": bs, "overall_score": overall, "result": result, "test_cases": st.session_state.tests, "bugs": st.session_state.bugs}
    st.download_button("Download Final Report JSON", json.dumps(report, indent=2).encode(), f"{st.session_state.student_name or 'student'}_final_report.json", "application/json", type="primary")
    st.caption("Work is stored in this browser session only. Download your files before closing or resetting the app.")
