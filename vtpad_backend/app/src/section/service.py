from fastapi import HTTPException
from typing import Optional
from starlette.requests import Request
from tortoise.transactions import in_transaction

from .model import SectionModel
from .dto import *
from ..common.crypto import get_user_id_by_token
from ..common.right_guard import check_user_into_space
from ..test_suite.model import TestSuiteModel


class SectionService:
    @staticmethod
    async def create(dto: SectionCreateDto, token: str) -> SectionModel:
        suite = await TestSuiteModel.get_or_none(id=dto.suite_id)
        if not suite:
            raise HTTPException(status_code=404, detail="Test suite not found")
        if dto.parent_id:
            parent = await SectionModel.get_or_none(id=dto.parent_id)
            if not parent or str(parent.suite_id) != str(suite.id):
                raise HTTPException(status_code=404, detail="Parent section not found")
        user_id = await get_user_id_by_token(token)
        last = await SectionModel.filter(suite_id=dto.suite_id, parent_id=dto.parent_id).order_by('-sort').first()
        sort = (last.sort + 10) if last else 10
        return await SectionModel.create(
            name=dto.name,
            description=dto.description,
            sort=sort,
            suite_id=dto.suite_id,
            parent_id=dto.parent_id,
            created_by_id=user_id,
        )

    @staticmethod
    async def get_by_suite(suite_id: str) -> list[dict]:
        sections = await SectionModel.filter(suite_id=suite_id).order_by('sort')
        return [
            {
                'id': str(s.id),
                'name': s.name,
                'description': s.description,
                'sort': s.sort,
                'parent_id': str(s.parent_id) if s.parent_id else None,
                'suite_id': str(s.suite_id),
                'created_at': s.created_at.isoformat() if s.created_at else None,
            }
            for s in sections
        ]

    @staticmethod
    async def get_tree(suite_id: str) -> list[dict]:
        from ..test_case.model import TestCaseModel
        sections = await SectionModel.filter(suite_id=suite_id).order_by('sort')
        section_map = {}
        for s in sections:
            sid = str(s.id)
            tc_count = await TestCaseModel.filter(section_id=sid).count()
            section_map[sid] = {
                'id': sid,
                'name': s.name,
                'description': s.description,
                'sort': s.sort,
                'parent_id': str(s.parent_id) if s.parent_id else None,
                'suite_id': str(s.suite_id),
                'children': [],
                'test_case_count': tc_count,
                'created_at': s.created_at.isoformat() if s.created_at else None,
            }

        roots = []
        for s in sections:
            sid = str(s.id)
            if s.parent_id and str(s.parent_id) in section_map:
                section_map[str(s.parent_id)]['children'].append(section_map[sid])
            else:
                roots.append(section_map[sid])

        return roots

    @staticmethod
    async def get_by_id(section_id: str) -> SectionModel:
        section = await SectionModel.get_or_none(id=section_id)
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        return section

    @staticmethod
    async def update(section_id: str, dto: SectionUpdateDto) -> SectionModel:
        section = await SectionService.get_by_id(section_id)
        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}
        if data.get("parent_id"):
            parent = await SectionModel.get_or_none(id=data["parent_id"])
            if not parent or str(parent.suite_id) != str(section.suite_id):
                raise HTTPException(status_code=404, detail="Parent section not found")
        if data:
            await SectionModel.filter(id=section_id).update(**data)
        return await SectionService.get_by_id(section_id)

    @staticmethod
    async def delete(section_id: str) -> bool:
        await SectionService.get_by_id(section_id)
        await SectionModel.filter(id=section_id).delete()
        return True

    @staticmethod
    async def update_sort(
        section_id: str,
        dto: SectionSortDto,
        request: Request,
    ) -> list[SectionModel]:
        neighbor_id = dto.sort_before_id or dto.sort_after_id
        if neighbor_id == section_id:
            raise HTTPException(status_code=422, detail='A section cannot be sorted relative to itself')

        section = await SectionService.get_by_id(section_id)
        suite_id = str(section.suite_id)
        suite = await TestSuiteModel.get_or_none(id=suite_id)
        if not suite:
            raise HTTPException(status_code=404, detail='Test suite not found')
        await check_user_into_space(str(suite.space_id), request, capability="sections")

        async with in_transaction() as connection:
            # Lock the suite row as a serialization point for all reorder requests
            # within this suite, then lock its existing sections before computing
            # and writing a complete sibling order.
            locked_suite = await TestSuiteModel.filter(id=suite_id).using_db(connection).select_for_update().first()
            if not locked_suite:
                raise HTTPException(status_code=404, detail='Test suite not found')

            siblings = await SectionModel.filter(
                suite_id=suite_id,
                parent_id=section.parent_id,
            ).using_db(connection).order_by('sort', 'id').select_for_update()
            by_id = {str(item.id): item for item in siblings}
            target = by_id.get(section_id)
            neighbor = by_id.get(neighbor_id)
            if not target:
                raise HTTPException(status_code=404, detail='Section not found in test suite')
            if not neighbor:
                raise HTTPException(
                    status_code=422,
                    detail='The neighbor must be a section in the same suite and parent',
                )

            ordered = [item for item in siblings if str(item.id) != section_id]
            neighbor_index = next(index for index, item in enumerate(ordered) if str(item.id) == neighbor_id)
            insert_at = neighbor_index if dto.sort_before_id else neighbor_index + 1
            ordered.insert(insert_at, target)

            for index, item in enumerate(ordered, start=1):
                await SectionModel.filter(id=item.id).using_db(connection).update(sort=index * 10)

            return await SectionModel.filter(
                suite_id=suite_id,
                parent_id=section.parent_id,
            ).using_db(connection).order_by('sort', 'id')
