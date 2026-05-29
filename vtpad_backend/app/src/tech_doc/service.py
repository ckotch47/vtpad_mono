import hashlib
from datetime import timezone, datetime
from typing import Optional

from fastapi import HTTPException
from tortoise.expressions import Q

from .model import TechDocModel, TechDocType
from .dto import *
from ..embedding.service import EmbeddingService
from ..common.pagination import paginate


class TechDocService:
    @staticmethod
    async def create(dto: TechDocCreateDto) -> TechDocModel:
        content_hash = hashlib.sha256((dto.content or "").encode()).hexdigest()
        now = datetime.now(timezone.utc)

        # Compute sort
        last = await TechDocModel.filter(
            space_id=dto.space_id,
            parent_id=dto.parent_id
        ).order_by("-sort").first()
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

        return await paginate(q, page, page_size, sort_by="sort", sort_order="asc")

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
        doc = await TechDocService.get_by_id(doc_id)
        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}

        if "content" in data:
            data["content_hash"] = hashlib.sha256((data["content"] or "").encode()).hexdigest()

        data.pop("created_at", None)
        data.pop("updated_at", None)

        if data:
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
        doc = await TechDocService.get_by_id(doc_id)
        # Check children
        children = await TechDocModel.filter(parent_id=doc_id).count()
        if children > 0:
            raise HTTPException(status_code=400, detail="Cannot delete: page has subpages")
        await EmbeddingService.delete_embeddings("tech_doc", doc_id)
        await TechDocModel.filter(id=doc_id).delete()
        return True

    @staticmethod
    async def reorder(doc_id: str, new_parent_id: Optional[str], new_sort: int) -> TechDocModel:
        doc = await TechDocService.get_by_id(doc_id)
        await TechDocModel.filter(id=doc_id).update(parent_id=new_parent_id, sort=new_sort)
        return await TechDocService.get_by_id(doc_id)
