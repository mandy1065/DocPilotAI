import ast
import io
import json
import os
import zipfile

import streamlit as st


PROJECT_FILES = [
    "requirements.txt",
    "api_client.py",
    "tests/data/golden_cases.json",
    "tests/test_deepeval_api.py",
    ".github/workflows/deepeval.yml",
]

STARTERS = {
    "requirements.txt": "# Add only the packages YOUR automation framework needs.\n",
    "api_client.py": "# Create a small reusable client that talks to the DocPilot API.\n",
    "tests/data/golden_cases.json": "[\n  \n]\n",
    "tests/test_deepeval_api.py": "# Build the DeepEval API regression test one step at a time.\n",
    ".github/workflows/deepeval.yml": "# Run the same pytest framework automatically in GitHub Actions.\n",
}

SOLUTIONS = {
    "requirements.txt": """# httpx sends HTTP requests to the API we are testing.
httpx>=0.27,<1

# pytest discovers and runs our automated test functions.
pytest>=8,<9

# deepeval provides AI quality metrics and LLMTestCase.
deepeval>=3,<4

# DeepEval can use OpenAI as the judge model for these metrics.
openai>=1,<3
""",
    "api_client.py": '''import os
import httpx


class DocPilotAPIClient:
    # Store one API address so every test does not repeat the URL.
    def __init__(self):
        self.base_url = os.getenv("DOCPILOT_API_URL", "http://127.0.0.1:8000")

    def health(self):
        # Send GET /api/health to check that the system under test is running.
        response = httpx.get(f"{self.base_url}/api/health", timeout=20)
        # Stop the test immediately if the server returned 4xx or 5xx.
        response.raise_for_status()
        # Convert JSON into a normal Python dictionary.
        return response.json()

    def create_text_document(self, text):
        # This lightweight endpoint gives CI a predictable classroom document.
        response = httpx.post(
            f"{self.base_url}/api/documents/text",
            json={"text": text},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def upload_pdf(self, pdf_path):
        # Open the PDF as bytes because file uploads are binary HTTP requests.
        with open(pdf_path, "rb") as pdf_file:
            response = httpx.post(
                f"{self.base_url}/api/documents",
                files={"file": pdf_file},
                timeout=60,
            )
        response.raise_for_status()
        return response.json()

    def ask(self, document_id, question):
        # Send the student's question to the uploaded document's RAG agent.
        response = httpx.post(
            f"{self.base_url}/api/documents/{document_id}/ask",
            json={"question": question},
            timeout=90,
        )
        response.raise_for_status()
        # Response includes answer AND retrieval_context for DeepEval.
        return response.json()
''',
    "tests/data/golden_cases.json": '''[
  {
    "id": "reset-link",
    "input": "How long is a password reset link valid?",
    "expected_output": "Password reset links expire after 30 minutes."
  },
  {
    "id": "returns",
    "input": "Can I return an opened product after 20 days?",
    "expected_output": "No. Returns within 30 days require the item to be unopened."
  },
  {
    "id": "remote-work",
    "input": "Can a new employee work remotely immediately?",
    "expected_output": "No. New employees must complete their first 90 days in the office."
  }
]
''',
    "tests/test_deepeval_api.py": '''import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.test_case import LLMTestCase

from api_client import DocPilotAPIClient


ROOT = Path(__file__).resolve().parents[1]
GOLDENS = json.loads(
    (ROOT / "tests" / "data" / "golden_cases.json").read_text()
)


@pytest.fixture(scope="session")
def api_client():
    # Create one reusable API client for the complete pytest run.
    client = DocPilotAPIClient()
    # A normal assertion proves the API is available before AI tests begin.
    assert client.health()["status"] == "ok"
    return client


@pytest.fixture(scope="session")
def document_id(api_client):
    # Use small known source text while learning the framework.
    source = """Password reset links expire after 30 minutes.
Items may be returned within 30 days only if unopened.
New employees must complete their first 90 days in the office."""
    # Create one document once and reuse its id in all test cases.
    result = api_client.create_text_document(source)
    return result["document_id"]


@pytest.mark.parametrize("golden", GOLDENS, ids=[g["id"] for g in GOLDENS])
def test_rag_quality(golden, api_client, document_id):
    # LEVEL 1: Call the real RAG API.
    result = api_client.ask(document_id, golden["input"])

    # LEVEL 2: Map API data into DeepEval's test-case structure.
    case = LLMTestCase(
        input=golden["input"],
        actual_output=result["answer"],
        expected_output=golden["expected_output"],
        retrieval_context=result["retrieval_context"],
    )

    # LEVEL 3: Add all five RAG quality metrics.
    metrics = [
        # Did the answer address the user's question?
        AnswerRelevancyMetric(threshold=0.70),
        # Did the answer stay supported by retrieved evidence?
        FaithfulnessMetric(threshold=0.80),
        # Were the retrieved chunks useful for the question?
        ContextualRelevancyMetric(threshold=0.60),
        # Were useful chunks ranked ahead of weak chunks?
        ContextualPrecisionMetric(threshold=0.60),
        # Did retrieval include enough evidence for the expected answer?
        ContextualRecallMetric(threshold=0.60),
    ]

    # LEVEL 4: Turn the metric thresholds into an automated PASS/FAIL gate.
    assert_test(case, metrics)
''',
    ".github/workflows/deepeval.yml": '''name: DeepEval API Quality Gate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  ai-quality-tests:
    runs-on: ubuntu-latest

    steps:
      # Download the automation framework onto the GitHub runner.
      - name: Checkout code
        uses: actions/checkout@v4

      # Give the runner the same Python version used by the project.
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      # Install packages listed in requirements.txt.
      - name: Install automation packages
        run: pip install -r requirements.txt

      # Run exactly the same pytest command the student used locally.
      - name: Run DeepEval API tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DOCPILOT_API_URL: ${{ secrets.DOCPILOT_API_URL }}
        run: pytest tests/test_deepeval_api.py -v
''',
}

