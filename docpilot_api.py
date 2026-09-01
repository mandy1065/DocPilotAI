from __future__ import annotations

import re
import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from rag_eval import RAGPipeline


app = FastAPI(
    title="DocPilot AI RAG API",
    version="1.0.0",
    description="Small API wrapper around the DocPilot RAG pipeline for QA automation training.",
)

# Classroom-only in-memory document store. Each uploaded source gets a document id.
DOCUMENTS: dict[str, RAGPipeline] = {}


class QuestionRequest(BaseModel):
    question: str


class TextDocumentRequest(BaseModel):
    text: str


@app.get("/api/health")
def health():
    """Simple endpoint automation can call before running the suite."""
    return {"status": "ok"}


@app.post("/api/documents")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a text-based PDF and create a searchable RAG document."""
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty.")

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
            temp_pdf.write(content)
            temp_pdf.flush()
            pipeline = RAGPipeline.from_pdf(Path(temp_pdf.name))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {exc}") from exc

    document_id = str(uuid4())
    DOCUMENTS[document_id] = pipeline
    return {
        "document_id": document_id,
        "filename": filename,
        "chunks": len(pipeline.chunks),
    }


@app.post("/api/documents/text")
def create_text_document(payload: TextDocumentRequest):
    """Create a focused classroom document for deterministic CI automation.

    The production-style PDF endpoint keeps the normal DocPilot chunking flow.
    This teaching endpoint intentionally uses small sentence chunks and Top-K=1
    so beginners begin with a clean retrieval baseline before experimenting with
    noisier retrieval settings and watching DeepEval metrics fail.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required.")

    chunks = [
        piece.strip()
        for piece in re.split(r"(?<=[.!?])\s+", payload.text.strip())
        if piece.strip()
    ]
    pipeline = RAGPipeline(chunks, top_k=1)
    document_id = str(uuid4())
    DOCUMENTS[document_id] = pipeline
    return {
        "document_id": document_id,
        "chunks": len(pipeline.chunks),
        "source_type": "text-fixture",
    }


@app.post("/api/documents/{document_id}/ask")
def ask_document(document_id: str, payload: QuestionRequest):
    """Ask the RAG agent and expose answer + retrieval context for DeepEval."""
    pipeline = DOCUMENTS.get(document_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    result = pipeline.ask(payload.question)
    return {
        "document_id": document_id,
        "question": payload.question,
        "answer": result.answer,
        "retrieval_context": result.retrieval_context,
    }
