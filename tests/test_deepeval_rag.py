import json
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

from rag_eval import RAGPipeline

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data"
GOLDENS = json.loads((DATA / "golden_cases.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def rag_pipeline():
    # This uses the same load -> chunk -> retrieve -> generate pattern as the
    # PDF agent, but a controlled text fixture keeps CI deterministic and easy
    # for students to inspect. For a real PDF, use RAGPipeline.from_pdf(path).
    return RAGPipeline.from_text_file(DATA / "training_policy.txt", top_k=4)


GENERATOR_METRICS = [
    AnswerRelevancyMetric(threshold=0.70),
    FaithfulnessMetric(threshold=0.80),
]

RETRIEVER_METRICS = [
    ContextualRelevancyMetric(threshold=0.60),
    ContextualPrecisionMetric(threshold=0.60),
    ContextualRecallMetric(threshold=0.60),
]


@pytest.mark.parametrize("golden", GOLDENS, ids=[g["id"] for g in GOLDENS])
def test_rag_generator_quality(golden, rag_pipeline):
    result = rag_pipeline.ask(golden["input"])

    test_case = LLMTestCase(
        input=golden["input"],
        actual_output=result.answer,
        expected_output=golden["expected_output"],
        retrieval_context=result.retrieval_context,
    )

    # Generator metrics answer two different QA questions:
    # 1) Did the response address the user's intent?
    # 2) Did the response stay supported by runtime retrieval context?
    assert_test(test_case, GENERATOR_METRICS)


@pytest.mark.parametrize("golden", GOLDENS, ids=[g["id"] for g in GOLDENS])
def test_rag_retriever_quality(golden, rag_pipeline):
    result = rag_pipeline.ask(golden["input"])

    test_case = LLMTestCase(
        input=golden["input"],
        actual_output=result.answer,
        expected_output=golden["expected_output"],
        retrieval_context=result.retrieval_context,
    )

    # Retriever metrics help identify whether a bad final answer began in
    # search/ranking/completeness rather than in the LLM generator.
    assert_test(test_case, RETRIEVER_METRICS)


def test_pipeline_can_be_built_from_real_pdf_when_student_supplies_one():
    """Teaching example for local PDF automation.

    Set DOCPILOT_TEST_PDF to a text-based PDF path before running pytest.
    CI skips this test because the course repository uses a readable text
    fixture for the default golden regression suite.
    """
    import os

    pdf_path = os.getenv("DOCPILOT_TEST_PDF")
    if not pdf_path:
        pytest.skip("Set DOCPILOT_TEST_PDF to run the real-PDF pipeline test.")

    pipeline = RAGPipeline.from_pdf(pdf_path)
    result = pipeline.ask("Summarize one important policy from this document.")

    assert result.answer.strip()
    assert result.retrieval_context
