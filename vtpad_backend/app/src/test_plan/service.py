import json
from uuid import UUID
from fastapi import HTTPException
from typing import Optional

from tortoise.expressions import Q
from tortoise import Tortoise
from tortoise.transactions import in_transaction

from .model import TestPlanModel
from .dto import *
from ..common.crypto import get_user_id_by_token
from ..common.pagination import paginate
from ..common.right_guard import check_user_into_space
from ..custom_field.model import CustomFieldEntityType, CustomFieldModel, CustomFieldType


class TestPlanService:
    @staticmethod
    def _validate_uuid_values(values: list[str], detail: str) -> None:
        try:
            for value in values:
                UUID(str(value))
        except (ValueError, TypeError, AttributeError) as exc:
            raise HTTPException(status_code=404, detail=detail) from exc

    @staticmethod
    async def _authorize(space_id: str, request, capability: str | None = None) -> None:
        await check_user_into_space(str(space_id), request, capability=capability)

    @staticmethod
    async def _validate_source_ids(space_id: str, suite_ids: list[str], case_ids: list[str]) -> None:
        from ..test_case.model import TestCaseModel
        from ..test_suite.model import TestSuiteModel

        suite_ids = list(dict.fromkeys(str(item) for item in suite_ids or []))
        case_ids = list(dict.fromkeys(str(item) for item in case_ids or []))
        TestPlanService._validate_uuid_values(suite_ids + case_ids, 'Plan source not found in space')
        suites = await TestSuiteModel.filter(id__in=suite_ids, space_id=space_id).count() if suite_ids else 0
        cases = await TestCaseModel.filter(id__in=case_ids, space_id=space_id).count() if case_ids else 0
        if suites != len(suite_ids) or cases != len(case_ids):
            raise HTTPException(status_code=404, detail='Plan source not found in space')

    @staticmethod
    async def _normalize_filters(filters, space_id: str, connection=None, lock_fields: bool = False) -> dict:
        from ..test_case.service import TestCaseService
        from ..custom_field.service import validate_value

        data = filters.model_dump() if hasattr(filters, 'model_dump') else (filters or {})
        if not isinstance(data, dict):
            raise HTTPException(status_code=422, detail='filters must be an object')
        priorities = data.get('priorities') or []
        if not isinstance(priorities, list) or any(
            not isinstance(priority, str) or priority not in {'P0', 'P1', 'P2', 'P3'}
            for priority in priorities
        ):
            raise HTTPException(status_code=422, detail='priority filters must be P0, P1, P2, or P3')
        priorities = list(dict.fromkeys(priorities))
        raw_tags = data.get('tags') or []
        if not isinstance(raw_tags, list):
            raise HTTPException(status_code=422, detail='tags must be a list')
        tags = TestCaseService._normalize_tags(raw_tags)
        custom_filters = data.get('custom_fields') or []
        if not isinstance(custom_filters, list) or any(not isinstance(item, dict) for item in custom_filters):
            raise HTTPException(status_code=422, detail='custom_fields must be a list of field/value objects')
        field_ids = [str(item.get('field_id') or '') for item in custom_filters]
        TestPlanService._validate_uuid_values(field_ids, 'Custom field is unavailable in this space')
        if len(set(field_ids)) != len(field_ids):
            raise HTTPException(status_code=422, detail='A custom field may only be filtered once')
        definitions_query = CustomFieldModel.filter(
            id__in=field_ids,
            space_id=space_id,
            entity_type=CustomFieldEntityType.testcase,
        )
        if connection is not None:
            definitions_query = definitions_query.using_db(connection)
        if lock_fields and field_ids:
            definitions_query = definitions_query.order_by('id').select_for_update()
        definitions = await definitions_query if field_ids else []
        by_id = {str(field.id): field for field in definitions}
        if len(by_id) != len(field_ids):
            raise HTTPException(status_code=422, detail='Custom field is unavailable in this space')
        normalized_custom = []
        for item in custom_filters:
            field_id = str(item.get('field_id'))
            field = by_id[field_id]
            value = item.get('value')
            if value is not None:
                value = validate_value(field, value, enforce_required=False)
            normalized_custom.append({'field_id': field_id, 'value': value})
        return {'priorities': priorities, 'tags': tags, 'custom_fields': normalized_custom}

    @staticmethod
    async def _selection_query(space_id: str, suite_ids: list[str], case_ids: list[str], filters: dict, connection=None):
        from ..test_case.model import TestCaseModel
        from ..test_case.service import TestCaseService

        query = TestCaseModel.filter(space_id=space_id)
        suite_ids = list(dict.fromkeys(str(item) for item in suite_ids or []))
        case_ids = list(dict.fromkeys(str(item) for item in case_ids or []))
        if suite_ids or case_ids:
            source_filter = Q(suite_id__in=suite_ids) if suite_ids else None
            if case_ids:
                source_filter = (source_filter | Q(id__in=case_ids)) if source_filter is not None else Q(id__in=case_ids)
            query = query.filter(source_filter)
        else:
            # An empty source set means an empty plan, not every case in the space.
            query = query.filter(id__in=[])
        priorities = filters.get('priorities') or []
        if priorities:
            query = query.filter(priority__in=priorities)
        tags = filters.get('tags') or []
        if tags:
            matching = await TestCaseService._filter_ids_by_all_tags(space_id, tags, connection)
            query = query.filter(id__in=list(matching or []))

        connection = connection or Tortoise.get_connection('default')
        query = query.using_db(connection)
        for item in filters.get('custom_fields') or []:
            field = await CustomFieldModel.filter(
                id=item['field_id'], space_id=space_id, entity_type=CustomFieldEntityType.testcase
            ).using_db(connection).first()
            if not field:
                raise HTTPException(status_code=422, detail='Custom field is unavailable in this space')
            value = item.get('value')
            params = [space_id, str(field.id)]
            if value is None:
                sql = (
                    'SELECT tc.id FROM test_case tc WHERE tc.space_id = $1 '
                    'AND NOT EXISTS (SELECT 1 FROM custom_field_value cfv '
                    'WHERE cfv.entity_id = tc.id AND cfv.field_id = $2 AND cfv.value IS NOT NULL)'
                )
            else:
                params.append(json.dumps(value, separators=(',', ':'), ensure_ascii=False))
                operator = (
                    '@>' if field.field_type == CustomFieldType.multiselect and value else '='
                )
                sql = (
                    'SELECT tc.id FROM test_case tc WHERE tc.space_id = $1 '
                    'AND EXISTS (SELECT 1 FROM custom_field_value cfv '
                    'WHERE cfv.entity_id = tc.id AND cfv.field_id = $2 '
                    f'AND cfv.value {operator} $3::jsonb)'
                )
            rows = await connection.execute_query_dict(sql, params)
            query = query.filter(id__in=[str(row['id']) for row in rows])
        return query.order_by('sort', 'id').prefetch_related('suite', 'section')

    @staticmethod
    async def _resolve_cases(space_id: str, suite_ids: list[str], case_ids: list[str], filters: dict, connection=None):
        query = await TestPlanService._selection_query(space_id, suite_ids, case_ids, filters, connection)
        return await query

    @staticmethod
    async def preview_selection(dto: TestPlanPreviewDto, request) -> dict:
        await TestPlanService._authorize(dto.space_id, request)
        await TestPlanService._validate_source_ids(dto.space_id, dto.suite_ids, dto.case_ids)
        filters = await TestPlanService._normalize_filters(dto.filters, dto.space_id)
        query = await TestPlanService._selection_query(dto.space_id, dto.suite_ids, dto.case_ids, filters)
        total = await query.count()
        cases = await query.limit(100)
        return {
            'total': total,
            'case_ids': [str(case.id) for case in cases[:100]],
            'truncated': total > 100,
        }

    @staticmethod
    async def create(dto: TestPlanCreateDto, token: str, request=None) -> TestPlanModel:
        if request is None:
            raise HTTPException(status_code=401, detail='not authenticated')
        await TestPlanService._authorize(dto.space_id, request, capability='plans')
        suite_ids = list(dict.fromkeys(dto.suite_ids or []))
        case_ids = list(dict.fromkeys(dto.case_ids or []))
        await TestPlanService._validate_source_ids(dto.space_id, suite_ids, case_ids)
        filters = await TestPlanService._normalize_filters(dto.filters, dto.space_id)
        user_id = await get_user_id_by_token(token)

        plan = await TestPlanModel.create(
            name=dto.name,
            description=dto.description,
            space_id=dto.space_id,
            suite_ids=suite_ids,
            case_ids=case_ids,
            filters=filters,
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
        search: Optional[str] = None,
        request=None,
    ) -> dict:
        if request is not None:
            await TestPlanService._authorize(str(space_id), request)
        q = TestPlanModel.filter(space_id=space_id)
        if search:
            q = q.filter(Q(name__icontains=search) | Q(description__icontains=search))

        result = await paginate(
            q.prefetch_related('created_by'), page, page_size, sort_by, sort_order
        )
        items = []
        for plan in result['items']:
            selection = await TestPlanService._selection_query(
                str(plan.space_id), plan.suite_ids or [], plan.case_ids or [], plan.filters or {}
            )
            items.append({
                'id': str(plan.id),
                'name': plan.name,
                'description': plan.description,
                'suite_ids': plan.suite_ids or [],
                'case_ids': plan.case_ids or [],
                'filters': plan.filters or {},
                'case_count': await selection.count(),
                'space_id': str(plan.space_id),
                'created_by_id': str(plan.created_by_id) if plan.created_by_id else None,
                'created_by': {
                    'id': str(plan.created_by.id),
                    'username': plan.created_by.username,
                } if plan.created_by else None,
                'created_at': plan.created_at.isoformat() if plan.created_at else None,
                'updated_at': plan.updated_at.isoformat() if plan.updated_at else None,
            })
        return {
            **result,
            'items': items,
        }

    @staticmethod
    async def get_by_id(plan_id: str, connection=None, request=None) -> TestPlanModel:
        query = TestPlanModel.filter(id=plan_id)
        if connection is not None:
            query = query.using_db(connection)
        plan = await query.prefetch_related('space').first()
        if not plan:
            raise HTTPException(status_code=404, detail="Test plan not found")
        if request is not None:
            await TestPlanService._authorize(str(plan.space_id), request)
        return plan

    @staticmethod
    async def update(plan_id: str, dto: TestPlanUpdateDto, request=None) -> TestPlanModel:
        plan = await TestPlanService.get_by_id(plan_id)
        if request is None:
            raise HTTPException(status_code=401, detail='not authenticated')
        await TestPlanService._authorize(str(plan.space_id), request, capability='plans')
        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}
        if 'suite_ids' in data:
            data['suite_ids'] = list(dict.fromkeys(data['suite_ids']))
        if 'case_ids' in data:
            data['case_ids'] = list(dict.fromkeys(data['case_ids']))
        if not data:
            return plan
        await TestPlanService._validate_source_ids(
            str(plan.space_id), data.get('suite_ids', plan.suite_ids or []), data.get('case_ids', plan.case_ids or [])
        )
        async with in_transaction() as connection:
            # Match field deletion's lock order (field rows before plan rows).
            # This prevents a concurrent delete from cleaning a filter and then
            # having a stale PATCH write the deleted field reference back.
            if 'filters' in data:
                data['filters'] = await TestPlanService._normalize_filters(
                    data['filters'], str(plan.space_id), connection, lock_fields=True
                )
            locked_plan = await TestPlanModel.filter(id=plan_id).using_db(connection).select_for_update().first()
            if not locked_plan:
                raise HTTPException(status_code=404, detail='Test plan not found')
            await TestPlanModel.filter(id=plan_id).using_db(connection).update(**data)
        return await TestPlanService.get_by_id(plan_id)

    @staticmethod
    async def delete(plan_id: str, request=None) -> bool:
        plan = await TestPlanService.get_by_id(plan_id)
        if request is None:
            raise HTTPException(status_code=401, detail='not authenticated')
        await TestPlanService._authorize(str(plan.space_id), request, capability='plans')
        await TestPlanModel.filter(id=plan_id).delete()
        return True

    @staticmethod
    async def get_cases(plan_id: str, connection=None, request=None) -> list:
        """Return union of cases from suites and explicit case_ids."""
        plan = await TestPlanService.get_by_id(plan_id, connection, request)
        return await TestPlanService._resolve_cases(
            str(plan.space_id), plan.suite_ids or [], plan.case_ids or [], plan.filters or {}, connection
        )

    @staticmethod
    async def count_cases(plan_id: str, connection=None) -> int:
        plan = await TestPlanService.get_by_id(plan_id, connection)
        query = await TestPlanService._selection_query(
            str(plan.space_id), plan.suite_ids or [], plan.case_ids or [], plan.filters or {}, connection
        )
        return await query.count()
