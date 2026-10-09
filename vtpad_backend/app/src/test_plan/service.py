from fastapi import HTTPException
from typing import Optional

from tortoise.expressions import Q

from .model import TestPlanModel
from .dto import *
from ..common.crypto import get_user_id_by_token
from ..common.pagination import paginate


class TestPlanService:
    @staticmethod
    async def create(dto: TestPlanCreateDto, token: str) -> TestPlanModel:
        user_id = await get_user_id_by_token(token)

        plan = await TestPlanModel.create(
            name=dto.name,
            description=dto.description,
            space_id=dto.space_id,
            suite_ids=dto.suite_ids or [],
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

        result = await paginate(
            q.prefetch_related('created_by'), page, page_size, sort_by, sort_order
        )
        return {
            **result,
            'items': [
                {
                    'id': str(plan.id),
                    'name': plan.name,
                    'description': plan.description,
                    'suite_ids': plan.suite_ids or [],
                    'case_ids': plan.case_ids or [],
                    'space_id': str(plan.space_id),
                    'created_by_id': str(plan.created_by_id) if plan.created_by_id else None,
                    'created_by': {
                        'id': str(plan.created_by.id),
                        'username': plan.created_by.username,
                    } if plan.created_by else None,
                    'created_at': plan.created_at.isoformat() if plan.created_at else None,
                    'updated_at': plan.updated_at.isoformat() if plan.updated_at else None,
                }
                for plan in result['items']
            ],
        }

    @staticmethod
    async def get_by_id(plan_id: str, connection=None) -> TestPlanModel:
        query = TestPlanModel.filter(id=plan_id)
        if connection is not None:
            query = query.using_db(connection)
        plan = await query.prefetch_related('space').first()
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
    async def get_cases(plan_id: str, connection=None) -> list:
        """Return union of cases from suites and explicit case_ids."""
        plan = await TestPlanService.get_by_id(plan_id, connection)
        from ..test_case.model import TestCaseModel

        seen = set()
        ordered = []

        # Cases from suites
        suite_ids = plan.suite_ids or []
        if suite_ids:
            query = TestCaseModel.filter(
                suite_id__in=suite_ids, space_id=str(plan.space_id)
            )
            if connection is not None:
                query = query.using_db(connection)
            suite_cases = await query.prefetch_related('suite', 'section')
            for c in suite_cases:
                cid = str(c.id)
                if cid not in seen:
                    seen.add(cid)
                    ordered.append(c)

        # Explicit case_ids
        explicit_ids = plan.case_ids or []
        if explicit_ids:
            query = TestCaseModel.filter(
                id__in=explicit_ids, space_id=str(plan.space_id)
            )
            if connection is not None:
                query = query.using_db(connection)
            explicit_cases = await query.prefetch_related('suite', 'section')
            case_map = {str(c.id): c for c in explicit_cases}
            for cid in explicit_ids:
                if cid in case_map and cid not in seen:
                    seen.add(cid)
                    ordered.append(case_map[cid])

        return ordered
