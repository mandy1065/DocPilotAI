import streamlit as st

st.set_page_config(page_title="Learn RAG for QA", page_icon="🧠", layout="wide")

MODULES = [
    {
        "id": "01",
        "title": "What is RAG?",
        "goal": "Understand what RAG is, why it exists, and how a document question becomes an AI answer.",
        "why": "A normal LLM answers from what it learned during training. A RAG system first looks inside a trusted knowledge source and then gives the LLM relevant evidence. For QA, this creates two things to test: retrieval and the final answer.",
        "concepts": [
            ("RAG", "Retrieval-Augmented Generation: retrieve useful evidence first, then generate an answer."),
            ("Knowledge source", "The trusted content the system searches, such as a PDF, policy, manual, or database."),
            ("Retrieval", "Finding the most relevant pieces of the source for the user's question."),
            ("Generation", "The LLM creates the final response using the retrieved evidence."),
        ],
        "diagram": ["📄 PDF / Knowledge", "✂️ Chunks", "🔢 Embeddings", "🔎 Retrieval", "🧠 LLM", "💬 Answer"],
        "example": {
            "source": "Password reset links expire after 30 minutes.",
            "question": "How long is the password reset link valid?",
            "retrieved": "Password reset links expire after 30 minutes.",
            "answer": "The password reset link is valid for 30 minutes.",
        },
        "qa": [
            "Did the system retrieve the right evidence?",
            "Is the answer supported by that evidence?",
            "Did the model add anything that was not in the source?",
        ],
        "questions": [
            ("What does RAG stand for?", "Retrieval-Augmented Generation."),
            ("Why not send the entire PDF to the LLM every time?", "Large documents are expensive and noisy. RAG retrieves only the most relevant pieces so the model gets focused context."),
            ("What are the two major areas a QA tester must validate?", "Retrieval quality and answer quality/grounding."),
            ("If the answer is wrong, does it always mean the LLM failed?", "No. The retriever may have returned the wrong evidence, so QA should inspect evidence before deciding the root cause."),
        ],
        "exercise": "Put these in the correct order: LLM answer, PDF, retrieval, chunking, embeddings.",
        "exercise_answer": "PDF → chunking → embeddings → retrieval → LLM answer",
    },
    {
        "id": "02",
        "title": "RAG Architecture",
        "goal": "Understand the major RAG components and where defects can happen.",
        "why": "A RAG chatbot is a pipeline. A defect in an early component can create a bad final answer even when the LLM itself is behaving correctly.",
        "concepts": [
            ("Loader", "Reads the source document."),
            ("Chunker", "Splits long content into smaller searchable pieces."),
            ("Embedding model", "Transforms text meaning into numeric vectors."),
            ("Vector store / index", "Stores searchable representations of chunks."),
            ("Retriever", "Selects the best chunks for a question."),
            ("Prompt + LLM", "Uses the retrieved evidence to create the final answer."),
        ],
        "diagram": ["📥 Loader", "✂️ Chunker", "🔢 Embed", "🗂️ Index", "🔎 Retriever", "🧠 LLM"],
        "example": {
            "source": "Return policy: items may be returned within 30 days if unopened.",
            "question": "Can I return an opened product after 20 days?",
            "retrieved": "items may be returned within 30 days if unopened",
            "answer": "No. The policy requires the item to be unopened.",
        },
        "qa": ["Find which pipeline stage failed first.", "Separate retrieval defects from generation defects.", "Validate source, context, and final response independently."],
        "questions": [
            ("What does the retriever do?", "It selects the chunks that appear most relevant to the user's question."),
            ("If the retrieved chunk is unrelated, where should QA investigate first?", "Retrieval/indexing/embedding behavior before blaming the final LLM answer."),
            ("Why inspect each component separately?", "Because the final symptom can be caused by an earlier pipeline failure."),
        ],
        "exercise": "The chatbot gives a wrong answer and the displayed evidence is unrelated. Which component likely failed first?",
        "exercise_answer": "The retrieval stage likely failed first because irrelevant chunks were selected.",
    },
    {
        "id": "03",
        "title": "Chunking",
        "goal": "Understand chunk size, overlap, context boundaries, and why chunking directly affects answer quality.",
        "why": "Retrieval usually searches chunks, not whole documents. If important facts are split badly, the correct answer may never reach the LLM.",
        "concepts": [
            ("Chunk", "A smaller section of a larger document."),
            ("Chunk size", "How much text is placed in one chunk."),
            ("Overlap", "Repeated text between adjacent chunks to preserve context across boundaries."),
            ("Boundary problem", "A condition or fact may be separated from the sentence it belongs to."),
        ],
        "diagram": ["📄 Long document", "✂️ Chunk A", "↔️ overlap", "✂️ Chunk B", "↔️ overlap", "✂️ Chunk C"],
        "example": {
            "source": "Employees receive 15 vacation days. Unused days cannot be carried forward unless a manager approves an exception.",
            "question": "Can unused vacation days be carried forward?",
            "retrieved": "Unused days cannot be carried forward unless a manager approves an exception.",
            "answer": "Normally no, unless a manager approves an exception.",
        },
        "qa": ["Test facts near chunk boundaries.", "Test questions that need two neighboring facts.", "Check whether conditions and exceptions remain attached to the main rule."],
        "questions": [
            ("What happens if chunks are too small?", "Important context may be separated, producing incomplete retrieval."),
            ("What happens if chunks are too large?", "Retrieval can become noisy because one chunk contains too many unrelated ideas."),
            ("Why use overlap?", "It helps preserve context when important information crosses chunk boundaries."),
            ("What is a good QA test for chunking?", "Ask a question whose answer depends on a rule plus its exception or condition."),
        ],
        "exercise": "Why should 'returns allowed within 30 days' and 'only if unopened' stay together?",
        "exercise_answer": "Because the condition changes the meaning. Separating them can cause an incomplete or misleading answer.",
    },
    {
        "id": "04",
        "title": "Embeddings",
        "goal": "Understand embeddings as a way to represent meaning so semantically similar text can be found.",
        "why": "Users rarely ask questions using the exact wording from a document. Embeddings help retrieval match meaning rather than only exact keywords.",
        "concepts": [
            ("Embedding", "A numeric representation of the meaning of text."),
            ("Semantic similarity", "Two differently worded sentences can still be close in meaning."),
            ("Vector", "The list of numbers used to represent the text in embedding space."),
            ("Similarity", "A score used to estimate which chunks are closest in meaning to the question."),
        ],
        "diagram": ["💬 Question", "🔢 Query vector", "↔️ Compare meaning", "🔢 Chunk vectors", "🎯 Closest chunks"],
        "example": {
            "source": "Users can recover account access using their registered email.",
            "question": "How do I reset my password?",
            "retrieved": "Users can recover account access using their registered email.",
            "answer": "Use your registered email to recover access.",
        },
        "qa": ["Ask the same intent using different wording.", "Test synonyms and paraphrases.", "Check whether semantically unrelated text is incorrectly ranked highly."],
        "questions": [
            ("Are embeddings the final answer?", "No. They help search for relevant content; the LLM still generates the answer."),
            ("Why are embeddings useful compared with exact keyword matching?", "They can match similar meaning even when the words are different."),
            ("What should QA test?", "Paraphrases, synonyms, ambiguous wording, and similar-but-wrong concepts."),
        ],
        "exercise": "Which is closest to 'How long is the reset link valid?' — A) Link expires after 30 minutes, B) Change profile photo, C) Support opens at 9 AM.",
        "exercise_answer": "A) Link expires after 30 minutes because it has the closest meaning to the question.",
    },
    {
        "id": "05",
        "title": "Vector Search & Retrieval",
        "goal": "Understand similarity search, Top-K retrieval, relevance, and retrieval failures.",
        "why": "The LLM can only ground its answer in evidence that reaches it. Good RAG QA therefore inspects what was retrieved before judging the response.",
        "concepts": [
            ("Vector search", "Searches for chunks whose embeddings are closest to the question embedding."),
            ("Top-K", "The number of highest-ranked chunks returned to the LLM."),
            ("Relevance", "How useful a retrieved chunk is for answering the actual question."),
            ("Retrieval failure", "The correct evidence exists but is not selected, or irrelevant evidence is selected instead."),
        ],
        "diagram": ["❓ Query", "🔢 Embed query", "📊 Rank chunks", "🥇 Top 1", "🥈 Top 2", "🧠 Context to LLM"],
        "example": {
            "source": "Chunk A: Reset link expires after 30 minutes. | Chunk B: Office opens at 9 AM. | Chunk C: Update profile photo in Settings.",
            "question": "When does my password-reset link expire?",
            "retrieved": "Chunk A: Reset link expires after 30 minutes.",
            "answer": "It expires after 30 minutes.",
        },
        "qa": ["Label retrieved chunks Relevant / Partially Relevant / Irrelevant.", "Test whether the correct evidence appears in Top-K.", "Check whether higher-ranked evidence is actually better than lower-ranked evidence."],
        "questions": [
            ("What does Top-K mean?", "How many top-ranked chunks the retrieval system returns."),
            ("What should QA inspect first when an answer is wrong?", "The retrieved evidence, to see whether the model received the correct context."),
            ("Can retrieval fail even if the correct answer exists in the PDF?", "Yes. The correct chunk may not rank highly enough to be returned."),
        ],
        "exercise": "If Top-K=2 and the correct chunk ranks 4th, what happens?",
        "exercise_answer": "The correct chunk is not passed to the LLM, so the answer may be wrong or unsupported even though the document contains the answer.",
    },
    {
        "id": "06",
        "title": "Grounding & Hallucination",
        "goal": "Learn to distinguish grounded, partially grounded, unsupported, and hallucinated answers.",
        "why": "A fluent answer is not automatically a correct answer. AI QA must compare the response against evidence rather than judging confidence or writing quality.",
        "concepts": [
            ("Grounded", "Every important claim in the answer is supported by the provided evidence."),
            ("Partially grounded", "Some claims are supported, but an important detail is missing or unsupported."),
            ("Hallucination", "The model invents a fact that is not supported by the source evidence."),
            ("Out-of-scope", "The document does not contain the requested information, so the safe response should acknowledge that."),
        ],
        "diagram": ["📚 Evidence", "⚖️ Compare claims", "✅ Supported", "⚠️ Partial", "❌ Unsupported / Hallucinated"],
        "example": {
            "source": "Returns are accepted within 30 days.",
            "question": "How long do refunds take to reach my bank?",
            "retrieved": "Returns are accepted within 30 days.",
            "answer": "Refunds take 10 business days.",
        },
        "qa": ["Trace every important claim back to evidence.", "Test out-of-scope questions.", "Do not accept plausible-sounding details without support."],
        "questions": [
            ("Is a confident answer necessarily correct?", "No. Confidence and fluency do not prove grounding."),
            ("What should happen when the source has no answer?", "The system should clearly say it does not know based on the available source rather than inventing information."),
            ("What is partially grounded?", "An answer where some content is supported but one or more important claims are missing support."),
            ("How does QA prove hallucination?", "Show the answer claim and demonstrate that the retrieved/source evidence does not support it."),
        ],
        "exercise": "Evidence only says 'returns within 30 days'. The bot says 'refunds arrive in 10 business days'. Classify the answer.",
        "exercise_answer": "Hallucinated / unsupported because the refund-processing time is not present in the evidence.",
    },
    {
        "id": "07",
        "title": "RAG Testing + Final AI QA Project",
        "goal": "Turn RAG knowledge into a professional QA test strategy and execute it in DocPilotAI.",
        "why": "The final skill is not memorizing RAG terminology. It is being able to design tests, investigate evidence, classify failures, and document defects like an AI QA engineer.",
        "concepts": [
            ("Happy path", "A clear in-scope question with an answer present in the source."),
            ("Negative / out-of-scope", "Question intentionally not answered by the source."),
            ("Retrieval test", "Checks whether correct evidence is selected."),
            ("Grounding test", "Checks whether response claims are supported by evidence."),
            ("Robustness test", "Uses paraphrases, edge cases, ambiguous wording, or adversarial prompts."),
            ("Defect", "A reproducible mismatch between expected and actual AI behavior."),
        ],
        "diagram": ["📄 Upload PDF", "❓ Ask questions", "🔎 Inspect evidence", "🧪 Test cases", "🐞 Defects", "📊 QA score"],
        "example": {
            "source": "Use any text-based training PDF.",
            "question": "Create a balanced set of happy-path, negative, retrieval, grounding, and robustness questions.",
            "retrieved": "Inspect the actual evidence returned for each question.",
            "answer": "Record expected vs actual, PASS/FAIL, notes, and defects for failed behavior.",
        },
        "qa": ["Design before executing.", "Record expected evidence as well as expected answer.", "Separate application defect, retrieval defect, and test-data/problem-definition issue."],
        "questions": [
            ("What should every AI QA test case contain?", "Scenario, prompt/input, expected behavior, actual behavior, PASS/FAIL, and useful evidence/notes."),
            ("Why include negative questions?", "To prove the system refuses or safely handles information that is not supported by the source."),
            ("Why inspect evidence for failed tests?", "It helps identify whether the root cause is retrieval or answer generation."),
            ("What makes a good AI bug report?", "Clear title, reproducible steps, exact prompt, expected behavior, actual behavior, evidence, severity, and linkage to a failed test."),
        ],
        "exercise": "Design five starter tests: happy path, out-of-scope, retrieval, grounding, and paraphrase/robustness.",
        "exercise_answer": "Create one test in each category and include prompt, expected answer/behavior, expected evidence, actual result, PASS/FAIL, and notes.",
    },
]

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 5% 0%,rgba(99,102,241,.12),transparent 28%),radial-gradient(circle at 95% 5%,rgba(14,165,233,.10),transparent 24%),#f8fafc;}
.block-container{max-width:1250px;padding-top:1.1rem;padding-bottom:3rem}
.hero{background:linear-gradient(135deg,#0f172a,#172554 56%,#312e81);border-radius:24px;padding:27px 30px;color:white;box-shadow:0 18px 45px rgba(15,23,42,.16);margin-bottom:16px}
.hero h1{margin:0;font-size:32px}.hero p{color:#dbeafe;margin:7px 0 0}.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.chip{padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.13);font-size:12px;font-weight:700}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:17px;padding:17px 18px;box-shadow:0 5px 18px rgba(15,23,42,.04);margin:9px 0 14px}.kicker{font-size:12px;font-weight:850;color:#4f46e5;text-transform:uppercase;letter-spacing:.08em}.card-title{font-size:21px;font-weight:850;color:#0f172a;margin:3px 0 8px}.muted{color:#64748b}
.diagram{display:flex;align-items:stretch;gap:7px;flex-wrap:wrap;margin:12px 0 18px}.node{flex:1;min-width:120px;background:linear-gradient(145deg,#0f172a,#1e293b);border:1px solid #334155;color:#e0f2fe;border-radius:14px;padding:15px 10px;text-align:center;font-weight:800;box-shadow:0 7px 18px rgba(15,23,42,.10)}.arrow{display:flex;align-items:center;color:#6366f1;font-size:24px;font-weight:900}
.example{background:#eef2ff;border:1px solid #c7d2fe;border-radius:16px;padding:16px}.qa{background:#ecfeff;border-left:4px solid #06b6d4;border-radius:13px;padding:14px 16px}.path{background:#0f172a;color:#dbeafe;border-radius:14px;padding:13px 16px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap}
div[data-testid="stExpander"]{border-radius:14px!important;border:1px solid #e2e8f0!important;background:white}.stButton>button{border-radius:12px;font-weight:750}.stTabs [data-baseweb="tab-list"]{gap:7px;background:#eaf0f7;padding:6px;border-radius:14px}.stTabs [data-baseweb="tab"]{border-radius:10px;height:42px;font-weight:750}.stTabs [aria-selected="true"]{background:white!important}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🧠 RAG for QA Students</h1>
  <p>Learn the system visually → understand what can fail → practice QA thinking → finish with the DocPilotAI testing project.</p>
  <div class="chips">
    <span class="chip">7 guided modules</span><span class="chip">Visual diagrams</span><span class="chip">Worked examples</span><span class="chip">Multiple Q&A</span><span class="chip">Final AI QA project</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Course journey")
st.markdown('<div class="path">01 What is RAG → 02 Architecture → 03 Chunking → 04 Embeddings → 05 Retrieval → 06 Grounding/Hallucination → 07 AI QA Project</div>', unsafe_allow_html=True)

labels = [f"{m['id']} — {m['title']}" for m in MODULES]
selected = st.selectbox("Choose learning module", labels, index=0)
module = MODULES[labels.index(selected)]

st.markdown(f"<div class='card'><div class='kicker'>Module {module['id']}</div><div class='card-title'>{module['title']}</div><div class='muted'>{module['goal']}</div></div>", unsafe_allow_html=True)

learn_tab, example_tab, questions_tab, exercise_tab = st.tabs(["📘 Learn", "👀 Visual Example", "❓ Questions & Answers", "🧪 Exercise"])

with learn_tab:
    st.markdown("#### Why this matters")
    st.write(module["why"])

    st.markdown("#### Visual flow")
    diagram_html = '<div class="diagram">'
    for i, node in enumerate(module["diagram"]):
        diagram_html += f'<div class="node">{node}</div>'
        if i < len(module["diagram"]) - 1:
            diagram_html += '<div class="arrow">→</div>'
    diagram_html += '</div>'
    st.markdown(diagram_html, unsafe_allow_html=True)

    st.markdown("#### Key concepts in simple language")
    cols = st.columns(2)
    for i, (name, explanation) in enumerate(module["concepts"]):
        with cols[i % 2]:
            st.markdown(f"<div class='card'><b>{name}</b><br><span class='muted'>{explanation}</span></div>", unsafe_allow_html=True)

    st.markdown("#### What should QA test?")
    st.markdown("<div class='qa'>" + "<br>".join(f"✅ {x}" for x in module["qa"]) + "</div>", unsafe_allow_html=True)

with example_tab:
    ex = module["example"]
    st.markdown("#### Follow one example through the concept")
    st.markdown(f"""
<div class="example">
<b>📚 Source / context</b><br>{ex['source']}<br><br>
<b>❓ User question</b><br>{ex['question']}<br><br>
<b>🔎 Retrieved evidence</b><br>{ex['retrieved']}<br><br>
<b>💬 Agent answer</b><br>{ex['answer']}
</div>
""", unsafe_allow_html=True)
    st.markdown("#### Instructor discussion")
    st.write("Ask students: **Is the evidence relevant? Is the answer supported? What could go wrong at this stage?**")

with questions_tab:
    st.markdown("#### Check your understanding")
    st.caption("Try answering each question before opening the answer.")
    for i, (q, a) in enumerate(module["questions"], 1):
        with st.expander(f"Q{i}. {q}"):
            st.success(a)

with exercise_tab:
    st.markdown("#### Small exercise")
    st.info(module["exercise"])
    answer_key = f"exercise_answer_{module['id']}"
    if st.button("Show answer", key=answer_key):
        st.success(module["exercise_answer"])
    st.markdown("#### Explain it in your own words")
    st.text_area("Student notes", placeholder="Write 2–4 sentences explaining what you learned and why a QA tester should care.", key=f"notes_{module['id']}")

st.divider()
if module["id"] == "07":
    st.markdown("### 🚀 Final Project — Test the DocPilotAI Agent")
    st.write("You have learned enough RAG to test the system like an AI QA engineer. In the project you will upload a PDF, ask questions, inspect evidence, create test cases, log defects, review your QA score, and download your final report.")
    if st.button("🚀 Start AI QA Project", type="primary", use_container_width=True):
        st.session_state["open_ai_qa_project"] = True
        st.switch_page("app.py")
else:
    next_index = int(module["id"])
    st.caption(f"Complete the Q&A and exercise, then continue to Module {next_index + 1:02d}.")