LESSONS = [
    {
        "title": "1 · Prepare the automation packages",
        "file": "requirements.txt",
        "what": "requirements.txt is a package list. It tells another computer which extra Python tools your automation framework needs.",
        "why": "Python does not include pytest, DeepEval, or an HTTP client by default. A teammate or CI runner can install the same tools with one command instead of guessing.",
        "without": "The project may fail with errors such as 'No module named pytest' or 'No module named deepeval'.",
        "analogy": "Think of it as the ingredient list for a recipe. Before cooking, we make sure all ingredients are available.",
        "learn": [
            ("httpx", "Sends GET/POST HTTP requests to the DocPilot API."),
            ("pytest", "Finds test_ functions, runs them, and reports PASS/FAIL."),
            ("deepeval", "Provides LLMTestCase and the AI evaluation metrics."),
            ("openai", "Lets DeepEval use an OpenAI judge model for metric scoring."),
            (">= and <", ">=8 means version 8 or newer; <9 prevents an unplanned major-version upgrade."),
            ("pip install -r requirements.txt", "Read this file and install every package listed in it."),
        ],
        "check": ["httpx", "pytest", "deepeval", "openai"],
        "hint1": "Your framework needs an HTTP client, a test runner, DeepEval, and the judge-model SDK.",
        "hint2": "Use httpx, pytest, deepeval, and openai.",
    },
    {
        "title": "2 · Build one reusable API client",
        "file": "api_client.py",
        "what": "An API client is a small Python helper that knows how to talk to the application we are testing.",
        "why": "Without it, every test would repeat URLs, HTTP methods, timeouts, JSON parsing, and error handling. A framework puts repeated work in one place.",
        "without": "Your test file becomes long and difficult to maintain. If the API URL changes, you may need to edit many tests.",
        "analogy": "The client is like a remote control. Tests press simple buttons such as health(), upload_pdf(), and ask() instead of rebuilding the electronics each time.",
        "learn": [
            ("GET /api/health", "Checks whether the API is running."),
            ("POST /api/documents", "Uploads a real PDF to the RAG agent."),
            ("POST /api/documents/{id}/ask", "Sends a question to that document."),
            ("response.raise_for_status()", "Immediately fails when the API returns an HTTP error."),
            ("response.json()", "Turns API JSON into a Python dictionary."),
            ("retrieval_context", "The API exposes retrieved chunks so DeepEval can test the retriever and grounding."),
        ],
        "check": ["class DocPilotAPIClient", "def health", "def upload_pdf", "def ask", "httpx", "retrieval_context"],
        "hint1": "Create one class and give it methods for health, PDF upload, and asking a question.",
        "hint2": "Use httpx.get/post, raise_for_status(), and response.json().",
    },
    {
        "title": "3 · Create reusable golden test data",
        "file": "tests/data/golden_cases.json",
        "what": "Golden data is a small collection of important questions where QA already knows the correct expected behavior.",
        "why": "Separating test data from Python makes the framework easier to grow. QA can add a new scenario without rewriting the whole test function.",
        "without": "Questions and expected answers become hard-coded throughout the Python file, which becomes repetitive and difficult to review.",
        "analogy": "It is the test-case spreadsheet of the automation framework: input in one field, expected result in another.",
        "learn": [
            ("id", "Readable name shown by pytest for the scenario."),
            ("input", "Question sent to the RAG API."),
            ("expected_output", "Known ideal answer used by reference-based metrics."),
            ("JSON", "Simple text format for storing structured test data."),
        ],
        "check": ["id", "input", "expected_output"],
        "hint1": "Every case needs a name, the question, and the expected answer.",
        "hint2": "Use a JSON list of objects with id, input, and expected_output.",
    },
    {
        "title": "4 · Grow one test into a DeepEval framework",
        "file": "tests/test_deepeval_api.py",
        "what": "This is the main automated test file. Pytest runs it, the API client calls the RAG agent, and DeepEval scores the runtime result.",
        "why": "This file connects all framework layers: test data → API → actual answer/context → LLMTestCase → metrics → PASS/FAIL.",
        "without": "You would have pieces of code but no repeatable regression test that proves AI quality after changes.",
        "analogy": "This is the conductor of the orchestra. It does not play every instrument; it coordinates the client, data, and metrics.",
        "learn": [
            ("fixture", "Creates reusable setup such as the API client or document id."),
            ("parametrize", "Runs the same test once for every golden case."),
            ("LLMTestCase", "Standard DeepEval container for input, actual output, expected output, and retrieval context."),
            ("Answer Relevancy", "Did the answer address the question?"),
            ("Faithfulness", "Did the answer stay supported by retrieved evidence?"),
            ("Contextual Relevancy", "Were retrieved chunks useful?"),
            ("Contextual Precision", "Were useful chunks ranked well?"),
            ("Contextual Recall", "Was enough evidence retrieved?"),
            ("assert_test", "Turns metric thresholds into pytest PASS/FAIL."),
        ],
        "check": ["LLMTestCase", "AnswerRelevancyMetric", "FaithfulnessMetric", "ContextualRelevancyMetric", "ContextualPrecisionMetric", "ContextualRecallMetric", "assert_test", "parametrize"],
        "hint1": "First call api_client.ask(). Then put the response into LLMTestCase.",
        "hint2": "Create a metrics list with all five metrics and pass case + metrics into assert_test().",
    },
    {
        "title": "5 · Move the same framework into CI/CD",
        "file": ".github/workflows/deepeval.yml",
        "what": "A GitHub Actions workflow is an instruction file for a temporary cloud computer called a runner.",
        "why": "The runner executes the same tests automatically after a push or pull request, so AI quality does not depend on someone remembering to run pytest manually.",
        "without": "A developer can change prompts, retrieval, or models and merge the change without running the AI regression suite.",
        "analogy": "Local pytest is a tester pressing the test button. CI/CD is a robot that presses that same button automatically every time code changes.",
        "learn": [
            ("checkout", "Downloads the repository onto the runner."),
            ("setup-python", "Installs the required Python version."),
            ("pip install", "Installs the framework packages."),
            ("secrets", "Supplies API keys/URLs without putting them in source code."),
            ("pytest ... -v", "Runs the exact same regression command as local execution."),
        ],
        "check": ["actions/checkout", "actions/setup-python", "OPENAI_API_KEY", "DOCPILOT_API_URL", "pytest", "test_deepeval_api.py"],
        "hint1": "CI needs checkout, Python setup, package installation, secrets, and one pytest command.",
        "hint2": "The last step should run pytest tests/test_deepeval_api.py -v.",
    },
]


