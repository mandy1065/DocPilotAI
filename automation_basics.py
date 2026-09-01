import streamlit as st

LESSONS = [
    {
        "title": "1 · What is test automation?",
        "plain": "Manual testing means a person performs the same steps and checks the result. Automation means we write code that performs those checks repeatedly for us. For AI QA, the automated test sends a question to the RAG pipeline, captures the answer and retrieved evidence, then uses DeepEval metrics to judge quality.",
        "flow": ["Test data", "Python test", "Call RAG", "Capture answer + context", "DeepEval metric", "PASS / FAIL"],
        "code": """def test_example():\n    result = pipeline.ask(\"How long is the reset link valid?\")\n    assert result.answer\n""",
        "explain": [
            "def test_example(): creates one automated test function.",
            "pipeline.ask(...) performs the action we want to test.",
            "result stores the actual runtime output.",
            "assert checks whether a condition is acceptable. If it is false, pytest fails the test.",
        ],
        "exercise": "In your own words, explain the difference between manually asking the chatbot a question and automating that same check.",
        "solution": "Manual: a tester opens the app, asks the question, reads the response, and decides whether it passed. Automated: Python sends the question, captures the response, applies checks/metrics, and produces PASS or FAIL without repeating the steps manually.",
    },
    {
        "title": "2 · Project files and folders",
        "plain": "Automation projects are easier to maintain when each file has one job. We keep application/RAG logic separate from test code and keep reusable test data outside the test function.",
        "flow": ["requirements.txt", "rag_pipeline.py", "tests/", "golden_cases.json", "test_deepeval.py", "workflow YAML"],
        "code": """my-ai-tests/\n├── requirements.txt\n├── rag_pipeline.py\n├── tests/\n│   ├── data/\n│   │   └── golden_cases.json\n│   └── test_deepeval.py\n└── .github/workflows/deepeval.yml\n""",
        "explain": [
            "requirements.txt lists packages that must be installed.",
            "rag_pipeline.py contains reusable RAG functions used by tests.",
            "tests/ contains automated test code.",
            "golden_cases.json stores questions and expected answers separately from Python.",
            "deepeval.yml tells GitHub Actions how to run the same tests automatically.",
        ],
        "exercise": "Which file should contain the RAG logic, and which file should contain DeepEval test cases?",
        "solution": "RAG logic belongs in rag_pipeline.py. Automated DeepEval tests belong in tests/test_deepeval.py. Keeping them separate makes the system easier to reuse and debug.",
    },
    {
        "title": "3 · Pytest from zero",
        "plain": "Pytest is the test runner. It finds Python functions whose names start with test_, runs them, and reports PASS or FAIL. You do not need a main() function for pytest tests.",
        "flow": ["pytest command", "Discover test_ files", "Run test_ functions", "Evaluate assertions", "Report result"],
        "code": """# tests/test_basic.py\n\ndef test_math_example():\n    actual = 2 + 2\n    expected = 4\n    assert actual == expected\n\n# terminal\n# pytest tests/test_basic.py -v\n""",
        "explain": [
            "The filename starts with test_, so pytest can discover it.",
            "The function also starts with test_.",
            "actual stores what the system produced.",
            "expected stores what we wanted.",
            "assert actual == expected is the quality check.",
            "-v means verbose, so pytest shows each test name and result.",
        ],
        "exercise": "Write the name of a valid pytest test function for checking password reset behavior.",
        "solution": "Example: def test_password_reset_policy():. The important beginner rule is that the function name should start with test_.",
    },
    {
        "title": "4 · Imports, functions and reusable code",
        "plain": "Automation should avoid copying the same code into every test. We put reusable behavior in functions/classes and import it into the test file.",
        "flow": ["rag_pipeline.py", "RAGPipeline class", "import", "test file", "reuse in many tests"],
        "code": """# rag_pipeline.py\nclass RAGPipeline:\n    def ask(self, question):\n        return \"runtime result\"\n\n# tests/test_deepeval.py\nfrom rag_pipeline import RAGPipeline\n\npipeline = RAGPipeline()\n""",
        "explain": [
            "class RAGPipeline groups related RAG behavior together.",
            "def ask(...) creates a reusable method.",
            "from rag_pipeline import RAGPipeline brings that class into the test file.",
            "pipeline = RAGPipeline() creates an object the tests can use.",
        ],
        "exercise": "Why is importing RAGPipeline better than duplicating retrieval/generation code inside every test?",
        "solution": "Because there is one reusable source of truth. If retrieval logic changes, the tests keep calling the same pipeline instead of maintaining many copied versions.",
    },
    {
        "title": "5 · Fixtures: prepare once, reuse many times",
        "plain": "A pytest fixture prepares something a test needs. In our project the fixture builds the RAG pipeline once, and each automated test can receive it as a function parameter.",
        "flow": ["Fixture", "Load source", "Build pipeline", "Inject into tests", "Reuse"],
        "code": """import pytest\n\n@pytest.fixture(scope=\"session\")\ndef pipeline():\n    text = \"Password reset links expire after 30 minutes.\"\n    return RAGPipeline.from_text(text)\n\ndef test_reset_link(pipeline):\n    result = pipeline.ask(\"How long is the reset link valid?\")\n    assert result.answer\n""",
        "explain": [
            "@pytest.fixture tells pytest this function prepares reusable test setup.",
            "scope='session' means pytest can create it once for the whole test run.",
            "return RAGPipeline... provides the object to tests.",
            "Adding pipeline as a test parameter asks pytest to inject that fixture automatically.",
        ],
        "exercise": "What problem does a fixture solve in this RAG test suite?",
        "solution": "It prevents every test from repeating setup such as loading the source document and building the retrieval index. The test can focus on behavior instead of setup code.",
    },
    {
        "title": "6 · Golden data and parametrization",
        "plain": "A real automation suite should run more than one question. Golden data stores stable input + expected-output pairs, while pytest parametrization runs the same test logic against every case.",
        "flow": ["Golden JSON", "Load cases", "parametrize", "Case 1", "Case 2", "Case 3"],
        "code": """GOLDENS = [\n    {\"input\": \"How long is the reset link valid?\", \"expected_output\": \"30 minutes\"},\n    {\"input\": \"Can I return an opened item?\", \"expected_output\": \"No\"},\n]\n\n@pytest.mark.parametrize(\"golden\", GOLDENS)\ndef test_rag_quality(golden, pipeline):\n    result = pipeline.ask(golden[\"input\"])\n    # DeepEval checks go here\n""",
        "explain": [
            "GOLDENS contains reusable test data rather than test logic.",
            "@pytest.mark.parametrize repeats one test for every golden case.",
            "golden['input'] is the current question.",
            "golden['expected_output'] is the known ideal/reference answer.",
            "When you add a new JSON case, the same automation can test it without copying another function.",
        ],
        "exercise": "Why is a golden dataset better than creating 20 almost-identical Python test functions?",
        "solution": "It separates data from logic. One reusable test function can execute many scenarios, making the suite easier to expand and maintain.",
    },
    {
        "title": "7 · From normal assertion to DeepEval assertion",
        "plain": "Traditional assertions work well for exact values, but natural-language AI answers can be correct with different wording. DeepEval lets the assertion evaluate quality dimensions instead of exact strings.",
        "flow": ["RAG result", "LLMTestCase", "Metric", "Threshold", "assert_test", "PASS / FAIL"],
        "code": """from deepeval import assert_test\nfrom deepeval.metrics import FaithfulnessMetric\nfrom deepeval.test_case import LLMTestCase\n\ncase = LLMTestCase(\n    input=golden[\"input\"],\n    actual_output=result.answer,\n    expected_output=golden[\"expected_output\"],\n    retrieval_context=result.retrieval_context,\n)\n\nmetric = FaithfulnessMetric(threshold=0.8)\nassert_test(case, [metric])\n""",
        "explain": [
            "LLMTestCase packages the AI test inputs and outputs in DeepEval's format.",
            "actual_output is produced at runtime by the RAG system.",
            "retrieval_context is the evidence the retriever actually returned.",
            "threshold=0.8 defines the minimum acceptable metric score.",
            "assert_test makes DeepEval part of pytest: below threshold means the automated test fails.",
        ],
        "exercise": "Why should actual_output come from pipeline.ask() instead of being hard-coded in the test?",
        "solution": "Because automation should evaluate the current system under test. Hard-coding actual_output would only evaluate a sample sentence and would not detect regressions in the real RAG pipeline.",
    },
    {
        "title": "8 · Environment variables and secrets",
        "plain": "Automation often needs API keys. A secret must never be typed into the Python test file or committed to GitHub. The program reads it from an environment variable instead.",
        "flow": ["GitHub Secret", "Environment variable", "Python reads key", "OpenAI call", "Secret stays hidden"],
        "code": """# Python\nimport os\napi_key = os.environ[\"OPENAI_API_KEY\"]\n\n# GitHub Actions\nenv:\n  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}\n""",
        "explain": [
            "GitHub stores the secret value outside source code.",
            "The workflow exposes it only to the test process as an environment variable.",
            "Python reads the variable with os.environ.",
            "The real key should never appear inside .py, .json, or .yml source files.",
        ],
        "exercise": "Should a student put sk-... directly in test_deepeval.py? Why?",
        "solution": "No. API keys are credentials. Store them in Streamlit Secrets for the app and GitHub Actions Secrets for CI, then read them through environment variables.",
    },
    {
        "title": "9 · CI/CD: automate the automation",
        "plain": "Running pytest on your laptop is test automation. CI/CD goes one step further: GitHub automatically runs those tests whenever important code changes are pushed or submitted in a pull request.",
        "flow": ["Developer changes code", "git push / PR", "GitHub Actions", "Install packages", "Run pytest + DeepEval", "Green / Red gate"],
        "code": """name: DeepEval Quality Gate\n\non:\n  push:\n  pull_request:\n\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n      - run: pip install -r requirements.txt\n      - run: pytest tests/test_deepeval.py -v\n""",
        "explain": [
            "on: defines when automation should start.",
            "jobs: groups work GitHub Actions will perform.",
            "checkout downloads the repository code into the runner.",
            "setup-python prepares Python.",
            "pip install installs project dependencies.",
            "pytest runs the same suite the student used locally.",
            "A failing test makes the CI job red, creating a quality gate.",
        ],
        "exercise": "Explain what should happen when a developer changes chunking and Contextual Recall falls below threshold.",
        "solution": "The push/PR triggers GitHub Actions, pytest runs the golden RAG cases, DeepEval detects low Contextual Recall, the test fails, and the GitHub job becomes red so the team can investigate the retrieval regression before release.",
    },
]

