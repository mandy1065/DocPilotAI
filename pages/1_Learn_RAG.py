from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Learn RAG", page_icon="📘", layout="wide")

BASE = Path(__file__).resolve().parent.parent
LEARNING_DIR = BASE / "learning"

MODULES = [
    {
        "id": "01",
        "title": "What is RAG?",
        "file": "module_01_what_is_rag.pptx",
        "goal": "Understand why RAG is used and how it helps an AI chatbot answer from documents.",
        "exercise": "Arrange the RAG pipeline in the correct order: LLM answer, PDF upload, retrieval, chunking, embeddings.",
        "answer": "PDF upload → chunking → embeddings → retrieval → LLM answer",
        "lab": "Upload a PDF in DocPilotAI and ask one simple fact-based question. Check whether the evidence supports the answer.",
    },
    {
        "id": "02",
        "title": "RAG Architecture",
        "file": "module_02_rag_architecture.pptx",
        "goal": "Identify the main RAG components and understand where failures can happen.",
        "exercise": "If the answer is wrong and the evidence is unrelated, which component likely failed first?",
        "answer": "The retriever likely failed first because it selected irrelevant chunks. Then grounding/prompting should also be checked.",
        "lab": "Ask a question and expand grounding evidence. Decide whether the answer failure is retrieval, answer generation, or both.",
    },
    {
        "id": "03",
        "title": "Chunking",
        "file": "module_03_chunking.pptx",
        "goal": "Understand chunk size, overlap, and how bad chunking causes incomplete answers.",
        "exercise": "For a return policy, why should ‘30 days’ and ‘if unopened’ stay close together?",
        "answer": "Because the condition changes the meaning. If retrieved separately, the agent may answer only ‘30 days’ and miss the unopened requirement.",
        "lab": "Ask a condition-based question, such as: ‘How many days do I have to return goods, and are there conditions?’",
    },
    {
        "id": "04",
        "title": "Embeddings",
        "file": "module_04_embeddings.pptx",
        "goal": "Explain embeddings as meaning converted into searchable numeric patterns.",
        "exercise": "Which sentence is closest to: ‘How long is the reset link valid?’ A) Link expires after 30 minutes B) Change profile photo C) Support hours",
        "answer": "A) Link expires after 30 minutes. It has the closest meaning to the question.",
        "lab": "Ask the same question using different wording and see whether DocPilotAI still retrieves relevant evidence.",
    },
    {
        "id": "05",
        "title": "Vector Search & Retrieval",
        "file": "module_05_vector_search_retrieval.pptx",
        "goal": "Understand Top-K retrieval and how QA evaluates retrieved evidence.",
        "exercise": "What should QA check first when an answer seems wrong?",
        "answer": "Check whether the retrieved evidence contains the answer and whether it is relevant to the question.",
        "lab": "Ask 3 questions and inspect evidence for each. Mark evidence as Relevant, Partially Relevant, or Irrelevant.",
    },
    {
        "id": "06",
        "title": "Grounding & Hallucination",
        "file": "module_06_grounding_hallucination.pptx",
        "goal": "Classify answers as grounded, partially grounded, or hallucinated.",
        "exercise": "Answer says ‘refunds take 10 business days’ but evidence only says ‘returns within 30 days.’ What is it?",
        "answer": "Hallucinated or unsupported, because refund processing time is not in the evidence.",
        "lab": "Find one answer where the answer and evidence do not fully match. Convert it into a bug report.",
    },
    {
        "id": "07",
        "title": "RAG Testing + Final Project",
        "file": "module_07_rag_testing_final_project.pptx",
        "goal": "Use DocPilotAI to create test cases, execute tests, log bugs, and download a QA report.",
        "exercise": "Create 5 starter test cases: happy path, negative, grounding, retrieval, and edge/prompt robustness.",
        "answer": "Each test case should include scenario, question, expected answer, expected evidence, actual answer, PASS/FAIL, and notes.",
        "lab": "Complete the final project: 15 test cases, 3 defects, QA score review, and final report download.",
    },
]

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at 5% 0%, rgba(99,102,241,.12), transparent 28%), radial-gradient(circle at 95% 5%, rgba(14,165,233,.11), transparent 25%), #f8fafc;}
.block-container {max-width: 1200px; padding-top: 1.2rem;}
.hero {background: linear-gradient(135deg,#0f172a,#172554 55%,#312e81); color:white; border-radius:24px; padding:26px 30px; box-shadow:0 18px 45px rgba(15,23,42,.16);}
.card {background:white; border:1px solid #e5e7eb; border-radius:18px; padding:18px; box-shadow:0 6px 22px rgba(15,23,42,.05); margin:12px 0;}
.kicker {color:#4f46e5; font-size:12px; text-transform:uppercase; font-weight:850; letter-spacing:.08em;}
.title {font-size:24px; font-weight:850; color:#0f172a;}
.flow {background:#0f172a; color:#dbeafe; padding:14px 16px; border-radius:14px; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; white-space:pre-wrap;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div style="font-size:32px;font-weight:900;letter-spacing:-.02em">📘 RAG for QA Students</div>
  <div style="color:#dbeafe;margin-top:6px">Visual PPT modules + small exercises + final hands-on DocPilotAI project.</div>
  <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap">
    <span style="padding:6px 10px;border:1px solid rgba(255,255,255,.14);border-radius:999px;background:rgba(255,255,255,.08)">7 modules</span>
    <span style="padding:6px 10px;border:1px solid rgba(255,255,255,.14);border-radius:999px;background:rgba(255,255,255,.08)">PPT + exercise</span>
    <span style="padding:6px 10px;border:1px solid rgba(255,255,255,.14);border-radius:999px;background:rgba(255,255,255,.08)">Final AI QA project</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Learning path")
st.markdown("""
<div class="flow">What is RAG → RAG Architecture → Chunking → Embeddings → Vector Search → Grounding/Hallucination → RAG Testing Project</div>
""", unsafe_allow_html=True)

labels = [f"{m['id']} — {m['title']}" for m in MODULES]
selected = st.selectbox("Choose module", labels)
module = MODULES[labels.index(selected)]

left, right = st.columns([1.1, .9], gap="large")
with left:
    st.markdown(f"<div class='card'><div class='kicker'>Module {module['id']}</div><div class='title'>{module['title']}</div><p>{module['goal']}</p></div>", unsafe_allow_html=True)
    ppt_path = LEARNING_DIR / module["file"]
    if ppt_path.exists():
        st.download_button(
            "⬇ Download visual PPT for this module",
            data=ppt_path.read_bytes(),
            file_name=module["file"],
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )
    else:
        st.warning("PPT generation is still pending. Refresh after the GitHub Actions build completes.")

    with st.expander("🧪 Small exercise", expanded=True):
        st.write(module["exercise"])
        if st.button("Show suggested answer", key=f"answer_{module['id']}"):
            st.success(module["answer"])

with right:
    st.markdown("<div class='card'><div class='kicker'>Hands-on lab</div><div class='title'>Apply this in DocPilotAI</div></div>", unsafe_allow_html=True)
    st.info(module["lab"])
    st.markdown("""
**Final project expectation**

By the end, students should:
- upload a PDF
- ask multiple RAG QA questions
- inspect evidence
- create test cases
- log defects
- review the QA score
- download the final QA report
""")

st.divider()
st.markdown("### Instructor use")
st.write("Teach each PPT first, run the small exercise, then open the DocPilotAI lab for practical testing. Module 7 becomes the final student project.")
