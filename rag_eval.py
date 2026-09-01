from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from openai import OpenAI
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RAGResult:
    input: str
    answer: str
    retrieval_context: list[str]


class RAGPipeline:
    """Small evaluation-friendly RAG pipeline that mirrors the DocPilotAI flow.

    The Streamlit app is interactive. Automated tests need the same core stages
    without clicking UI controls: load -> chunk -> index -> retrieve -> generate.
    """

    def __init__(self, chunks: list[str], top_k: int = 4, model: str | None = None):
        if not chunks:
            raise ValueError("At least one non-empty chunk is required.")
        self.chunks = chunks
        self.top_k = max(1, int(top_k))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=25000,
        )
        self.matrix = self.vectorizer.fit_transform(self.chunks)

    @staticmethod
    def chunk_text(text: str, size: int = 1200, overlap: int = 200) -> list[str]:
        text = (text or "").strip()
        if not text:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= len(text):
                break
            start = max(0, end - overlap)
        return chunks

    @classmethod
    def from_text(
        cls,
        text: str,
        *,
        chunk_size: int = 1200,
        overlap: int = 200,
        top_k: int = 4,
        model: str | None = None,
    ) -> "RAGPipeline":
        chunks = cls.chunk_text(text, chunk_size, overlap)
        return cls(chunks, top_k=top_k, model=model)

    @classmethod
    def from_text_file(
        cls,
        path: str | Path,
        *,
        chunk_size: int = 1200,
        overlap: int = 200,
        top_k: int = 4,
        model: str | None = None,
    ) -> "RAGPipeline":
        text = Path(path).read_text(encoding="utf-8")
        return cls.from_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
            top_k=top_k,
            model=model,
        )

    @classmethod
    def from_pdf(
        cls,
        path: str | Path,
        *,
        chunk_size: int = 1200,
        overlap: int = 200,
        top_k: int = 4,
        model: str | None = None,
    ) -> "RAGPipeline":
        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(text)
        if not pages:
            raise ValueError("No extractable text found in PDF.")
        return cls.from_text(
            "\n\n".join(pages),
            chunk_size=chunk_size,
            overlap=overlap,
            top_k=top_k,
            model=model,
        )

    def retrieve(self, question: str) -> list[str]:
        query = self.vectorizer.transform([question])
        scores = cosine_similarity(query, self.matrix).flatten()
        order = scores.argsort()[::-1][: self.top_k]
        return [self.chunks[i] for i in order]

    def ask(self, question: str) -> RAGResult:
        context = self.retrieve(question)
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        joined_context = "\n\n---\n\n".join(context)
        prompt = f"""
You are a document-grounded assistant under automated QA evaluation.
Answer only from the supplied context.
If the answer is not supported, say exactly: I don't know based on the uploaded document.
Keep the answer concise and do not invent facts.

CONTEXT:
{joined_context}

QUESTION:
{question}
""".strip()
        response = client.responses.create(model=self.model, input=prompt)
        return RAGResult(
            input=question,
            answer=response.output_text.strip(),
            retrieval_context=context,
        )


def load_goldens(path: str | Path) -> list[dict]:
    import json

    return json.loads(Path(path).read_text(encoding="utf-8"))
