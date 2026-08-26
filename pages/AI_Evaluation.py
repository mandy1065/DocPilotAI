import json
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Evaluation | DocPilot AI", page_icon="🎓", layout="wide")

MODEL = st.secrets.get("OPENAI_MODEL", "gpt-5.4-nano")
PASS_THRESHOLD = 70

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(99,102,241,.13), transparent 28%),
            radial-gradient(circle at 95% 10%, rgba(14,165,233,.10), transparent 25%),
            #f7f9fc;
    }
    .block-container {max-width: 1180px;padding-top:1.4rem;padding-bottom:3rem;}
    .hero {
        background:linear-gradient(135deg,#0f172a 0%,#172554 52%,#312e81 100%);
        border-radius:24px;padding:24px 28px;color:white;margin-bottom:18px;
        box-shadow:0 18px 45px rgba(15,23,42,.18);
    }
    .hero-title {font-size:28px;font-weight:800;margin-bottom:4px;}
    .hero-copy {color:#cbd5e1;font-size:14px;}
    .kicker {color:#6366f1;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;}
    .section-title {font-size:22px;font-weight:800;color:#0f172a;margin:2px 0 8px 0;}
    .rubric-card {
        background:#fff;border:1px solid #e5e7eb;border-radius:16px;padding:14px 16px;
        box-shadow:0 5px 18px rgba(15,23,42,.04);height:100%;
    }
    div[data-testid="stMetric"] {
        background:#fff;border:1px solid #e5e7eb;padding:14px 16px;border-radius:16px;
        box-shadow:0 5px 18px rgba(15,23,42,.04);
    }
    .stButton > button,.stDownloadButton > button {border-radius:12px;font-weight:700;}
    footer {visibility:hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_client():
    key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        st.error("OPENAI_API_KEY is missing from Streamlit Secrets.")
        st.stop()
    return OpenAI(api_key=key)


client = get_client()


def submission_signature():
    payload = {
        "pdf": st.session_state.get("pdf_name"),
        "tests": st.session_state.get("tests", []),
        "bugs": st.session_state.get("bugs", []),
    }
    return json.dumps(payload, sort_keys=True, default=str)


def build_evidence_packet():
    """Attach the most relevant PDF evidence to each student test case."""
    tests = st.session_state.get("tests", [])
    vectorizer = st.session_state.get("vectorizer")
    matrix = st.session_state.get("matrix")
    chunks = st.session_state.get("chunks", [])

    if vectorizer is None or matrix is None or not chunks:
        return []

    from sklearn.metrics.pairwise import cosine_similarity

    packet = []
    for test in tests:
        question = str(test.get("question", "")).strip()
        if not question:
            evidence = []
        else:
            q = vectorizer.transform([question])
            scores = cosine_similarity(q, matrix).flatten()
            order = scores.argsort()[::-1][:3]
            evidence = [
                {
                    "page": chunks[i].get("page"),
                    "text": str(chunks[i].get("text", ""))[:900],
                }
                for i in order
            ]
        packet.append({"test": test, "pdf_evidence": evidence})
    return packet


def extract_json(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Evaluator did not return valid JSON.")
    return json.loads(text[start:end + 1])


def normalize_score(value, maximum):
    try:
        value = float(value)
    except Exception:
        value = 0
    return round(max(0, min(maximum, value)), 1)


def evaluate_submission():
    tests = st.session_state.get("tests", [])
    bugs = st.session_state.get("bugs", [])
    evidence_packet = build_evidence_packet()

    categories = sorted({str(t.get("category", "")).strip() for t in tests if t.get("category")})
    failed_ids = [str(t.get("id")) for t in tests if t.get("status") == "FAIL"]

    grading_data = {
        "pdf_name": st.session_state.get("pdf_name"),
        "student_test_cases_with_pdf_evidence": evidence_packet,
        "student_bug_reports": bugs,
        "observed_categories": categories,
        "failed_test_ids": failed_ids,
    }

    prompt = f"""
You are a strict but fair senior AI QA instructor grading a student's manual AI testing assignment.

The student tested a PDF-grounded chatbot. Grade the STUDENT'S QA WORK, not the chatbot itself.
Use only the supplied student submission and the PDF evidence attached to each test case. Do not use outside knowledge.

RUBRIC — exactly 100 points total:
1. Test case quality: 30 points
   - clear scenarios, meaningful prompts, correct structure, useful expected/actual results.
2. Coverage: 20 points
   - breadth across happy path, negative/out-of-scope, hallucination/grounding, retrieval, and edge cases.
3. Expected-result correctness: 20 points
   - expected answers must be supported by the provided PDF evidence; do not reward invented expectations.
4. PASS/FAIL execution accuracy: 15 points
   - status should reasonably match expected vs actual behavior.
5. Bug report quality: 15 points
   - valid issue, clear title, sensible type/severity, reproducible steps, expected vs actual, and linkage to a failed test where appropriate.

IMPORTANT GRADING RULES:
- Do not give points just because fields are filled in.
- Penalize duplicate or superficial test cases.
- Penalize expected results contradicted by PDF evidence.
- Penalize marking an incorrect actual answer as PASS or a correct answer as FAIL.
- A bug should describe an actual failure from the submitted execution evidence. Penalize unsupported bugs.
- Do not require exactly 15 tests or 3 bugs to give a useful evaluation, but lack of breadth/coverage should lower the score.
- Keep feedback concise and specific.

Return STRICT JSON only, with this exact structure:
{{
  "test_case_quality": {{"score": 0, "max": 30, "feedback": ""}},
  "coverage": {{"score": 0, "max": 20, "feedback": ""}},
  "expected_result_correctness": {{"score": 0, "max": 20, "feedback": ""}},
  "execution_accuracy": {{"score": 0, "max": 15, "feedback": ""}},
  "bug_report_quality": {{"score": 0, "max": 15, "feedback": ""}},
  "strengths": [""],
  "improvements": [""],
  "test_reviews": [
    {{"id": "TC-001", "assessment": "Good|Needs Work|Incorrect", "comment": ""}}
  ],
  "bug_reviews": [
    {{"id": "BUG-001", "assessment": "Valid|Needs Work|Unsupported", "comment": ""}}
  ],
  "summary": ""
}}

STUDENT SUBMISSION:
{json.dumps(grading_data, ensure_ascii=False)}
""".strip()

    response = client.responses.create(model=MODEL, input=prompt)
    result = extract_json(response.output_text)

    rubric = [
        ("test_case_quality", 30),
        ("coverage", 20),
        ("expected_result_correctness", 20),
        ("execution_accuracy", 15),
        ("bug_report_quality", 15),
    ]
    total = 0
    for key, maximum in rubric:
        result.setdefault(key, {})
        result[key]["score"] = normalize_score(result[key].get("score", 0), maximum)
        result[key]["max"] = maximum
        result[key].setdefault("feedback", "")
        total += result[key]["score"]

    result["overall_score"] = round(total, 1)
    result["result"] = "PASS" if total >= PASS_THRESHOLD else "FAIL"
    result["evaluated_at"] = datetime.now().isoformat(timespec="seconds")
    return result


st.markdown(
    """
    <div class="hero">
      <div class="hero-title">🎓 AI Evaluation Agent</div>
      <div class="hero-copy">Submit your manually designed test cases and bug reports for instructor-style AI grading grounded in the uploaded PDF.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

pdf_name = st.session_state.get("pdf_name")
tests = st.session_state.get("tests", [])
bugs = st.session_state.get("bugs", [])

if not pdf_name:
    st.warning("Go back to DocPilot AI, upload/process the assignment PDF, then return here.")
    st.stop()

st.markdown('<div class="kicker">Submission</div><div class="section-title">Ready for evaluation</div>', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.metric("PDF", pdf_name)
m2.metric("Test Cases", len(tests), "Target 15")
m3.metric("Bug Reports", len(bugs), "Target 3")

r1, r2, r3, r4, r5 = st.columns(5)
for col, title, points in [
    (r1, "Test Quality", "30 pts"),
    (r2, "Coverage", "20 pts"),
    (r3, "Expected Results", "20 pts"),
    (r4, "PASS / FAIL", "15 pts"),
    (r5, "Bug Quality", "15 pts"),
]:
    col.markdown(f'<div class="rubric-card"><b>{title}</b><br><span style="color:#64748b">{points}</span></div>', unsafe_allow_html=True)

st.write("")
if len(tests) < 1:
    st.info("Create at least one manual test case before evaluation.")
elif st.button("✦ Evaluate My Submission", type="primary", use_container_width=True):
    with st.spinner("Evaluation agent is checking your test design, PDF grounding, execution decisions, and bug reports..."):
        try:
            result = evaluate_submission()
            st.session_state["ai_evaluation"] = result
            st.session_state["ai_evaluation_signature"] = submission_signature()
            st.success("Evaluation complete.")
        except Exception as exc:
            st.error(f"Evaluation could not be completed: {exc}")

result = st.session_state.get("ai_evaluation")
if result:
    if st.session_state.get("ai_evaluation_signature") != submission_signature():
        st.warning("Your test cases or bugs changed after this evaluation. Run Evaluate My Submission again for an updated score.")

    st.divider()
    overall = result.get("overall_score", 0)
    status = result.get("result", "FAIL")
    a, b, c = st.columns(3)
    a.metric("Overall Score", f"{overall}%")
    b.metric("Result", status)
    c.metric("Pass Threshold", f"{PASS_THRESHOLD}%")

    if status == "PASS":
        st.success(f"✅ PASS — {overall}%")
    else:
        st.error(f"❌ FAIL — {overall}%")

    rubric_rows = []
    labels = {
        "test_case_quality": "Test Case Quality",
        "coverage": "Coverage",
        "expected_result_correctness": "Expected Result Correctness",
        "execution_accuracy": "PASS/FAIL Accuracy",
        "bug_report_quality": "Bug Report Quality",
    }
    for key, label in labels.items():
        item = result.get(key, {})
        rubric_rows.append({
            "Area": label,
            "Score": item.get("score", 0),
            "Max": item.get("max", 0),
            "Feedback": item.get("feedback", ""),
        })
    st.subheader("Rubric breakdown")
    st.dataframe(pd.DataFrame(rubric_rows), use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Strengths")
        for item in result.get("strengths", []):
            if item:
                st.write(f"• {item}")
    with c2:
        st.subheader("What to improve")
        for item in result.get("improvements", []):
            if item:
                st.write(f"• {item}")

    if result.get("test_reviews"):
        st.subheader("Test case review")
        st.dataframe(pd.DataFrame(result["test_reviews"]), use_container_width=True, hide_index=True)

    if result.get("bug_reviews"):
        st.subheader("Bug report review")
        st.dataframe(pd.DataFrame(result["bug_reviews"]), use_container_width=True, hide_index=True)

    if result.get("summary"):
        st.subheader("Instructor feedback")
        st.write(result["summary"])

    final_report = {
        "student_name": st.session_state.get("student_name", ""),
        "student_id": st.session_state.get("student_id", ""),
        "pdf": pdf_name,
        "test_cases": tests,
        "bugs": bugs,
        "ai_evaluation": result,
    }
    st.download_button(
        "↓ Download evaluated submission",
        json.dumps(final_report, indent=2, ensure_ascii=False).encode(),
        f"{st.session_state.get('student_name') or 'student'}_evaluated_submission.json",
        "application/json",
        type="primary",
        use_container_width=True,
    )

st.caption("The evaluation agent grades the student's QA work against PDF evidence. It does not replace instructor review for high-stakes grading.")
