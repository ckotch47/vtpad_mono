import hashlib
from typing import Optional

from fastapi import HTTPException
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from .model import TechDocModel
from .dto import *
from ..embedding.service import EmbeddingService
from ..common.pagination import paginate
from ..space.model import SpaceModel


class TechDocService:
    @staticmethod
    async def _sanitize_parent_links(docs: list[TechDocModel]) -> None:
        """Hide stale/cross-space parent IDs from read responses."""
        parent_ids = {str(doc.parent_id) for doc in docs if doc.parent_id}
        if not parent_ids:
            return
        parents = await TechDocModel.filter(id__in=parent_ids).values("id", "space_id")
        valid_pairs = {(str(parent["id"]), str(parent["space_id"])) for parent in parents}
        for doc in docs:
            if doc.parent_id and (str(doc.parent_id), str(doc.space_id)) not in valid_pairs:
                doc.parent_id = None

    @staticmethod
    async def _validate_parent(
        parent_id: Optional[str],
        space_id: str,
        doc_id: Optional[str] = None,
        connection=None,
    ) -> None:
        if parent_id is None:
            return

        parent_query = TechDocModel.filter(id=parent_id)
        if connection is not None:
            parent_query = parent_query.using_db(connection)
        current = await parent_query.first()
        if current is None or str(current.space_id) != str(space_id):
            raise HTTPException(status_code=422, detail="Parent tech doc must belong to the same space")

        visited = set()
        while current is not None:
            current_id = str(current.id)
            if str(current.space_id) != str(space_id):
                raise HTTPException(status_code=422, detail="Parent tech doc hierarchy must belong to the same space")
            if current_id in visited:
                raise HTTPException(status_code=422, detail="Tech doc parent hierarchy contains a cycle")
            visited.add(current_id)
            if doc_id is not None and current_id == str(doc_id):
                raise HTTPException(status_code=422, detail="Tech doc cannot be nested under itself")
            parent_id = current.parent_id
            if parent_id is None:
                break
            parent_query = TechDocModel.filter(id=parent_id)
            if connection is not None:
                parent_query = parent_query.using_db(connection)
            current = await parent_query.first()

    @staticmethod
    async def _lock_space(space_id: str, connection) -> None:
        space = await SpaceModel.filter(id=space_id).using_db(connection).select_for_update().first()
        if space is None:
            raise HTTPException(status_code=404, detail="Space not found")

    @staticmethod
    async def create(dto: TechDocCreateDto) -> TechDocModel:
        content_hash = hashlib.sha256((dto.content or "").encode()).hexdigest()
        async with in_transaction() as connection:
            await TechDocService._lock_space(dto.space_id, connection)
            await TechDocService._validate_parent(dto.parent_id, dto.space_id, connection=connection)

            last = await TechDocModel.filter(
                space_id=dto.space_id,
                parent_id=dto.parent_id,
            ).using_db(connection).order_by("-sort").first()
            sort = (last.sort + 10) if last else 10

            doc = await TechDocModel.create(
                space_id=dto.space_id,
                title=dto.title,
                content=dto.content or "",
                source_url=dto.source_url,
                doc_type=dto.doc_type,
                version=dto.version,
                content_hash=content_hash,
                parent_id=dto.parent_id,
                sort=sort,
                using_db=connection,
            )

        await EmbeddingService.index_tech_doc(
            doc_id=str(doc.id),
            space_id=dto.space_id,
            title=dto.title,
            content=dto.content or "",
        )
        return doc

    @staticmethod
    async def get_by_id(doc_id: str) -> TechDocModel:
        doc = await TechDocModel.get_or_none(id=doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Tech doc not found")
        await TechDocService._sanitize_parent_links([doc])
        return doc

    @staticmethod
    async def get_by_space(
        space_id: str,
        query: Optional[str] = None,
        doc_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> dict:
        q = TechDocModel.filter(space_id=space_id)

        if doc_type:
            q = q.filter(doc_type=doc_type)
        if query:
            q = q.filter(Q(title__icontains=query) | Q(content__icontains=query))

        result = await paginate(q, page, page_size, sort_by="sort", sort_order="asc")
        await TechDocService._sanitize_parent_links(result["items"])
        return result

    @staticmethod
    async def get_tree(space_id: str) -> list[dict]:
        """Get wiki tree of tech docs for a space."""
        docs = await TechDocModel.filter(space_id=space_id).order_by("sort").all()

        doc_map = {}
        for d in docs:
            doc_map[str(d.id)] = {
                "id": str(d.id),
                "title": d.title,
                "doc_type": d.doc_type.value if hasattr(d.doc_type, "value") else d.doc_type,
                "parent_id": str(d.parent_id) if d.parent_id else None,
                "sort": d.sort,
                "children": [],
            }

        # A broken legacy cross-space parent is treated as a root. Do not expose
        # the foreign document ID in REST or MCP tree responses.
        for node in doc_map.values():
            if node["parent_id"] and node["parent_id"] not in doc_map:
                node["parent_id"] = None

        root = []
        for d_id, node in doc_map.items():
            pid = node["parent_id"]
            if pid and pid in doc_map:
                doc_map[pid]["children"].append(node)
            else:
                root.append(node)

        return root

    @staticmethod
    async def update(doc_id: str, dto: TechDocUpdateDto) -> TechDocModel:
        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}

        if "content" in data:
            data["content_hash"] = hashlib.sha256((data["content"] or "").encode()).hexdigest()

        data.pop("created_at", None)
        data.pop("updated_at", None)

        if "parent_id" in data:
            async with in_transaction() as connection:
                doc = await TechDocModel.filter(id=doc_id).using_db(connection).select_for_update().first()
                if not doc:
                    raise HTTPException(status_code=404, detail="Tech doc not found")
                await TechDocService._lock_space(str(doc.space_id), connection)
                await TechDocService._validate_parent(
                    data["parent_id"], str(doc.space_id), doc_id, connection
                )
                await TechDocModel.filter(id=doc_id).using_db(connection).update(**data)
        elif data:
            await TechDocModel.filter(id=doc_id).update(**data)

        updated = await TechDocService.get_by_id(doc_id)
        await EmbeddingService.index_tech_doc(
            doc_id=str(updated.id),
            space_id=str(updated.space_id),
            title=updated.title,
            content=updated.content or "",
        )
        return updated

    @staticmethod
    async def delete(doc_id: str) -> bool:
        async with in_transaction() as connection:
            doc = await TechDocModel.filter(id=doc_id).using_db(connection).select_for_update().first()
            if not doc:
                raise HTTPException(status_code=404, detail="Tech doc not found")
            await TechDocService._lock_space(str(doc.space_id), connection)
            children = await TechDocModel.filter(parent_id=doc_id).using_db(connection).count()
            if children > 0:
                raise HTTPException(status_code=400, detail="Cannot delete: page has subpages")
            await EmbeddingService.delete_embeddings("tech_doc", doc_id, connection=connection)
            await TechDocModel.filter(id=doc_id).using_db(connection).delete()
        return True

    @staticmethod
    async def reorder(doc_id: str, new_parent_id: Optional[str], new_sort: int) -> TechDocModel:
        async with in_transaction() as connection:
            doc = await TechDocModel.filter(id=doc_id).using_db(connection).select_for_update().first()
            if not doc:
                raise HTTPException(status_code=404, detail="Tech doc not found")
            await TechDocService._lock_space(str(doc.space_id), connection)
            await TechDocService._validate_parent(
                new_parent_id, str(doc.space_id), doc_id, connection
            )
            await TechDocModel.filter(id=doc_id).using_db(connection).update(
                parent_id=new_parent_id,
                sort=new_sort,
            )
        return await TechDocService.get_by_id(doc_id)
