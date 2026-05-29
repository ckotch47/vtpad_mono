from fastapi import HTTPException
from typing import Optional

from .model import SectionModel
from .dto import *
from ..common.crypto import get_user_id_by_token


class SectionService:
    @staticmethod
    async def create(dto: SectionCreateDto, token: str) -> SectionModel:
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
        await SectionService.get_by_id(section_id)
        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}
        if data:
            await SectionModel.filter(id=section_id).update(**data)
        return await SectionService.get_by_id(section_id)

    @staticmethod
    async def delete(section_id: str) -> bool:
        await SectionService.get_by_id(section_id)
        await SectionModel.filter(id=section_id).delete()
        return True

    @staticmethod
    async def update_sort(section_id: str, dto: SectionSortDto) -> list[SectionModel]:
        section = await SectionService.get_by_id(section_id)
        suite_id = str(section.suite_id)
        parent_id = section.parent_id

        if dto.sort_before_id:
            before = await SectionService.get_by_id(dto.sort_before_id)
            target = await SectionService.get_by_id(section_id)
            await SectionModel.filter(id=dto.sort_before_id).update(sort=target.sort)
            await SectionModel.filter(id=section_id).update(sort=before.sort)

        if dto.sort_after_id:
            after = await SectionService.get_by_id(dto.sort_after_id)
            target = await SectionService.get_by_id(section_id)
            await SectionModel.filter(id=dto.sort_after_id).update(sort=target.sort)
            await SectionModel.filter(id=section_id).update(sort=after.sort)

        return await SectionModel.filter(suite_id=suite_id, parent_id=parent_id).order_by('sort')
