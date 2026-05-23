"""Batch reindex all test cases for semantic search.

Usage:
    cd vtpad_backend
    .venv/bin/python scripts/reindex_embeddings.py [--space-id SPACE_ID]
"""

import argparse
import asyncio
import sys

sys.path.insert(0, ".")

from app.main import config_orm
from tortoise import Tortoise
from app.src.test_case.model import TestCaseModel
from app.src.embedding.service import EmbeddingService


async def main():
    parser = argparse.ArgumentParser(description="Reindex test case embeddings")
    parser.add_argument("--space-id", help="Reindex only this space")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size")
    args = parser.parse_args()

    await Tortoise.init(config=config_orm)

    q = TestCaseModel.filter(status="active")
    if args.space_id:
        q = q.filter(space_id=args.space_id)

    total = await q.count()
    print(f"Found {total} test cases to index")

    processed = 0
    async for case in q:
        await EmbeddingService.index_test_case(
            case_id=str(case.id),
            space_id=str(case.space_id),
            title=case.title,
            text=case.text,
            steps=case.steps,
            expected_results=case.expected_results,
            preconditions=case.preconditions,
        )
        processed += 1
        if processed % args.batch_size == 0:
            print(f"  ... {processed}/{total} done")

    print(f"Done! Indexed {processed} test cases.")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