def _init_state():
    st.session_state.setdefault("api_lab_files", {})
    st.session_state.setdefault("api_lab_step", 0)
    st.session_state.setdefault("api_lab_passed", {})


def _validate_python(source):
    try:
        ast.parse(source)
        return True, "Python syntax is valid."
    except SyntaxError as exc:
        return False, f"Python syntax error on line {exc.lineno}: {exc.msg}"


def _validate(filename, source, required):
    if filename.endswith(".py"):
        ok, message = _validate_python(source)
        if not ok:
            return False, message
    if filename.endswith(".json"):
        try:
            data = json.loads(source)
            if not isinstance(data, list) or not data:
                return False, "Golden JSON needs at least one test case."
        except Exception as exc:
            return False, f"JSON is not valid: {exc}"
    missing = [token for token in required if token not in source]
    if missing:
        return False, "Still missing: " + ", ".join(missing)
    return True, "Great — this framework layer contains the required building blocks."


def _project_zip(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, content in files.items():
            archive.writestr(path, content)
        archive.writestr(
            "README.txt",
            "DeepEval API Automation Framework\n\n"
            "1. Install: pip install -r requirements.txt\n"
            "2. Set DOCPILOT_API_URL to the running DocPilot API.\n"
            "3. Set OPENAI_API_KEY for DeepEval judge metrics.\n"
            "4. Run: pytest tests/test_deepeval_api.py -v\n\n"
            "The PDF/RAG API is the system under test; this project is the QA automation framework.\n",
        )
    return buffer.getvalue()


def render_deepeval_project_lab():
    _init_state()

    st.markdown("## 🧑‍💻 Beginner → Framework Builder: DeepEval API Automation")
    st.write(
        "Build a real AI QA framework without rebuilding the RAG application. "
        "DocPilot's PDF/RAG API is the **system under test**. Your job is to automate it."
    )

    st.info(
        "Framework mental model: **Golden question → API call → answer + retrieval context → "
        "LLMTestCase → 5 DeepEval metrics → pytest PASS/FAIL → CI/CD**"
    )

    with st.expander("🌐 What API are we testing?", expanded=True):
        st.markdown(
            "**Provided by DocPilot:**\n\n"
            "- `GET /api/health` — check service\n"
            "- `POST /api/documents` — upload a PDF\n"
            "- `POST /api/documents/{id}/ask` — ask the PDF agent\n\n"
            "The ask response contains `answer` and `retrieval_context`, which is exactly what DeepEval needs."
        )
        st.code(
            '{\n  "answer": "The reset link expires after 30 minutes.",\n'
            '  "retrieval_context": ["Password reset links expire after 30 minutes."]\n}',
            language="json",
        )

    passed = sum(1 for i in range(len(LESSONS)) if st.session_state.api_lab_passed.get(i))
    st.progress(passed / len(LESSONS), text=f"Framework progress: {passed}/{len(LESSONS)} layers complete")

    left, right = st.columns([0.27, 0.73], gap="large")

    with left:
        st.markdown("### Framework Explorer")
        for i, lesson in enumerate(LESSONS):
            mark = "✅" if st.session_state.api_lab_passed.get(i) else "○"
            if st.button(f"{mark} {lesson['file']}", key=f"api_nav_{i}", use_container_width=True):
                st.session_state.api_lab_step = i
                st.rerun()
        st.markdown("---")
        st.caption("Provided system under test")
        st.write("🔒 `DocPilot PDF/RAG API`")
        st.caption("Files you build")
        for path in PROJECT_FILES:
            icon = "📄" if path in st.session_state.api_lab_files else "▫️"
            st.write(f"{icon} `{path}`")

    index = st.session_state.api_lab_step
    lesson = LESSONS[index]
    filename = lesson["file"]

    with right:
        st.markdown(f"### {lesson['title']}")

        st.markdown("#### 🧠 Understand this before you code")
        st.markdown(f"**What is it?** {lesson['what']}")
        st.markdown(f"**Why do we use it?** {lesson['why']}")
        st.markdown(f"**What if we don't have it?** {lesson['without']}")
        st.info(f"**Simple analogy:** {lesson['analogy']}")

        st.markdown("#### Learn the pieces")
        for term, meaning in lesson["learn"]:
            with st.expander(term):
                st.write(meaning)

        st.divider()
        st.markdown("#### ✍️ Now build this layer")

        if filename not in st.session_state.api_lab_files:
            if st.button(f"＋ Create {filename}", type="primary", key=f"api_create_{index}"):
                st.session_state.api_lab_files[filename] = STARTERS[filename]
                st.rerun()
        else:
            source = st.text_area(
                filename,
                value=st.session_state.api_lab_files[filename],
                height=390,
                key=f"api_editor_{index}",
                label_visibility="collapsed",
            )
            st.session_state.api_lab_files[filename] = source

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("▶ Validate", type="primary", key=f"api_validate_{index}", use_container_width=True):
                    ok, message = _validate(filename, source, lesson["check"])
                    if ok:
                        st.session_state.api_lab_passed[index] = True
                        st.success(message)
                    else:
                        st.error(message)
            with c2:
                with st.popover("💡 Hints", use_container_width=True):
                    st.markdown("**Hint 1 — direction**")
                    st.write(lesson["hint1"])
                    st.markdown("**Hint 2 — stronger clue**")
                    st.write(lesson["hint2"])
                    with st.expander("Hint 3 — complete commented solution"):
                        st.caption("Use this after trying. Comments explain the important lines and framework decisions.")
                        language = "python" if filename.endswith(".py") else ("json" if filename.endswith(".json") else "text")
                        st.code(SOLUTIONS[filename], language=language)
            with c3:
                if st.button("↺ Reset", key=f"api_reset_{index}", use_container_width=True):
                    st.session_state.api_lab_files[filename] = STARTERS[filename]
                    st.session_state.api_lab_passed.pop(index, None)
                    st.rerun()

            if st.session_state.api_lab_passed.get(index) and index < len(LESSONS) - 1:
                if st.button("Next framework layer →", key=f"api_next_{index}"):
                    st.session_state.api_lab_step += 1
                    st.rerun()

    st.divider()
    st.markdown("## 🚀 Run the framework")

    all_done = all(st.session_state.api_lab_passed.get(i) for i in range(len(LESSONS)))
    if not all_done:
        st.warning("Complete and validate all five framework layers to unlock the final API + DeepEval run.")
        return

    st.success("You built the framework. This is the same command you will run locally and in CI/CD.")
    st.code("pytest tests/test_deepeval_api.py -v", language="bash")

    run_col, download_col = st.columns(2)
    with run_col:
        if st.button("▶ Run one real API + DeepEval example", type="primary", use_container_width=True):
            try:
                # Do not execute arbitrary student Python on the shared Streamlit server.
                # Instead run the repository's controlled API in-process through FastAPI TestClient.
                from fastapi.testclient import TestClient
                from deepeval.metrics import (
                    AnswerRelevancyMetric,
                    FaithfulnessMetric,
                    ContextualRelevancyMetric,
                    ContextualPrecisionMetric,
                    ContextualRecallMetric,
                )
                from deepeval.test_case import LLMTestCase
                from docpilot_api import app

                key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
                if not key:
                    st.error("OPENAI_API_KEY is not configured for this Streamlit app.")
                    return
                os.environ["OPENAI_API_KEY"] = key

                client = TestClient(app)
                source_text = (
                    "Password reset links expire after 30 minutes. "
                    "Items may be returned within 30 days only if unopened. "
                    "New employees must complete their first 90 days in the office."
                )
                created = client.post("/api/documents/text", json={"text": source_text}).json()
                question = "How long is a password reset link valid?"
                expected = "Password reset links expire after 30 minutes."
                response = client.post(
                    f"/api/documents/{created['document_id']}/ask",
                    json={"question": question},
                )
                response.raise_for_status()
                result = response.json()

                case = LLMTestCase(
                    input=question,
                    actual_output=result["answer"],
                    expected_output=expected,
                    retrieval_context=result["retrieval_context"],
                )
                metrics = [
                    AnswerRelevancyMetric(threshold=0.70),
                    FaithfulnessMetric(threshold=0.80),
                    ContextualRelevancyMetric(threshold=0.60),
                    ContextualPrecisionMetric(threshold=0.60),
                    ContextualRecallMetric(threshold=0.60),
                ]

                rows = []
                for metric in metrics:
                    metric.measure(case)
                    rows.append({
                        "Metric": metric.__class__.__name__,
                        "Score": round(float(metric.score), 3),
                        "Threshold": metric.threshold,
                        "Result": "PASS" if metric.is_successful() else "FAIL",
                        "Reason": metric.reason,
                    })

                st.write("**API answer**")
                st.success(result["answer"])
                st.write("**API retrieval_context**")
                for chunk in result["retrieval_context"]:
                    st.write("•", chunk)
                st.dataframe(rows, use_container_width=True, hide_index=True)
            except Exception as exc:
                st.error(f"The controlled API evaluation could not complete: {exc}")

    with download_col:
        st.download_button(
            "↓ Download my API automation framework",
            data=_project_zip(dict(st.session_state.api_lab_files)),
            file_name="my_deepeval_api_framework.zip",
            mime="application/zip",
            use_container_width=True,
        )

    st.markdown("### What you can now explain in an interview")
    st.markdown(
        "I built a **data-driven pytest framework for a RAG API**. It uploads/creates a document, sends golden questions, "
        "captures the runtime answer and retrieval context, evaluates generator and retriever quality with five DeepEval metrics, "
        "and runs the same regression suite in CI/CD."
    )
