import json
import os
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from docpilot_api_client import DocPilotAPIClient


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data"
GOLDENS = json.loads((DATA / "golden_cases.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def api_client():
    """Create one reusable API client for the complete test session."""
    base_url = os.getenv("DOCPILOT_API_URL", "http://127.0.0.1:8000")
    client = DocPilotAPIClient(base_url)
    assert client.health()["status"] == "ok"
    return client


@pytest.fixture(scope="session")
def document_id(api_client):
    """Load the controlled source once, just like uploading one document before testing it."""
    source_text = (DATA / "training_policy.txt").read_text(encoding="utf-8")
    created = api_client.create_text_document(source_text)
    return created["document_id"]


@pytest.mark.parametrize("golden", GOLDENS, ids=[g["id"] for g in GOLDENS])
def test_rag_api_with_all_deepeval_metrics(golden, api_client, document_id):
    # STEP 1: Call the system under test through its API.
    result = api_client.ask(document_id, golden["input"])

    # STEP 2: Convert the API response into DeepEval's standard test-case object.
    test_case = LLMTestCase(
        input=golden["input"],
        actual_output=result["answer"],
        expected_output=golden["expected_output"],
        retrieval_context=result["retrieval_context"],
    )

    # STEP 3: Add generator + retriever metrics to one reusable quality gate.
    metrics = [
        AnswerRelevancyMetric(threshold=0.70),
        FaithfulnessMetric(threshold=0.80),
        ContextualRelevancyMetric(threshold=0.60),
        ContextualPrecisionMetric(threshold=0.60),
        ContextualRecallMetric(threshold=0.60),
    ]

    # STEP 4: Fail pytest when an AI quality threshold is missed.
    assert_test(test_case, metrics)
