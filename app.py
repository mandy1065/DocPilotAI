import json
import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="DocPilot AI", page_icon="🤖", layout="wide")

# The root app stays hidden from the student course navigation. Opening the
# direct root URL sends students to Learn RAG first. The dedicated project page
# sets DOCPILOT_PROJECT_PAGE=1 and executes this file as the final project.
if os.environ.get("DOCPILOT_PROJECT_PAGE") != "1" and not st.session_state.get("open_ai_qa_project", False):
    st.switch_page("pages/1_Learn_RAG.py")

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

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(99,102,241,.13), transparent 28%),
            radial-gradient(circle at 95% 10%, rgba(14,165,233,.10), transparent 25%),
            #f7f9fc;
    }
    .block-container {max-width: 1280px;padding-top: 1.4rem;padding-bottom: 3rem;}
    .agent-hero {background: linear-gradient(135deg, #0f172a 0%, #172554 52%, #312e81 100%);border:1px solid rgba(255,255,255,.10);border-radius:24px;padding:24px 28px;margin-bottom:18px;box-shadow:0 18px 45px rgba(15,23,42,.18);color:white;}
    .agent-title {display:flex;align-items:center;gap:14px;font-size:30px;font-weight:800;letter-spacing:-.02em;margin-bottom:4px;}
    .agent-orb {width:46px;height:46px;border-radius:16px;display:grid;place-items:center;background:linear-gradient(135deg,#22d3ee,#6366f1);box-shadow:0 0 30px rgba(34,211,238,.32);font-size:24px;}
    .agent-subtitle {color:#cbd5e1;font-size:14px;margin-left:60px;}
    .chip-row {display:flex;gap:8px;flex-wrap:wrap;margin-top:16px;margin-left:60px;}.chip {display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:650;color:#e2e8f0;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);}.dot {width:7px;height:7px;border-radius:50%;background:#34d399;box-shadow:0 0 10px #34d399;}
    div[data-testid="stContainer"] {border-radius:18px;} div[data-testid="stChatMessage"] {border:1px solid #e7eaf0;background:rgba(255,255,255,.86);border-radius:18px;padding:8px 10px;box-shadow:0 5px 16px rgba(15,23,42,.04);} div[data-testid="stChatMessage"] p {font-size:15px;line-height:1.55;}
    div[data-testid="stExpander"] {border:1px solid #e2e8f0;border-radius:14px;background:#fbfcfe;}.stTabs [data-baseweb="tab-list"] {gap:8px;background:#eef2f7;padding:6px;border-radius:14px;}.stTabs [data-baseweb="tab"] {height:42px;border-radius:10px;padding-left:18px;padding-right:18px;font-weight:700;}.stTabs [aria-selected="true"] {background:#ffffff !important;box-shadow:0 2px 8px rgba(15,23,42,.08);}
    div[data-testid="stMetric"] {background:#ffffff;border:1px solid #e5e7eb;padding:14px 16px;border-radius:16px;box-shadow:0 5px 18px rgba(15,23,42,.04);}.status-card {background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;padding:14px 16px;box-shadow:0 5px 18px rgba(15,23,42,.04);margin-bottom:14px;}.status-label {font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:.06em;}.status-value {font-size:14px;color:#0f172a;font-weight:700;margin-top:3px;}.section-kicker {color:#6366f1;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;}.section-title {font-size:22px;font-weight:800;color:#0f172a;margin-bottom:2px;}.section-copy {font-size:13px;color:#64748b;margin-bottom:14px;}.stButton > button,.stDownloadButton > button {border-radius:12px;font-weight:700;}div[data-testid="stFileUploader"] {background:#ffffff;border:1px dashed #cbd5e1;padding:8px;border-radius:16px;}div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea,div[data-baseweb="select"] > div {border-radius:12px !important;}footer {visibility:hidden;}
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

DEFAULTS = {"student_name":"","student_id":"","pdf_name":None,"chunks":[],"vectorizer":None,"matrix":None,"messages":[],"last_question":"","last_answer":"","tests":[],"bugs":[]}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

def extract_pages(file):
    file.seek(0); reader=PdfReader(file); pages=[]
    for n,page in enumerate(reader.pages,1):
        text=(page.extract_text() or "").strip()
        if text: pages.append((n,text))
    return pages

def chunk_pages(pages,size=1200,overlap=200):
    chunks=[]
    for page_no,text in pages:
        start=0; idx=1
        while start < len(text):
            end=min(start+size,len(text)); piece=text[start:end].strip()
            if piece: chunks.append({"page":page_no,"id":f"p{page_no}_c{idx}","text":piece})
            if end >= len(text): break
            start=end-overlap; idx+=1
    return chunks

def index_chunks(chunks):
    vectorizer=TfidfVectorizer(stop_words="english",ngram_range=(1,2),max_features=25000)
    matrix=vectorizer.fit_transform([c["text"] for c in chunks])
    return vectorizer,matrix

def retrieve(question):
    q=st.session_state.vectorizer.transform([question]); scores=cosine_similarity(q,st.session_state.matrix).flatten(); order=scores.argsort()[::-1][:TOP_K]
    return [{**st.session_state.chunks[i],"score":float(scores[i])} for i in order]

def compact_answer(text,max_chars=180):
    text=" ".join((text or "").split())
    if not text: return "I don't know based on the uploaded document."
    if len(text)<=max_chars: return text
    for marker in [". ","? ","! "]:
        if marker in text:
            first=text.split(marker,1)[0]+marker.strip()
            if len(first)<=max_chars: return first
    clipped=text[:max_chars-1].rsplit(" ",1)[0].rstrip(" ,;:-")
    return clipped+"…"

def corrupt_numeric_answer(answer):
    match=re.search(r"\b(\d+(?:\.\d+)?)\b",answer)
    if not match: return None
    original=match.group(1); wrong=str(round(float(original)+5,2)) if "." in original else str(int(original)+5)
    return answer[:match.start()]+wrong+answer[match.end():]

def training_defect(question_number,answer,evidence):
    if not TEACHING_BUG_MODE or question_number%2==1: return answer,evidence
    defect_slot=(question_number//2)%3
    if defect_slot==1:
        wrong_answer=corrupt_numeric_answer(answer)
        if wrong_answer: return wrong_answer,evidence
        return "I don't know based on the uploaded document.",evidence
    if defect_slot==2: return "I don't know based on the uploaded document.",evidence
    if len(answer)>35:
        short=answer[:35].rsplit(" ",1)[0].rstrip(" ,;:-")+"…"
        return short,evidence
    return "I don't know based on the uploaded document.",evidence

def ask_pdf(question,question_number):
    evidence=retrieve(question)
    context="\n\n---\n\n".join(f"[Page {x['page']} | {x['id']}]\n{x['text']}" for x in evidence)
    prompt=f"""You are DocPilot AI, a friendly PDF question-answering chatbot.
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
{question}""".strip()
    response=client.responses.create(model=MODEL,input=prompt)
    answer=compact_answer(response.output_text.strip(),MAX_ANSWER_CHARS)
    return training_defect(question_number,answer,evidence)

def test_score():
    tests=st.session_state.tests
    if not tests: return 0.0
    volume=min(len(tests)/TARGET_TESTS,1)*25; fields=["id","scenario","category","question","expected","actual","status"]
    completeness=sum(sum(bool(str(t.get(f," ")).strip()) for f in fields)/len(fields) for t in tests)/len(tests)*35
    wanted={"Happy Path","Negative / Out-of-Scope","Hallucination / Grounding","Retrieval","Edge Case / Prompt Robustness"}
    coverage=len(wanted & {t["category"] for t in tests})/len(wanted)*20
    execution=sum((bool(t["actual"].strip())+(t["status"] in {"PASS","FAIL"})+(len(t["notes"].strip())>=10))/3 for t in tests)/len(tests)*20
    return round(volume+completeness+coverage+execution,1)

def bug_score():
    bugs=st.session_state.bugs
    if not bugs: return 0.0
    volume=min(len(bugs)/TARGET_BUGS,1)*20; fields=["id","title","severity","type","steps","expected","actual"]
    completeness=sum(sum(bool(str(b.get(f," ")).strip()) for f in fields)/len(fields) for b in bugs)/len(bugs)*50
    repro=sum(1 if len(b["steps"].strip())>=30 else .5 for b in bugs)/len(bugs)*15
    failed={t["id"] for t in st.session_state.tests if t["status"]=="FAIL"}
    linkage=sum(bool(b["linked"] and b["linked"] in failed) for b in bugs)/len(bugs)*15
    return round(volume+completeness+repro+linkage,1)

st.markdown(f"""<div class="agent-hero"><div class="agent-title"><div class="agent-orb">✦</div><span>DocPilot AI</span></div><div class="agent-subtitle">Document Intelligence Agent · AI QA Student Testing Lab</div><div class="chip-row"><span class="chip"><span class="dot"></span> Agent online</span><span class="chip">⚡ {MODEL}</span><span class="chip">📄 PDF grounded</span><span class="chip">🧪 QA workspace</span></div></div>""",unsafe_allow_html=True)

left,right=st.columns([1.15,1],gap="large")
with left:
    with st.container(border=True):
        st.markdown('<div class="section-kicker">Session</div><div class="section-title">Tester identity</div><div class="section-copy">Identify your QA session before recording test evidence.</div>',unsafe_allow_html=True)
        c1,c2=st.columns(2); st.session_state.student_name=c1.text_input("Student Name *",value=st.session_state.student_name); st.session_state.student_id=c2.text_input("Student ID / Email",value=st.session_state.student_id)
with right:
    with st.container(border=True):
        st.markdown('<div class="section-kicker">Knowledge source</div><div class="section-title">Connect a PDF</div><div class="section-copy">Upload a text-based document and let the agent build a searchable index.</div>',unsafe_allow_html=True)
        uploaded=st.file_uploader("Upload PDF",type=["pdf"],label_visibility="collapsed")
        if uploaded and st.button("⚡ Process document",type="primary",use_container_width=True):
            pages=extract_pages(uploaded); chunks=chunk_pages(pages)
            if not chunks: st.error("No extractable text found. Use a text-based PDF, not a scanned image-only PDF.")
            else:
                vectorizer,matrix=index_chunks(chunks); st.session_state.pdf_name=uploaded.name; st.session_state.chunks=chunks; st.session_state.vectorizer=vectorizer; st.session_state.matrix=matrix; st.session_state.messages=[]; st.session_state.last_question=""; st.session_state.last_answer=""; st.success(f"Indexed {len(chunks)} searchable chunks")

if st.session_state.pdf_name:
    q_count=sum(1 for m in st.session_state.messages if m["role"]=="user"); s1,s2,s3=st.columns(3)
    s1.markdown(f'<div class="status-card"><div class="status-label">Active source</div><div class="status-value">📄 {st.session_state.pdf_name}</div></div>',unsafe_allow_html=True)
    s2.markdown('<div class="status-card"><div class="status-label">Agent status</div><div class="status-value">🟢 Ready for questions</div></div>',unsafe_allow_html=True)
    s3.markdown(f'<div class="status-card"><div class="status-label">Session activity</div><div class="status-value">💬 {q_count} questions asked</div></div>',unsafe_allow_html=True)

st.markdown("<div style='height:4px'></div>",unsafe_allow_html=True)
tab_chat,tab_tests,tab_bugs,tab_score=st.tabs(["✦ Agent Chat","🧪 Test Cases","🐞 Defects","📊 QA Score"])
with tab_chat:
    st.markdown('<div class="section-kicker">Agent console</div><div class="section-title">Ask DocPilot</div><div class="section-copy">Probe the document with normal, negative, edge-case, retrieval, and grounding questions. Expand source evidence only when needed.</div>',unsafe_allow_html=True)
    if not st.session_state.pdf_name: st.info("Connect and process a PDF to activate the agent.")
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if m.get("evidence"):
                    with st.expander("View grounding evidence"):
                        for e in m["evidence"]: st.caption(f"Page {e['page']}"); st.write(e["text"])
        question=st.chat_input("Message DocPilot about the uploaded PDF...")
        if question:
            st.session_state.messages.append({"role":"user","content":question}); question_number=sum(1 for m in st.session_state.messages if m["role"]=="user")
            with st.chat_message("user"): st.markdown(question)
            with st.chat_message("assistant"):
                with st.spinner("Agent is retrieving evidence and reasoning..."): answer,evidence=ask_pdf(question,question_number)
                st.markdown(answer)
                with st.expander("View grounding evidence"):
                    for e in evidence: st.caption(f"Page {e['page']}"); st.write(e["text"])
            st.session_state.messages.append({"role":"assistant","content":answer,"evidence":evidence}); st.session_state.last_question=question; st.session_state.last_answer=answer

with tab_tests:
    st.markdown('<div class="section-kicker">QA execution</div><div class="section-title">Test case workspace</div>',unsafe_allow_html=True); st.caption(f"Target: {TARGET_TESTS} test cases across multiple AI QA categories.")
    with st.container(border=True):
        with st.form("test_form",clear_on_submit=True):
            c1,c2=st.columns(2); tc_id=c1.text_input("Test Case ID *",value=f"TC-{len(st.session_state.tests)+1:03d}"); scenario=c1.text_input("Scenario / Title *"); category=c1.selectbox("Category *",TEST_CATEGORIES); status=c2.selectbox("Execution Status *",["PASS","FAIL"]); question=c2.text_area("Prompt / Input *",value=st.session_state.last_question); expected=st.text_area("Expected Result *"); actual=st.text_area("Actual Agent Result *",value=st.session_state.last_answer); notes=st.text_area("Tester Notes"); save=st.form_submit_button("＋ Add test case",type="primary",use_container_width=True)
    if save:
        if not st.session_state.student_name.strip(): st.error("Enter Student Name first.")
        elif not all(x.strip() for x in [tc_id,scenario,question,expected,actual]): st.error("Complete all required fields.")
        else: st.session_state.tests.append({"id":tc_id.strip(),"scenario":scenario.strip(),"category":category,"question":question.strip(),"expected":expected.strip(),"actual":actual.strip(),"status":status,"notes":notes.strip(),"created_at":datetime.now().isoformat(timespec="seconds")}); st.success(f"{tc_id} added.")
    if st.session_state.tests:
        df=pd.DataFrame(st.session_state.tests); st.dataframe(df[["id","scenario","category","status","question"]],use_container_width=True,hide_index=True); st.download_button("↓ Export test cases CSV",df.to_csv(index=False).encode(),f"{st.session_state.student_name or 'student'}_test_cases.csv","text/csv")

with tab_bugs:
    st.markdown('<div class="section-kicker">Defect triage</div><div class="section-title">Bug reporting workspace</div>',unsafe_allow_html=True); failed_ids=[t["id"] for t in st.session_state.tests if t["status"]=="FAIL"]
    with st.container(border=True):
        with st.form("bug_form",clear_on_submit=True):
            c1,c2=st.columns(2); bug_id=c1.text_input("Bug ID *",value=f"BUG-{len(st.session_state.bugs)+1:03d}"); title=c1.text_input("Bug Title *"); severity=c1.selectbox("Severity *",SEVERITIES); bug_type=c2.selectbox("Bug Type *",BUG_TYPES); linked=c2.selectbox("Link to Failed Test",[""]+failed_ids); steps=st.text_area("Steps to Reproduce *",placeholder="1. Upload PDF\n2. Ask the question\n3. Observe the response"); expected=st.text_area("Expected Behaviour *"); actual=st.text_area("Actual Behaviour *",value=st.session_state.last_answer); save_bug=st.form_submit_button("＋ Log defect",type="primary",use_container_width=True)
    if save_bug:
        if not st.session_state.student_name.strip(): st.error("Enter Student Name first.")
        elif not all(x.strip() for x in [bug_id,title,steps,expected,actual]): st.error("Complete all required fields.")
        else: st.session_state.bugs.append({"id":bug_id.strip(),"title":title.strip(),"severity":severity,"type":bug_type,"linked":linked,"steps":steps.strip(),"expected":expected.strip(),"actual":actual.strip(),"created_at":datetime.now().isoformat(timespec="seconds")}); st.success(f"{bug_id} added.")
    if st.session_state.bugs:
        df=pd.DataFrame(st.session_state.bugs); st.dataframe(df[["id","title","severity","type","linked"]],use_container_width=True,hide_index=True); st.download_button("↓ Export defects CSV",df.to_csv(index=False).encode(),f"{st.session_state.student_name or 'student'}_bugs.csv","text/csv")

with tab_score:
    st.markdown('<div class="section-kicker">Evaluation</div><div class="section-title">QA performance dashboard</div><div class="section-copy">Your score reflects test design, execution evidence, defect quality, and linkage.</div>',unsafe_allow_html=True); ts=test_score(); bs=bug_score(); overall=round(ts*.70+bs*.30,1); result="PASS" if overall>=PASS_THRESHOLD else "FAIL"; q_count=sum(1 for m in st.session_state.messages if m["role"]=="user"); m1,m2,m3,m4=st.columns(4); m1.metric("Questions",q_count); m2.metric("Test Cases",len(st.session_state.tests),f"Target {TARGET_TESTS}"); m3.metric("Defects",len(st.session_state.bugs),f"Target {TARGET_BUGS}"); m4.metric("Threshold",f"{PASS_THRESHOLD}%"); c1,c2,c3=st.columns(3); c1.metric("Test Design",f"{ts}%"); c2.metric("Defect Quality",f"{bs}%"); c3.metric("Overall QA Score",f"{overall}%")
    if result=="PASS": st.success(f"✅ PASS — {overall}%")
    else: st.error(f"❌ FAIL — {overall}%")
    report={"student_name":st.session_state.student_name,"student_id":st.session_state.student_id,"pdf":st.session_state.pdf_name,"questions_asked":q_count,"test_case_score":ts,"bug_score":bs,"overall_score":overall,"result":result,"test_cases":st.session_state.tests,"bugs":st.session_state.bugs}
    st.download_button("↓ Download final QA report",json.dumps(report,indent=2).encode(),f"{st.session_state.student_name or 'student'}_final_report.json","application/json",type="primary"); st.caption("Session data is temporary. Download your files before closing or resetting the app.")
