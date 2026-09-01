# DeepEval RAG Automation — Student Guide

This phase turns DocPilotAI-style RAG testing into an automated regression suite.

## 1. Install

```bash
pip install -r requirements.txt
```

Set your OpenAI key locally.

macOS/Linux:
```bash
export OPENAI_API_KEY="your-key"
```

PowerShell:
```powershell
$env:OPENAI_API_KEY="your-key"
```

## 2. Understand the automated data flow

```text
question (input)
      ↓
RAGPipeline.retrieve()
      ↓
retrieval_context
      ↓
RAGPipeline.ask()
      ↓
actual_output
      ↓
DeepEval metrics
      ↓
score + reason + PASS/FAIL
```

For reference-based retriever metrics, the golden dataset also supplies `expected_output`.

## 3. Run the course regression suite

```bash
pytest tests/test_deepeval_rag.py -v
```

The suite covers:

- Answer Relevancy — does the response answer the input?
- Faithfulness — is the response supported by retrieved context?
- Contextual Relevancy — is retrieved context relevant to the input?
- Contextual Precision — are relevant chunks ranked ahead of irrelevant ones?
- Contextual Recall — does retrieval contain the information needed for the expected answer?

## 4. Run against a real PDF locally

`rag_eval.py` supports text-based PDFs through `RAGPipeline.from_pdf(path)`.

To activate the optional PDF test:

macOS/Linux:
```bash
export DOCPILOT_TEST_PDF="/path/to/training.pdf"
pytest tests/test_deepeval_rag.py -v
```

PowerShell:
```powershell
$env:DOCPILOT_TEST_PDF="C:\path\to\training.pdf"
pytest tests/test_deepeval_rag.py -v
```

The default CI suite uses `tests/data/training_policy.txt` so students can inspect and edit the knowledge source directly without storing a binary PDF in the course fixture.

## 5. Golden data

Edit `tests/data/golden_cases.json` to add stable regression cases.

Each case contains:

```json
{
  "id": "reset_link",
  "input": "How long is the password reset link valid?",
  "expected_output": "The password reset link expires after 30 minutes."
}
```

Add high-value business scenarios, not every possible prompt.

## 6. GitHub Actions CI/CD

The workflow is `.github/workflows/rag-deepeval.yml`.

Before it can pass, create this GitHub repository secret:

```text
OPENAI_API_KEY
```

Then every matching push or pull request can run the DeepEval regression suite automatically.

## 7. How to debug a failure

Use the failed metric to choose where to investigate:

```text
Answer Relevancy FAIL
→ generator did not answer the user's intent well

Faithfulness FAIL
→ generator contradicted or exceeded retrieved evidence

Contextual Relevancy FAIL
→ retriever returned noisy or unrelated context

Contextual Precision FAIL
→ useful chunks are ranked below less useful chunks

Contextual Recall FAIL
→ retrieval missed information required for the expected answer
```

Always inspect the question, expected output, runtime answer, retrieval context, metric score, and metric reason before logging a defect.
