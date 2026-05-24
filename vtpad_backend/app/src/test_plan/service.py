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
            case_ids=dto.case_ids or [],
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
        q = TestPlanModel.filter(space_id=space_id)
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
        plan = await TestPlanModel.get_or_none(id=plan_id).prefetch_related('space')
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
    async def get_cases(plan_id: str) -> list:
        """Return test cases in the plan's fixed case_ids list."""
        plan = await TestPlanService.get_by_id(plan_id)
        from ..test_case.model import TestCaseModel

        case_ids = plan.case_ids or []
        if not case_ids:
            return []

        cases = await TestCaseModel.filter(id__in=case_ids).all()
        # Preserve order from case_ids
        case_map = {str(c.id): c for c in cases}
        ordered = []
        for cid in case_ids:
            if cid in case_map:
                ordered.append(case_map[cid])
        return ordered
