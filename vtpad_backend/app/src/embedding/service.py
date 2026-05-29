"""EmbeddingService — manages vector embeddings for semantic search via pgvector."""

import json
import math
from typing import Optional

from tortoise import Tortoise
from tortoise.expressions import Q

from .model import EmbeddingModel
from .provider import EmbeddingProvider, EMBEDDING_DIMENSIONS
import logging
logger = logging.getLogger(__name__)


class EmbeddingService:
    provider = EmbeddingProvider()

    @staticmethod
    async def _get_raw_conn():
        """Get raw asyncpg connection from pool."""
        conn = Tortoise.get_connection("default")
        # Ensure pool is created
        if conn._pool is None:
            await conn.execute_query("SELECT 1")
        return conn._pool.acquire()

    @staticmethod
    async def _set_pgvector(record_id: str, vector: list[float]) -> None:
        """Write vector into pgvector column via raw SQL."""
        vec_str = "[" + ",".join(str(v) for v in vector) + "]"
        async with await EmbeddingService._get_raw_conn() as raw_conn:
            await raw_conn.execute(
                "UPDATE embedding SET embedding_vector = $1::vector WHERE id = $2",
                vec_str, record_id,
            )

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors (Python fallback)."""
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

        record = await EmbeddingModel.create(
            space_id=space_id,
            source_type="test_case",
            source_id=case_id,
            source_field="full_text",
            text_chunk=content[:8000],
            embedding=json.dumps(embedding),
        )
        await cls._set_pgvector(str(record.id), embedding)

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

        chunks = cls._chunk_text(content, max_length=3000, overlap=200)
        texts = [f"{title}\n\n{chunk}" for chunk in chunks]

        embeddings = await cls.provider.embed(texts)
        if embeddings is None:
            return

        for chunk, emb in zip(chunks, embeddings):
            record = await EmbeddingModel.create(
                space_id=space_id,
                source_type="tech_doc",
                source_id=doc_id,
                source_field="content",
                text_chunk=chunk[:8000],
                embedding=json.dumps(emb),
            )
            await cls._set_pgvector(str(record.id), emb)

    @classmethod
    async def delete_embeddings(cls, source_type: str, source_id: str) -> None:
        """Delete all embeddings for a source entity."""
        await EmbeddingModel.filter(source_type=source_type, source_id=source_id).delete()

    @classmethod
    async def _search_pgvector(
        cls,
        space_id: str,
        query_embedding: list[float],
        source_types: list[str] | None = None,
        top_k: int = 10,
        min_score: float = 0.7,
    ) -> list[dict]:
        """Native pgvector cosine similarity search."""
        vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
        source_filter = ""
        params = [vec_str, space_id, top_k * 3]  # fetch more for filtering

        if source_types:
            placeholders = ",".join(f"${i + 4}" for i in range(len(source_types)))
            source_filter = f"AND source_type = ANY(ARRAY[{placeholders}])"
            params.extend(source_types)

        sql = f"""
            SELECT id, source_type, source_id, source_field, text_chunk,
                   1 - (embedding_vector <=> $1::vector) AS score
            FROM embedding
            WHERE space_id = $2
              AND embedding_vector IS NOT NULL
              {source_filter}
            ORDER BY embedding_vector <=> $1::vector
            LIMIT $3
        """

        async with await cls._get_raw_conn() as raw_conn:
            rows = await raw_conn.fetch(sql, *params)

        results = []
        for row in rows:
            score = row["score"]
            if score is not None and score >= min_score:
                results.append({
                    "source_type": row["source_type"],
                    "source_id": str(row["source_id"]),
                    "source_field": row["source_field"],
                    "text_chunk": row["text_chunk"],
                    "score": round(score, 4),
                })
        return results[:top_k]

    @classmethod
    async def semantic_search(
        cls,
        space_id: str,
        query: str,
        source_types: list[str] | None = None,
        top_k: int = 10,
        min_score: float = 0.7,
    ) -> list[dict]:
        """Semantic search via pgvector cosine similarity."""
        query_embedding = await cls.provider.embed_single(query)
        if query_embedding is None:
            return []

        # Try pgvector native search first
        try:
            return await cls._search_pgvector(
                space_id=space_id,
                query_embedding=query_embedding,
                source_types=source_types,
                top_k=top_k,
                min_score=min_score,
            )
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            # Fallback to Python cosine similarity
            pass

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
