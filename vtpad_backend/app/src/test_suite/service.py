from fastapi import HTTPException
from typing import Optional

from tortoise.expressions import Q
from tortoise.functions import Count

from .model import TestSuiteModel, TestSuiteStatus
from .dto import *
from ..common.crypto import get_user_id_by_token


class TestSuiteService:
    @staticmethod
    async def create(dto: TestSuiteCreateDto, token: str) -> TestSuiteModel:
        user_id = await get_user_id_by_token(token)
        last = await TestSuiteModel.filter(space_id=dto.space_id).order_by('-sort').first()
        sort = (last.sort + 10) if last else 10
        return await TestSuiteModel.create(
            name=dto.name,
            description=dto.description,
            sort=sort,
            space_id=dto.space_id,
            created_by_id=user_id,
        )

    @staticmethod
    async def get_by_space(
        space_id: str,
        page: int = 1,
        page_size: int = 25,
        sort_by: Optional[str] = 'created_at',
        sort_order: Optional[str] = 'desc',
        search: Optional[str] = None
    ) -> dict:
        q = TestSuiteModel.filter(space_id=space_id, status=TestSuiteStatus.active).annotate(
            cases_count=Count('test_cases'),
            sections_count=Count('sections')
        )
        if search:
            q = q.filter(Q(name__icontains=search) | Q(description__icontains=search))

        order = f'{"-" if sort_order == "desc" else ""}{sort_by}'
        q = q.order_by(order)

        total = await q.count()
        items = await q.offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

    @staticmethod
    async def get_by_id(suite_id: str) -> TestSuiteModel:
        suite = await TestSuiteModel.get_or_none(id=suite_id)
        if not suite:
            raise HTTPException(status_code=404, detail="Test suite not found")
        return suite

    @staticmethod
    async def update(suite_id: str, dto: TestSuiteUpdateDto) -> TestSuiteModel:
        suite = await TestSuiteService.get_by_id(suite_id)
        data = dto.model_dump(exclude_unset=True)
        if data:
            await TestSuiteModel.filter(id=suite_id).update(**data)
        return await TestSuiteService.get_by_id(suite_id)

    @staticmethod
    async def delete(suite_id: str) -> bool:
        suite = await TestSuiteService.get_by_id(suite_id)
        await TestSuiteModel.filter(id=suite_id).update(status=TestSuiteStatus.archived)
        return True

    @staticmethod
    async def update_sort(suite_id: str, dto: TestSuiteSortDto) -> list[TestSuiteModel]:
        suite = await TestSuiteService.get_by_id(suite_id)
        space_id = str(suite.space_id)

        if dto.sort_before_id:
            before = await TestSuiteService.get_by_id(dto.sort_before_id)
            target = await TestSuiteService.get_by_id(suite_id)
            await TestSuiteModel.filter(id=dto.sort_before_id).update(sort=target.sort)
            await TestSuiteModel.filter(id=suite_id).update(sort=before.sort)

        if dto.sort_after_id:
            after = await TestSuiteService.get_by_id(dto.sort_after_id)
            target = await TestSuiteService.get_by_id(suite_id)
            await TestSuiteModel.filter(id=dto.sort_after_id).update(sort=target.sort)
            await TestSuiteModel.filter(id=suite_id).update(sort=after.sort)

        return await TestSuiteService.get_by_space(space_id)