st.markdown("""
<style>
.auto-hero{background:linear-gradient(135deg,#111827,#1e3a8a,#0f766e);color:white;padding:25px 28px;border-radius:23px;margin:8px 0 17px}.auto-hero h1{margin:0;font-size:30px}.auto-hero p{color:#dbeafe;line-height:1.6;max-width:900px}.auto-flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:8px;margin:12px 0 20px}.auto-node{background:#0f172a;color:white;border-radius:14px;padding:13px;text-align:center;font-size:12px;font-weight:750}.auto-card{background:white;border:1px solid #e2e8f0;border-radius:17px;padding:18px 20px;margin:12px 0}.auto-explain{background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:14px 17px}.auto-explain li{margin:7px 0;color:#334155;line-height:1.5}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="auto-hero">
<h1>🤖 Automation Basics — Start From Zero</h1>
<p>Before DeepEval, learn how a normal Python automation project works. You will learn what pytest does, how test files are structured, how reusable setup works, how golden data drives many test cases, what an assertion is, how secrets are handled, and how GitHub Actions runs the same suite automatically.</p>
</div>
""", unsafe_allow_html=True)

st.info("Beginner goal: by the end of these lessons, you should be able to explain every important line in the DeepEval project you build next — not just copy it.")

lesson_names = [lesson["title"] for lesson in LESSONS]
selected = st.selectbox("Choose automation lesson", lesson_names, key="automation_basics_lesson")
lesson = LESSONS[lesson_names.index(selected)]

