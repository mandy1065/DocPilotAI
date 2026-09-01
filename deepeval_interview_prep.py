import streamlit as st

QUESTIONS = [
    {
        "category": "Automation Basics",
        "level": "Beginner",
        "question": "What is test automation?",
        "answer": "Test automation means writing code that executes test steps, checks results, and reports PASS or FAIL automatically instead of repeating the same checks manually every time.",
        "interview_tip": "Connect it to repeatability: automation is most useful for regression tests that need to run again after code, prompt, model, or retrieval changes.",
    },
    {
        "category": "Automation Basics",
        "level": "Beginner",
        "question": "Why do we use pytest in an AI QA framework?",
        "answer": "pytest is the test runner. It discovers test functions, executes them, shows which cases passed or failed, supports fixtures and parameterized test data, and can run the same tests locally or in CI/CD.",
        "interview_tip": "DeepEval supplies AI-quality assertions; pytest supplies the overall automation structure and runner.",
    },
    {
        "category": "Automation Basics",
        "level": "Beginner",
        "question": "What is a fixture in pytest?",
        "answer": "A fixture prepares reusable setup data or objects for tests. In our framework a fixture can create the API client once or upload the source document once and return its document_id to multiple test cases.",
        "interview_tip": "Mention that fixtures reduce duplicated setup code.",
    },
    {
        "category": "Automation Basics",
        "level": "Beginner",
        "question": "What is parameterization in pytest?",
        "answer": "Parameterization lets one test function run many test-data rows. Instead of writing five nearly identical tests, we can store five golden questions and run the same RAG-quality test for all of them.",
        "interview_tip": "A good phrase is: one test flow, many datasets.",
    },
    {
        "category": "API Automation",
        "level": "Beginner",
        "question": "Why are we testing the RAG agent through an API instead of the Streamlit UI?",
        "answer": "The API gives a stable, fast way to call the system and capture machine-readable values such as answer and retrieval_context. UI tests are still useful for user-interface behavior, but API tests are usually better for large AI regression suites.",
        "interview_tip": "Explain that API and UI testing solve different problems; they complement each other.",
    },
    {
        "category": "API Automation",
        "level": "Beginner",
        "question": "What does the API client do in our framework?",
        "answer": "The API client hides HTTP details behind simple Python methods. A test can call client.ask(document_id, question) instead of rewriting request URLs, headers, payloads, and error handling in every test.",
        "interview_tip": "This is an example of reusable framework design.",
    },
    {
        "category": "API Automation",
        "level": "Intermediate",
        "question": "What should a RAG answer API return so DeepEval can evaluate it properly?",
        "answer": "At minimum it should return the generated answer and the retrieval_context used to produce that answer. The test already knows the input question, and reference-based metrics may also use an expected_output from golden test data.",
        "interview_tip": "Say retrieval_context is essential for diagnosing retriever versus generator problems.",
    },
    {
        "category": "RAG Testing",
        "level": "Beginner",
        "question": "What are the two major parts we evaluate in a RAG system?",
        "answer": "The retriever and the generator. The retriever must find useful source chunks, and the generator must use those chunks to produce a relevant, grounded answer.",
        "interview_tip": "This distinction is central to RAG QA interviews.",
    },
    {
        "category": "RAG Testing",
        "level": "Intermediate",
        "question": "Why is one end-to-end PASS/FAIL score not enough for RAG testing?",
        "answer": "Because a bad final answer can come from different root causes. Retrieval may return the wrong evidence, or retrieval may be correct and the generator may invent or change facts. Separate metrics help locate the failing stage.",
        "interview_tip": "Use the words root-cause analysis.",
    },
    {
        "category": "DeepEval Metrics",
        "level": "Beginner",
        "question": "What does Answer Relevancy measure?",
        "answer": "It measures whether the generated answer actually addresses the user's question. It can catch responses that are related to the topic but do not answer the user's intent.",
        "interview_tip": "It does not prove that the answer is factually grounded.",
    },
    {
        "category": "DeepEval Metrics",
        "level": "Beginner",
        "question": "What does Faithfulness measure?",
        "answer": "Faithfulness checks whether claims in the generated answer are supported by the retrieved context. It is useful for detecting unsupported or contradictory facts in a RAG response.",
        "interview_tip": "If retrieval is correct but Faithfulness fails, investigate generation or grounding first.",
    },
    {
        "category": "DeepEval Metrics",
        "level": "Beginner",
        "question": "What does Contextual Relevancy measure?",
        "answer": "It measures whether the retrieved context is useful for the user's question. A low score often means the retriever returned too many unrelated or noisy chunks.",
        "interview_tip": "This is a retriever-quality metric.",
    },
    {
        "category": "DeepEval Metrics",
        "level": "Intermediate",
        "question": "What does Contextual Precision measure?",
        "answer": "Contextual Precision focuses on ranking quality. It checks whether useful chunks appear earlier than irrelevant chunks in the retrieval results.",
        "interview_tip": "Use it when evaluating similarity ranking, reranking, or Top-K ordering.",
    },
    {
        "category": "DeepEval Metrics",
        "level": "Intermediate",
        "question": "What does Contextual Recall measure?",
        "answer": "Contextual Recall checks whether retrieval captured all the information required to support the expected answer. Retrieval can be relevant but still incomplete, especially for questions with multiple rules or exceptions.",
        "interview_tip": "Relevancy is about usefulness; recall is about completeness.",
    },
    {
        "category": "DeepEval Metrics",
        "level": "Intermediate",
        "question": "What fields are commonly passed into an LLMTestCase for RAG evaluation?",
        "answer": "input is the user question, actual_output is the runtime model answer, expected_output is the known reference answer when required, and retrieval_context is the list of chunks returned by the retriever.",
        "interview_tip": "Be able to map these fields to your actual API response and golden dataset.",
    },
    {
        "category": "DeepEval Metrics",
        "level": "Intermediate",
        "question": "Can Faithfulness pass even when retrieval is wrong?",
        "answer": "Yes. If the generator faithfully repeats incorrect or irrelevant retrieved context, Faithfulness can still be high because it evaluates the answer against the supplied context. That is why retriever metrics must also be included.",
        "interview_tip": "This is a strong scenario answer because it shows you understand metric limitations.",
    },
    {
        "category": "Golden Data",
        "level": "Beginner",
        "question": "What is a golden dataset?",
        "answer": "A golden dataset is a controlled collection of important test questions with known expected answers or expected behavior. The same dataset is reused to detect regressions over time.",
        "interview_tip": "Start with high-risk, business-critical, representative cases rather than thousands of weak cases.",
    },
    {
        "category": "Golden Data",
        "level": "Intermediate",
        "question": "How would you choose test cases for a RAG golden dataset?",
        "answer": "I would include common user questions, critical business rules, policy exceptions, paraphrases, multi-fact questions, previously reported defects, out-of-scope questions, and cases known to challenge retrieval.",
        "interview_tip": "Mention risk-based coverage and defect history.",
    },
    {
        "category": "Thresholds",
        "level": "Intermediate",
        "question": "What is a DeepEval threshold?",
        "answer": "A threshold is the minimum acceptable score for a metric. If the metric score falls below that threshold, the automated quality check fails.",
        "interview_tip": "Thresholds should be calibrated using real baseline results; they should not be arbitrary numbers.",
    },
    {
        "category": "Thresholds",
        "level": "Advanced",
        "question": "Would you use the same threshold for every metric and every use case?",
        "answer": "Not necessarily. Different quality dimensions and business risks may require different thresholds. For example, a high-risk policy assistant may require stronger Faithfulness than a low-risk brainstorming tool. I would baseline the system, review failures, and tune thresholds based on risk and observed behavior.",
        "interview_tip": "Avoid saying '0.7 is always correct'. Explain how you calibrate.",
    },
    {
        "category": "Debugging",
        "level": "Intermediate",
        "question": "Answer Relevancy fails but Faithfulness passes. What could that mean?",
        "answer": "The model may be faithfully using the retrieved evidence but still answering the wrong intent or giving information that does not directly answer the question. I would inspect the question, answer, and retrieved chunks together.",
        "interview_tip": "Do not automatically blame retrieval; first inspect whether the answer addresses the user's intent.",
    },
    {
        "category": "Debugging",
        "level": "Intermediate",
        "question": "Faithfulness fails while the retrieval metrics pass. Where would you investigate first?",
        "answer": "I would investigate the generator, grounding prompt, and answer-generation logic. The retriever appears to have supplied good evidence, but the generated answer is not staying supported by that evidence.",
        "interview_tip": "This is a classic retriever-versus-generator diagnosis question.",
    },
    {
        "category": "Debugging",
        "level": "Intermediate",
        "question": "Contextual Relevancy fails. What would you investigate?",
        "answer": "I would inspect the returned chunks, Top-K setting, chunk size, retrieval scoring, query wording, and possible reranking. The failure indicates too much retrieved content is unrelated to the question.",
        "interview_tip": "Mention that increasing Top-K can improve recall but also increase noise.",
    },
    {
        "category": "Debugging",
        "level": "Advanced",
        "question": "Contextual Recall fails but Contextual Relevancy passes. What does that tell you?",
        "answer": "The returned context is relevant, but it is incomplete. The retriever found useful evidence but missed one or more facts needed for the complete expected answer. I would inspect missing chunks, Top-K, chunk boundaries, and whether the required facts are split across sections.",
        "interview_tip": "This is a good example of why multiple retrieval metrics are needed.",
    },
    {
        "category": "CI/CD",
        "level": "Beginner",
        "question": "Why run DeepEval tests in CI/CD?",
        "answer": "CI/CD automatically reruns the AI quality suite after important changes. This helps catch regressions caused by changes to prompts, models, retrieval logic, chunking, source documents, or application code before they reach users.",
        "interview_tip": "Describe CI as repeatable quality evidence, not only an automation convenience.",
    },
    {
        "category": "CI/CD",
        "level": "Beginner",
        "question": "Why do we store OPENAI_API_KEY as a GitHub secret?",
        "answer": "API keys are credentials and should not be committed to source code. GitHub Actions secrets let the workflow access the key at runtime while keeping the value hidden from the repository.",
        "interview_tip": "Never hard-code secrets in test files or YAML.",
    },
    {
        "category": "CI/CD",
        "level": "Intermediate",
        "question": "What happens in our AI QA CI pipeline?",
        "answer": "The workflow checks out the repository, sets up Python, installs dependencies, starts the DocPilot API, supplies required secrets, runs pytest, calls the RAG API for golden cases, evaluates the runtime responses with DeepEval, and fails the job when quality thresholds are missed.",
        "interview_tip": "Explain the pipeline as a sequence from environment setup to quality gate.",
    },
    {
        "category": "Framework Design",
        "level": "Intermediate",
        "question": "What makes this an automation framework instead of just one test script?",
        "answer": "The responsibilities are separated and reusable: the API client handles HTTP calls, golden JSON holds test data, pytest controls execution, DeepEval metrics handle AI-quality assertions, fixtures handle setup, and GitHub Actions runs the same framework in CI.",
        "interview_tip": "Use words such as reusable, maintainable, data-driven, and separation of concerns.",
    },
    {
        "category": "Framework Design",
        "level": "Advanced",
        "question": "How would you scale this framework from five tests to hundreds?",
        "answer": "I would keep test data separate from code, organize datasets by feature or risk, reuse API clients and fixtures, run targeted suites when appropriate, control LLM evaluation cost, track flaky or unstable cases, capture metric scores and reasons, and maintain a smaller critical CI gate plus broader scheduled regression runs.",
        "interview_tip": "Show that scaling AI evaluation involves cost and stability as well as code structure.",
    },
    {
        "category": "Scenario",
        "level": "Advanced",
        "question": "A model upgrade improves Answer Relevancy but lowers Faithfulness. Would you release it?",
        "answer": "I would not decide from one aggregate result. I would inspect which cases lost Faithfulness, especially high-risk ones, compare metric reasons and retrieved evidence, evaluate whether thresholds and test data are appropriate, and assess business risk. Better relevance does not compensate for unsupported facts in a high-risk RAG system.",
        "interview_tip": "Interviewers want risk-based reasoning, not a simple yes/no answer.",
    },
]

