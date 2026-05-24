from fastapi import HTTPException
from typing import Optional

from tortoise.expressions import Q

from .model import TestPlanModel
from .dto import *
from ..common.crypto import get_user_id_by_token


class TestPlanService:
    @staticmethod
    async def create(dto: TestPlanCreateDto, token: str) -> TestPlanModel:
        user_id = await get_user_id_by_token(token)

        plan = await TestPlanModel.create(
            name=dto.name,
            description=dto.description,
            space_id=dto.space_id,
            suite_id=dto.suite_id,
            filters=dto.filters or {},
            created_by_id=user_id,
        )
        return plan

    @staticmethod
    async def get_by_space(
        space_id: str,
        page: int = 1,
        page_size: int = 25,
        sort_by: Optional[str] = 'created_at',
        sort_order: Optional[str] = 'desc',
        search: Optional[str] = None
    ) -> dict:
        q = TestPlanModel.filter(space_id=space_id).prefetch_related('suite')
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
    async def get_by_id(plan_id: str) -> TestPlanModel:
        plan = await TestPlanModel.get_or_none(id=plan_id).prefetch_related('suite', 'space')
        if not plan:
            raise HTTPException(status_code=404, detail="Test plan not found")
        return plan

    @staticmethod
    async def update(plan_id: str, dto: TestPlanUpdateDto) -> TestPlanModel:
        await TestPlanService.get_by_id(plan_id)
        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}
        if data:
            await TestPlanModel.filter(id=plan_id).update(**data)
        return await TestPlanService.get_by_id(plan_id)

    @staticmethod
    async def delete(plan_id: str) -> bool:
        await TestPlanService.get_by_id(plan_id)
        await TestPlanModel.filter(id=plan_id).delete()
        return True

    @staticmethod
    async def get_filtered_cases(plan_id: str) -> list:
        """Return test case IDs that match the plan's filters."""
        plan = await TestPlanService.get_by_id(plan_id)
        from ..test_case.model import TestCaseModel

        q = TestCaseModel.filter(space_id=str(plan.space_id))

        if plan.suite_id:
            q = q.filter(suite_id=str(plan.suite_id))

        filters = plan.filters or {}

        if filters.get('types'):
            q = q.filter(type__in=filters['types'])
        if filters.get('statuses'):
            q = q.filter(status__in=filters['statuses'])
        if filters.get('sections'):
            q = q.filter(section_id__in=filters['sections'])

        cases = await q.all()
        return cases