st.markdown(f"<div class='auto-card'><h2 style='margin-top:0'>{lesson['title']}</h2><p style='line-height:1.7;color:#334155'>{lesson['plain']}</p></div>", unsafe_allow_html=True)

st.markdown("### See the automation flow")
st.markdown('<div class="auto-flow">' + ''.join(f'<div class="auto-node">{item}</div>' for item in lesson['flow']) + '</div>', unsafe_allow_html=True)

learn_tab, code_tab, exercise_tab = st.tabs(["📘 Understand", "💻 Code + line explanation", "🧪 Beginner exercise"])

with learn_tab:
    st.write(lesson["plain"])
    st.markdown("**The key question to ask:** What is being prepared, what action is being performed, and what check decides PASS or FAIL?")

with code_tab:
    st.code(lesson["code"], language="yaml" if "CI/CD" in lesson["title"] else "python")
    st.markdown("#### What each important line means")
    st.markdown('<div class="auto-explain"><ul>' + ''.join(f'<li>{item}</li>' for item in lesson['explain']) + '</ul></div>', unsafe_allow_html=True)

with exercise_tab:
    st.info(lesson["exercise"])
    st.text_area("Your answer", key=f"auto_answer_{lesson_names.index(selected)}", height=110, placeholder="Explain it in your own words...")
    h1, h2, h3 = st.tabs(["Hint 1", "Hint 2", "Hint 3 · Complete answer"])
    with h1:
        st.write("Identify the setup, action, and expected check in the example.")
    with h2:
        st.write("Use the code and line explanations above. Focus on why the automation is reusable.")
    with h3:
        st.success(lesson["solution"])

st.divider()
st.markdown("### When you are ready")
st.write("Continue to **Learn DeepEval Metrics** to understand AI-specific quality checks, then open **Build DeepEval Project** and create the complete automation suite yourself.")