st.markdown("## 🎤 AI QA / DeepEval Interview Prep")
st.write(
    "Use these after completing Phase 2. Start with Beginner questions, then practice explaining Intermediate and Advanced scenarios in your own words."
)

categories = ["All"] + sorted({q["category"] for q in QUESTIONS})
levels = ["All", "Beginner", "Intermediate", "Advanced"]

c1, c2 = st.columns(2)
with c1:
    category = st.selectbox("Topic", categories, key="interview_category")
with c2:
    level = st.selectbox("Difficulty", levels, key="interview_level")

filtered = [
    q for q in QUESTIONS
    if (category == "All" or q["category"] == category)
    and (level == "All" or q["level"] == level)
]

st.caption(f"Showing {len(filtered)} interview questions")

for index, item in enumerate(filtered, 1):
    with st.expander(f"Q{index}. [{item['level']}] {item['question']}"):
        st.markdown("**Strong interview answer**")
        st.success(item["answer"])
        st.markdown("**What to emphasize**")
        st.info(item["interview_tip"])

st.divider()
st.markdown("### How to practice")
st.write(
    "First hide the answer and explain the question aloud in 30–60 seconds. Then open the answer, compare it with your explanation, and repeat it using your own words. For scenario questions, always explain what evidence you would inspect before deciding the root cause."
)
