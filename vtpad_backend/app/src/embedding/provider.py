"""Embedding provider — generates vector embeddings from text."""

import os
from typing import Optional

import httpx
import logging
logger = logging.getLogger(__name__)


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://192.168.3.15:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "nomic-embed-text:latest")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_URL = "https://api.openai.com/v1/embeddings"
OPENAI_MODEL = "text-embedding-3-small"

EMBEDDING_DIMENSIONS = 768  # nomic-embed-text dimensionality


class EmbeddingProvider:
    """Local Ollama embeddings (default) with OpenAI fallback."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)

    async def embed(self, texts: list[str]) -> list[list[float]] | None:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []

        texts = [t.strip() for t in texts if t and t.strip()]
        if not texts:
            return []

        # Try Ollama first
        result = await self._embed_ollama(texts)
        if result is not None:
            return result

        # Fallback to OpenAI
        if OPENAI_API_KEY:
            return await self._embed_openai(texts)

        return None

    async def embed_single(self, text: str) -> list[float] | None:
        """Generate embedding for a single text."""
        result = await self.embed([text])
        return result[0] if result else None

    async def _embed_ollama(self, texts: list[str]) -> list[list[float]] | None:
        """Call Ollama /api/embeddings endpoint."""
        embeddings = []
        for text in texts:
            try:
                response = await self.client.post(
                    f"{OLLAMA_HOST}/api/embeddings",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": text,
                    },
                )
                response.raise_for_status()
                data = response.json()
                emb = data.get("embedding")
                if emb:
                    embeddings.append(emb)
            except Exception as e:
                logger.error('Unexpected error: %s', e, exc_info=True)
                return None
        return embeddings if embeddings else None

    async def _embed_openai(self, texts: list[str]) -> list[list[float]] | None:
        """Call OpenAI embeddings API."""
        try:
            response = await self.client.post(
                OPENAI_EMBEDDING_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_MODEL,
                    "input": texts,
                    "dimensions": EMBEDDING_DIMENSIONS,
                },
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            return None

    async def close(self):
        await self.client.aclose()
