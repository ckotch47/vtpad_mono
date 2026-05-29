from fastapi import HTTPException
from typing import Optional

from tortoise.expressions import Q
from tortoise.functions import Count

from .model import TestSuiteModel, TestSuiteStatus
from .dto import *
from ..common.crypto import get_user_id_by_token
from ..common.pagination import paginate


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
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> dict:
        filters = {'space_id': space_id}
        if status == 'archived':
            filters['status'] = TestSuiteStatus.archived
        elif status == 'all':
            pass
        else:
            filters['status'] = TestSuiteStatus.active

        q = TestSuiteModel.filter(**filters)
        if search:
            q = q.filter(Q(name__icontains=search) | Q(description__icontains=search))

        result = await paginate(q, page, page_size, sort_by, sort_order)
        items = result['items']
        suite_ids = [str(s.id) for s in items]

        # Count cases per suite
        from ..test_case.model import TestCaseModel
        case_counts = {}
        if suite_ids:
            case_rows = await TestCaseModel.filter(suite_id__in=suite_ids).group_by('suite_id').annotate(count=Count('id')).values('suite_id', 'count')
            case_counts = {str(r['suite_id']): r['count'] for r in case_rows}

        # Count sections per suite
        from ..section.model import SectionModel
        section_counts = {}
        if suite_ids:
            section_rows = await SectionModel.filter(suite_id__in=suite_ids).group_by('suite_id').annotate(count=Count('id')).values('suite_id', 'count')
            section_counts = {str(r['suite_id']): r['count'] for r in section_rows}

        return {
            **result,
            'items': [
                {
                    'id': str(s.id),
                    'name': s.name,
                    'description': s.description,
                    'status': s.status,
                    'sort': s.sort,
                    'space_id': str(s.space_id) if s.space_id else None,
                    'created_by_id': str(s.created_by_id) if s.created_by_id else None,
                    'created_at': s.created_at.isoformat() if s.created_at else None,
                    'updated_at': s.updated_at.isoformat() if s.updated_at else None,
                    'cases_count': case_counts.get(str(s.id), 0),
                    'sections_count': section_counts.get(str(s.id), 0),
                }
                for s in items
            ],
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
        data = {k: v for k, v in data.items() if v is not None}
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
