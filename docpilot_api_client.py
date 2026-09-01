from __future__ import annotations

from pathlib import Path

import httpx


class DocPilotAPIClient:
    """Small reusable client used by beginner pytest + DeepEval automation."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        # Save the API address once so tests do not repeat it everywhere.
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        # Call the health endpoint to confirm the API is running.
        response = httpx.get(f"{self.base_url}/api/health", timeout=20)
        # Raise an error immediately when the API returned 4xx/5xx.
        response.raise_for_status()
        # Convert the JSON response into a Python dictionary.
        return response.json()

    def upload_pdf(self, pdf_path: str | Path) -> dict:
        # Open the PDF in binary mode because an API upload sends bytes.
        with Path(pdf_path).open("rb") as pdf_file:
            response = httpx.post(
                f"{self.base_url}/api/documents",
                files={"file": (Path(pdf_path).name, pdf_file, "application/pdf")},
                timeout=60,
            )
        response.raise_for_status()
        return response.json()

    def create_text_document(self, text: str) -> dict:
        # CI uses a tiny text fixture so students can learn the framework first.
        response = httpx.post(
            f"{self.base_url}/api/documents/text",
            json={"text": text},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def ask(self, document_id: str, question: str) -> dict:
        # Send one question to the uploaded document's RAG agent.
        response = httpx.post(
            f"{self.base_url}/api/documents/{document_id}/ask",
            json={"question": question},
            timeout=90,
        )
        response.raise_for_status()
        # The returned dictionary includes answer + retrieval_context for DeepEval.
        return response.json()
