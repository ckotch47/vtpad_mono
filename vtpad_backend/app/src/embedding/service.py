"""EmbeddingService — manages vector embeddings for semantic search."""

import json
import math
from typing import Optional

from tortoise.expressions import Q

from .model import EmbeddingModel
from .provider import EmbeddingProvider, EMBEDDING_DIMENSIONS


class EmbeddingService:
    provider = EmbeddingProvider()

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def _extract_text(
        source_type: str,
        title: str | None = None,
        text: str | None = None,
        steps: str | None = None,
        expected_results: str | None = None,
        preconditions: str | None = None,
        description: str | None = None,
    ) -> str:
        """Extract searchable text from a source entity."""
        parts = []
        if title:
            parts.append(title)
        if text:
            parts.append(text)
        if description:
            parts.append(description)
        if preconditions:
            parts.append(preconditions)
        if steps:
            parts.append(steps)
        if expected_results:
            parts.append(expected_results)
        return "\n\n".join(parts)

    @classmethod
    async def index_test_case(
        cls,
        case_id: str,
        space_id: str,
        title: str | None = None,
        text: str | None = None,
        steps: str | None = None,
        expected_results: str | None = None,
        preconditions: str | None = None,
    ) -> None:
        """Create/update embeddings for a test case."""
        # Delete old embeddings
        await EmbeddingModel.filter(source_type="test_case", source_id=case_id).delete()

        content = cls._extract_text(
            "test_case",
            title=title,
            text=text,
            steps=steps,
            expected_results=expected_results,
            preconditions=preconditions,
        )
        if not content or not content.strip():
            return

        embedding = await cls.provider.embed_single(content)
        if embedding is None:
            return

        await EmbeddingModel.create(
            space_id=space_id,
            source_type="test_case",
            source_id=case_id,
            source_field="full_text",
            text_chunk=content[:8000],
            embedding=json.dumps(embedding),
        )

    @classmethod
    async def index_tech_doc(
        cls,
        doc_id: str,
        space_id: str,
        title: str,
        content: str,
    ) -> None:
        """Create/update embeddings for a tech doc."""
        await EmbeddingModel.filter(source_type="tech_doc", source_id=doc_id).delete()

        if not content or not content.strip():
            return

        # Simple chunking: whole doc if < 4000 chars, else split by paragraphs
        chunks = cls._chunk_text(content, max_length=3000, overlap=200)
        texts = [f"{title}\n\n{chunk}" for chunk in chunks]

        embeddings = await cls.provider.embed(texts)
        if embeddings is None:
            return

        for chunk, emb in zip(chunks, embeddings):
            await EmbeddingModel.create(
                space_id=space_id,
                source_type="tech_doc",
                source_id=doc_id,
                source_field="content",
                text_chunk=chunk[:8000],
                embedding=json.dumps(emb),
            )

    @classmethod
    async def delete_embeddings(cls, source_type: str, source_id: str) -> None:
        """Delete all embeddings for a source entity."""
        await EmbeddingModel.filter(source_type=source_type, source_id=source_id).delete()

    @classmethod
    async def semantic_search(
        cls,
        space_id: str,
        query: str,
        source_types: list[str] | None = None,
        top_k: int = 10,
        min_score: float = 0.7,
    ) -> list[dict]:
        """Semantic search via cosine similarity in Python.

        NOTE: For production with large datasets, switch to pgvector native
        vector operations (embedding_vector column with VECTOR type).
        """
        query_embedding = await cls.provider.embed_single(query)
        if query_embedding is None:
            return []

        q = EmbeddingModel.filter(space_id=space_id)
        if source_types:
            q = q.filter(source_type__in=source_types)

        items = await q.all()
        results = []
        for item in items:
            if not item.embedding:
                continue
            try:
                vec = item.embedding
                if isinstance(vec, str):
                    vec = json.loads(vec)
                if not isinstance(vec, list):
                    continue
                score = cls._cosine_similarity(query_embedding, vec)
                if score >= min_score:
                    results.append({
                        "source_type": item.source_type,
                        "source_id": str(item.source_id),
                        "source_field": item.source_field,
                        "text_chunk": item.text_chunk,
                        "score": round(score, 4),
                    })
            except (json.JSONDecodeError, ValueError, TypeError):
                continue

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _chunk_text(text: str, max_length: int = 3000, overlap: int = 200) -> list[str]:
        """Split text into overlapping chunks."""
        if len(text) <= max_length:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + max_length
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks
