from fastapi import HTTPException
from typing import Optional
from tortoise import Tortoise

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
        normalized_search = search.strip() if isinstance(search, str) else ''
        filters = {'space_id': space_id}
        if status == 'archived':
            filters['status'] = TestSuiteStatus.archived
        elif status == 'all':
            pass
        else:
            filters['status'] = TestSuiteStatus.active

        if normalized_search:
            params = [space_id, normalized_search]
            conditions = [
                'test_suite.space_id = $1',
                "test_suite.search_vector @@ websearch_to_tsquery('simple', $2)",
            ]
            if status != 'all':
                suite_status = (
                    TestSuiteStatus.archived if status == 'archived'
                    else TestSuiteStatus.active
                )
                params.append(suite_status.value)
                conditions.append(f'test_suite.status = ${len(params)}')
            where_sql = ' AND '.join(conditions)
            connection = Tortoise.get_connection('default')
            count_rows = await connection.execute_query_dict(
                f'SELECT count(*) AS total FROM test_suite WHERE {where_sql}', params
            )
            total = count_rows[0]['total']
            page_params = [*params, page_size, (page - 1) * page_size]
            rows = await connection.execute_query_dict(
                "SELECT test_suite.id, ts_rank(test_suite.search_vector, "
                "websearch_to_tsquery('simple', $2)) AS rank "
                f'FROM test_suite WHERE {where_sql} '
                f'ORDER BY rank DESC, test_suite.id ASC LIMIT ${len(params) + 1} '
                f'OFFSET ${len(params) + 2}',
                page_params,
            )
            suite_ids = [str(row['id']) for row in rows]
            suites = await TestSuiteModel.filter(id__in=suite_ids).prefetch_related(
                'created_by'
            ) if suite_ids else []
            suites_by_id = {str(suite.id): suite for suite in suites}
            items = [suites_by_id[suite_id] for suite_id in suite_ids if suite_id in suites_by_id]
            result = {
                'items': items,
                'total': total,
                'page': page,
                'page_size': page_size,
                'pages': (total + page_size - 1) // page_size,
            }
        else:
            q = TestSuiteModel.filter(**filters)
            result = await paginate(
                q.prefetch_related('created_by'), page, page_size, sort_by, sort_order
            )
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
                    'created_by': {
                        'id': str(s.created_by.id),
                        'username': s.created_by.username,
                    } if s.created_by else None,
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
            if str(before.space_id) != str(target.space_id):
                raise HTTPException(status_code=422, detail="Suites must be reordered within the same space")
            await TestSuiteModel.filter(id=dto.sort_before_id).update(sort=target.sort)
            await TestSuiteModel.filter(id=suite_id).update(sort=before.sort)

        if dto.sort_after_id:
            after = await TestSuiteService.get_by_id(dto.sort_after_id)
            target = await TestSuiteService.get_by_id(suite_id)
            if str(after.space_id) != str(target.space_id):
                raise HTTPException(status_code=422, detail="Suites must be reordered within the same space")
            await TestSuiteModel.filter(id=dto.sort_after_id).update(sort=target.sort)
            await TestSuiteModel.filter(id=suite_id).update(sort=after.sort)

        return await TestSuiteService.get_by_space(space_id)
