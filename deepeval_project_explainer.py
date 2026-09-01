import streamlit as st


FILE_LESSONS = [
    {
        "file": "requirements.txt",
        "title": "Before coding: understand requirements.txt",
        "what": "requirements.txt is a simple list of Python packages that this project depends on. Think of it as the project's software shopping list.",
        "why": "Python does not automatically include OpenAI, DeepEval, pytest, PDF readers, or scikit-learn. We list them here so a student, teammate, or CI server can install the same tools needed by the project.",
        "without": "Without this file, someone opening your project would have to guess which packages to install. GitHub Actions would also not know which libraries your automated tests need.",
        "command": "pip install -r requirements.txt",
        "command_meaning": "pip = Python's package installer. install = install packages. -r = read package names from a file. requirements.txt = the file to read.",
        "items": [
            ("openai>=1,<3", "OpenAI Python library", "Our RAG pipeline uses it to send the retrieved context and question to an OpenAI model and receive an answer.", ">=1 means version 1 or newer; <3 means do not automatically move to version 3 or above."),
            ("pypdf>=5,<7", "PDF reader", "Our real project can upload a PDF. pypdf extracts readable text from that PDF so the RAG pipeline can chunk and search it.", ">=5,<7 means use a compatible version from the 5.x or 6.x range."),
            ("scikit-learn>=1.5,<2", "Retrieval tools", "We use TF-IDF and cosine similarity from scikit-learn to turn document text into searchable numbers and rank the best chunks.", "Use version 1.5 or newer, but stay below the next major version 2."),
            ("pytest>=8,<9", "Automation test runner", "pytest finds test functions such as test_rag_quality(), executes them, and reports PASS or FAIL.", "Use pytest 8.x so the course does not unexpectedly change when a future major version appears."),
            ("deepeval>=3,<4", "AI evaluation library", "DeepEval provides Answer Relevancy, Faithfulness, Contextual Relevancy, Contextual Precision, and Contextual Recall metrics.", "Use DeepEval 3.x; avoid an automatic major upgrade to 4.x that could contain breaking changes."),
        ],
        "remember": "requirements.txt does NOT contain our test logic. It only tells Python which external libraries must exist before our project can run.",
    },
    {
        "file": "rag_pipeline.py",
        "title": "Before coding: understand rag_pipeline.py",
        "what": "This is the code for the system we want to test. It takes document text, breaks it into chunks, retrieves useful evidence, sends that evidence to the LLM, and returns the answer.",
        "why": "Automation should call the real application logic. If our tests only evaluate hard-coded answers, we are testing examples—not our RAG pipeline.",
        "without": "Without reusable RAG code, pytest has nothing real to call. We would be manually copying answers into tests instead of detecting regressions in retrieval or generation.",
        "command": "result = pipeline.ask(question)",
        "command_meaning": "The automated test sends a question to the RAG pipeline. The returned result gives us the generated answer AND retrieval_context that DeepEval needs.",
        "items": [
            ("chunk_text()", "Chunking", "Splits a long document into smaller searchable pieces.", "QA later checks whether chunk boundaries cause missing context."),
            ("TfidfVectorizer", "Search representation", "Converts text into numeric features so questions and chunks can be compared.", "DocPilotAI uses lightweight TF-IDF for classroom retrieval rather than a neural vector database."),
            ("cosine_similarity", "Ranking", "Scores how similar the user's question is to each document chunk.", "Higher-scoring chunks are returned first."),
            ("retrieve()", "Retriever", "Returns the Top-K chunks that appear most relevant to the question.", "DeepEval retriever metrics evaluate these chunks."),
            ("ask()", "Generator call", "Retrieves evidence and then asks the LLM to answer using that evidence.", "The runtime answer becomes actual_output in DeepEval."),
            ("retrieval_context", "Evidence captured for testing", "Stores the exact chunks the RAG system supplied to the model.", "Faithfulness and retrieval metrics cannot be meaningfully tested without this evidence."),
        ],
        "remember": "The RAG pipeline is the SYSTEM UNDER TEST. DeepEval is the evaluation layer that checks the quality of what this system returns.",
    },
    {
        "file": "tests/data/golden_cases.json",
        "title": "Before coding: understand golden test data",
        "what": "A golden dataset is a small collection of important questions where QA already knows what a good answer should contain.",
        "why": "Automation needs stable test scenarios. Instead of rewriting questions inside Python every time, we keep test data separately and run the same scenarios after every code change.",
        "without": "Without golden cases, we may test random prompts each time and cannot easily tell whether a new RAG version became better or worse on important business rules.",
        "command": "pytest runs the same test once for every golden case",
        "command_meaning": "One Python test function can automatically run many questions by reading them from this JSON file.",
        "items": [
            ("id", "Test-case name", "A short unique label such as reset-link or return-policy.", "It makes failures easy to identify in pytest output."),
            ("input", "User question", "The exact prompt our automated test sends to the RAG system.", "This becomes LLMTestCase.input."),
            ("expected_output", "Known good answer", "The reference answer QA expects based on the source document.", "Contextual Precision and Contextual Recall use this reference to judge retrieval quality."),
        ],
        "remember": "Golden data is not the model's actual answer. expected_output is our QA reference; actual_output is produced later by the running RAG system.",
    },
    {
        "file": "tests/test_deepeval.py",
        "title": "Before coding: understand the pytest + DeepEval test file",
        "what": "This file is the automation test suite. It connects our golden questions to the RAG pipeline, captures runtime results, creates DeepEval test cases, runs metrics, and decides PASS or FAIL.",
        "why": "This is where separate pieces become a real regression test: test data → application call → actual result → metric evaluation → assertion.",
        "without": "Having a RAG pipeline and DeepEval installed is not enough. Nothing automatically runs until we write tests that call them and assert acceptable quality.",
        "command": "pytest tests/test_deepeval.py -v",
        "command_meaning": "pytest = run tests; tests/test_deepeval.py = which test file to run; -v = verbose output so students can see individual test names and results.",
        "items": [
            ("import", "Reuse code", "Imports pytest, DeepEval metrics, LLMTestCase, and our RAGPipeline.", "Imports let one file use classes/functions defined elsewhere."),
            ("@pytest.fixture", "Reusable setup", "Builds the RAG pipeline once and supplies it to tests.", "Fixtures reduce duplicated setup code."),
            ("@pytest.mark.parametrize", "Data-driven testing", "Runs the same test logic for multiple golden cases.", "Three golden cases can become three automated executions without copying the test function."),
            ("LLMTestCase", "Standard evaluation object", "Packages input, actual_output, expected_output, and retrieval_context together.", "Each metric reads the fields it needs from this object."),
            ("metrics = [...]", "Quality checks", "Defines which DeepEval dimensions we want to measure and their thresholds.", "Different metrics help isolate generator vs retriever problems."),
            ("assert_test()", "AI assertion", "Runs the metrics and fails the pytest test when quality is below the configured threshold.", "This turns metric scores into an automated quality gate."),
        ],
        "remember": "A traditional assert may check exact values. DeepEval assert_test() checks AI quality dimensions where multiple differently worded answers can still be acceptable.",
    },
    {
        "file": ".github/workflows/deepeval.yml",
        "title": "Before coding: understand GitHub Actions CI/CD",
        "what": "This YAML file tells GitHub to create a temporary computer and run our DeepEval automation automatically when code is pushed or a pull request is opened.",
        "why": "Local tests depend on a person remembering to run them. CI/CD makes quality checks repeatable for every important change.",
        "without": "A developer could change the prompt, chunking, model, or retrieval code and merge it without running the AI regression suite.",
        "command": "push code → GitHub Actions → install → pytest → PASS/FAIL",
        "command_meaning": "The same pytest command students learned locally becomes an automated quality gate in GitHub.",
        "items": [
            ("on:", "Trigger", "Defines when the workflow should start, such as push or pull_request.", "Automation begins without a person manually opening a terminal."),
            ("actions/checkout", "Get the code", "Copies the repository files onto the temporary GitHub runner.", "The runner must have our project before it can test it."),
            ("actions/setup-python", "Install Python", "Provides the Python version our project expects.", "The CI computer starts clean, so we explicitly prepare its environment."),
            ("pip install -r requirements.txt", "Install dependencies", "Uses the requirements file built in Step 1.", "This is why requirements.txt matters beyond a student's laptop."),
            ("secrets.OPENAI_API_KEY", "Secure secret", "Makes the API key available to the test process without writing it into GitHub source code.", "Never hard-code API keys in Python or YAML."),
            ("pytest tests/test_deepeval.py -v", "Run the suite", "Runs the same automated tests that students can run locally.", "A failing test makes the GitHub job red so the team investigates before release."),
        ],
        "remember": "CI/CD is not a different test suite. It is another place that automatically runs the same tests you already built.",
    },
]


def render_project_file_explainer(step_index: int):
    step_index = max(0, min(step_index, len(FILE_LESSONS) - 1))
    lesson = FILE_LESSONS[step_index]

    st.markdown("## 🧠 Understand This File Before You Code")
    st.markdown(f"### {lesson['title']}")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**What is it?**")
        st.write(lesson["what"])
    with c2:
        st.markdown("**Why do we use it?**")
        st.write(lesson["why"])
    with c3:
        st.markdown("**What if we don't have it?**")
        st.write(lesson["without"])

    st.markdown("#### One command / idea to understand")
    st.code(lesson["command"], language="bash" if lesson["file"] in {"requirements.txt", ".github/workflows/deepeval.yml"} else "python")
    st.info(lesson["command_meaning"])

    st.markdown("#### Understand the pieces before typing them")
    for code, name, purpose, detail in lesson["items"]:
        with st.expander(f"`{code}` — {name}"):
            st.markdown("**What does it do?**")
            st.write(purpose)
            st.markdown("**Why does our project need it?**")
            st.write(detail)

    st.success("Key idea: " + lesson["remember"])
    st.caption("When this makes sense, continue to the editor below and build the file yourself. Use Hint 1 and Hint 2 first; Hint 3 contains the complete solution if you get stuck.")
