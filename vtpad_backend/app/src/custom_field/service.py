import math
from datetime import date
from typing import Any

from fastapi import HTTPException
from tortoise.transactions import in_transaction

from .model import CustomFieldEntityType, CustomFieldModel, CustomFieldType, CustomFieldValueModel
from .dto import CustomFieldCreateDto, CustomFieldUpdateDto
from ..common.crypto import get_user_id_by_token
from ..common.right_guard import check_user_into_space


def _field_options(field_type: CustomFieldType | str, options: Any) -> list[str]:
    value = field_type.value if hasattr(field_type, 'value') else field_type
    if value not in ('select', 'multiselect'):
        return []
    if not isinstance(options, list) or any(not isinstance(item, str) or not item.strip() for item in options):
        raise HTTPException(status_code=422, detail='select fields require a list of non-empty string options')
    normalized = [item.strip() for item in options]
    if not normalized:
        raise HTTPException(status_code=422, detail='select fields require at least one option')
    if len(set(normalized)) != len(normalized):
        raise HTTPException(status_code=422, detail='select options must be unique')
    return normalized


def validate_value(field: CustomFieldModel, value: Any, *, enforce_required: bool = True) -> Any:
    """Validate and normalize a JSON custom-field value against its definition."""
    field_type = field.field_type.value if hasattr(field.field_type, 'value') else field.field_type
    options = _field_options(field_type, field.options or [])
    if value is None:
        if enforce_required and field.required:
            raise HTTPException(status_code=422, detail=f'{field.name} is required')
        return None

    if field_type == 'text':
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail=f'{field.name} must be text')
        normalized = value
        empty = not normalized.strip()
    elif field_type == 'number':
        if isinstance(value, bool) or not isinstance(value, (int, float)) or (isinstance(value, float) and not math.isfinite(value)):
            raise HTTPException(status_code=422, detail=f'{field.name} must be a finite number')
        normalized = value
        empty = False
    elif field_type == 'date':
        if not isinstance(value, str):
            raise HTTPException(status_code=422, detail=f'{field.name} must be an ISO date')
        try:
            normalized = date.fromisoformat(value).isoformat()
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f'{field.name} must be an ISO date') from exc
        empty = False
    elif field_type == 'checkbox':
        if not isinstance(value, bool):
            raise HTTPException(status_code=422, detail=f'{field.name} must be true or false')
        normalized = value
        empty = False
    elif field_type == 'select':
        if not isinstance(value, str) or value not in options:
            raise HTTPException(status_code=422, detail=f'{field.name} must match one of its options')
        normalized = value
        empty = False
    elif field_type == 'multiselect':
        if not isinstance(value, list) or any(not isinstance(item, str) or item not in options for item in value):
            raise HTTPException(status_code=422, detail=f'{field.name} must contain only its options')
        if len(set(value)) != len(value):
            raise HTTPException(status_code=422, detail=f'{field.name} options must not repeat')
        normalized = value
        empty = not normalized
    else:
        raise HTTPException(status_code=422, detail='Unsupported custom field type')

    if enforce_required and field.required and empty:
        raise HTTPException(status_code=422, detail=f'{field.name} is required')
    return normalized


class CustomFieldService:
    @staticmethod
    async def _authorize(space_id: str, request, capability: str | None = None) -> None:
        await check_user_into_space(str(space_id), request, capability=capability)

    @staticmethod
    async def create(dto: CustomFieldCreateDto, token: str, request) -> CustomFieldModel:
        capability = "runs" if dto.entity_type == CustomFieldEntityType.testrun else "cases"
        await CustomFieldService._authorize(dto.space_id, request, capability)
        if dto.entity_type == CustomFieldEntityType.testrun and dto.required:
            raise HTTPException(status_code=422, detail='Required custom fields currently support test cases only')
        options = _field_options(dto.field_type, dto.options or [])
        name = dto.name.strip()
        if not name:
            raise HTTPException(status_code=422, detail='Custom field name is required')
        user_id = await get_user_id_by_token(token)
        if dto.required and dto.entity_type == CustomFieldEntityType.testcase:
            # Serialize with testcase creation so a concurrent case cannot
            # read the definitions before this required field is inserted.
            from ..space.model import SpaceModel
            from ..test_case.model import TestCaseModel

            async with in_transaction() as connection:
                space = await SpaceModel.filter(id=dto.space_id).using_db(connection).select_for_update().first()
                if not space:
                    raise HTTPException(status_code=404, detail='Space not found')
                if await TestCaseModel.filter(space_id=dto.space_id).using_db(connection).exists():
                    raise HTTPException(
                        status_code=422,
                        detail='Create this field as optional, populate every existing test case, then make it required',
                    )
                return await CustomFieldModel.create(
                    name=name,
                    field_type=dto.field_type,
                    entity_type=dto.entity_type,
                    options=options,
                    required=True,
                    sort=dto.sort,
                    space_id=dto.space_id,
                    created_by_id=user_id,
                    using_db=connection,
                )
        return await CustomFieldModel.create(
            name=name,
            field_type=dto.field_type,
            entity_type=dto.entity_type,
            options=options,
            required=dto.required,
            sort=dto.sort,
            space_id=dto.space_id,
            created_by_id=user_id,
        )

    @staticmethod
    async def get_by_space(space_id: str, entity_type: str = None, request=None) -> list[CustomFieldModel]:
        await CustomFieldService._authorize(space_id, request)
        q = CustomFieldModel.filter(space_id=space_id)
        if entity_type:
            q = q.filter(entity_type=entity_type)
        return await q.order_by('sort', 'name')

    @staticmethod
    async def get_by_id(field_id: str, request=None) -> CustomFieldModel:
        field = await CustomFieldModel.get_or_none(id=field_id)
        if not field:
            raise HTTPException(status_code=404, detail='Custom field not found')
        if request is not None:
            await CustomFieldService._authorize(str(field.space_id), request)
        return field

    @staticmethod
    async def update(field_id: str, dto: CustomFieldUpdateDto, request) -> CustomFieldModel:
        async with in_transaction() as connection:
            # Resolve the space first, then lock space -> field consistently
            # with testcase creation and required-field mutations.
            field_ref = await CustomFieldModel.filter(id=field_id).using_db(connection).first()
            if not field_ref:
                raise HTTPException(status_code=404, detail='Custom field not found')
            from ..space.model import SpaceModel
            space = await SpaceModel.filter(id=field_ref.space_id).using_db(connection).select_for_update().first()
            if not space:
                raise HTTPException(status_code=404, detail='Custom field not found')
            field = await CustomFieldModel.filter(id=field_id).using_db(connection).select_for_update().first()
            if not field:
                raise HTTPException(status_code=404, detail='Custom field not found')
            capability = "runs" if field.entity_type == CustomFieldEntityType.testrun else "cases"
            await CustomFieldService._authorize(str(field.space_id), request, capability)

            # Preserve the established PATCH contract: omitted and explicit
            # null fields are ignored; nullable values are only accepted by
            # DTOs whose domain operation explicitly supports clearing them.
            data = {
                key: value
                for key, value in dto.model_dump(exclude_unset=True).items()
                if value is not None
            }
            if data.get('name') is not None:
                data['name'] = data['name'].strip()
                if not data['name']:
                    raise HTTPException(status_code=422, detail='Custom field name is required')
            next_type = data.get('field_type', field.field_type)
            next_options = data.get('options', field.options or [])
            if 'options' in data or 'field_type' in data:
                next_options = _field_options(next_type, next_options)
            else:
                # Allow unrelated edits to legacy select definitions that
                # predate option validation; they can be repaired by adding
                # options without rewriting historical snapshots.
                next_options = list(field.options or [])
            if field.entity_type == CustomFieldEntityType.testrun and data.get('required') is True:
                raise HTTPException(status_code=422, detail='Required custom fields currently support test cases only')
            if 'options' in data or 'field_type' in data:
                data['options'] = next_options

            values = CustomFieldValueModel.filter(field_id=field_id).using_db(connection)
            saved_values = await values
            for saved_value in saved_values:
                candidate = CustomFieldModel(
                    id=field.id,
                    name=data.get('name', field.name),
                    field_type=next_type,
                    entity_type=field.entity_type,
                    options=next_options,
                    required=data.get('required', field.required),
                    sort=data.get('sort', field.sort),
                    space_id=field.space_id,
                )
                validate_value(candidate, saved_value.value)

            if data.get('required') is True and not field.required and field.entity_type == CustomFieldEntityType.testcase:
                from ..test_case.model import TestCaseModel

                case_ids = await TestCaseModel.filter(space_id=field.space_id).using_db(connection).values_list('id', flat=True)
                populated = {str(row.entity_id) for row in saved_values}
                if any(str(case_id) not in populated for case_id in case_ids):
                    raise HTTPException(
                        status_code=422,
                        detail='Populate this field for every existing test case before making it required',
                    )

            if data:
                await CustomFieldModel.filter(id=field_id).using_db(connection).update(**data)
        return await CustomFieldService.get_by_id(field_id, request)

    @staticmethod
    async def delete(field_id: str, request) -> bool:
        async with in_transaction() as connection:
            field = await CustomFieldModel.filter(id=field_id).using_db(connection).select_for_update().first()
            if not field:
                raise HTTPException(status_code=404, detail='Custom field not found')
            capability = "runs" if field.entity_type == CustomFieldEntityType.testrun else "cases"
            await CustomFieldService._authorize(str(field.space_id), request, capability)
            # Remove dependent plan predicates atomically with the definition;
            # otherwise plan counts, previews, and run creation would retain
            # filters that can no longer be resolved.
            await connection.execute_query(
                "UPDATE test_plan SET filters = jsonb_set("
                "COALESCE(filters, '{}'::jsonb), '{custom_fields}', "
                "COALESCE((SELECT jsonb_agg(item) FROM jsonb_array_elements("
                "COALESCE(filters->'custom_fields', '[]'::jsonb)) AS entries(item) "
                "WHERE item->>'field_id' <> $1::text), '[]'::jsonb), true) "
                "WHERE space_id = $2 AND COALESCE(filters->'custom_fields', '[]'::jsonb) "
                "@> jsonb_build_array(jsonb_build_object('field_id', $1::text))",
                [str(field.id), str(field.space_id)],
            )
            await CustomFieldValueModel.filter(field_id=field_id).using_db(connection).delete()
            await CustomFieldModel.filter(id=field_id).using_db(connection).delete()
        return True


class CustomFieldValueService:
    @staticmethod
    async def _resolve_entity(entity_type: CustomFieldEntityType | str, entity_id: str, connection=None):
        entity_type = entity_type.value if hasattr(entity_type, 'value') else entity_type
        if entity_type == 'testcase':
            from ..test_case.model import TestCaseModel
            entity = await TestCaseModel.filter(id=entity_id).using_db(connection).first() if connection else await TestCaseModel.get_or_none(id=entity_id)
        elif entity_type == 'testrun':
            from ..test_run.model import TestRunModel
            entity = await TestRunModel.filter(id=entity_id).using_db(connection).first() if connection else await TestRunModel.get_or_none(id=entity_id)
        else:
            raise HTTPException(status_code=422, detail='Unsupported custom field entity type')
        if not entity:
            raise HTTPException(status_code=404, detail='Custom field entity not found')
        return entity

    @staticmethod
    async def set_value(dto, request, token: str | None = None) -> CustomFieldValueModel:
        async with in_transaction() as connection:
            # Read the field first to resolve its entity, but acquire row locks
            # in entity -> field order. TestCaseService.update already holds
            # the testcase row before locking custom-field definitions; keeping
            # the same order avoids a field/case deadlock on concurrent edits.
            field = await CustomFieldModel.filter(id=dto.field_id).using_db(connection).first()
            if not field:
                raise HTTPException(status_code=404, detail='Custom field not found')
            entity = await CustomFieldValueService._resolve_entity(field.entity_type, dto.entity_id, connection)
            if str(entity.space_id) != str(field.space_id):
                raise HTTPException(status_code=404, detail='Custom field entity not found')
            capability = "runs" if field.entity_type == CustomFieldEntityType.testrun else "cases"
            await CustomFieldService._authorize(str(field.space_id), request, capability)
            if field.entity_type == CustomFieldEntityType.testcase:
                from ..test_case.model import TestCaseModel
                entity = await TestCaseModel.filter(id=dto.entity_id).using_db(connection).select_for_update().first()
                if not entity:
                    raise HTTPException(status_code=404, detail='Custom field entity not found')
            field = await CustomFieldModel.filter(id=dto.field_id).using_db(connection).select_for_update().first()
            if not field or str(field.space_id) != str(entity.space_id):
                raise HTTPException(status_code=404, detail='Custom field not found')
            value = validate_value(field, dto.value)
            existing = await CustomFieldValueModel.filter(
                field_id=dto.field_id, entity_id=dto.entity_id
            ).using_db(connection).first()
            if existing:
                if existing.value == value:
                    return existing
                await CustomFieldValueModel.filter(id=existing.id).using_db(connection).update(value=value)
                existing.value = value
                saved = existing
            else:
                saved = await CustomFieldValueModel.create(
                    field_id=dto.field_id,
                    entity_id=dto.entity_id,
                    value=value,
                    using_db=connection,
                )
            if field.entity_type == CustomFieldEntityType.testcase:
                from ..test_case.service import TestCaseService
                case = await CustomFieldValueService._resolve_entity('testcase', dto.entity_id, connection)
                user_id = await get_user_id_by_token(token) if token else None
                await TestCaseService._create_test_case_version(case, user_id, next_version=True, connection=connection)
        return saved

    @staticmethod
    async def get_snapshot_values(space_id: str, entity_ids: list[str], connection=None) -> dict[str, list[dict]]:
        result = {str(entity_id): [] for entity_id in entity_ids}
        if not entity_ids:
            return result
        definitions_query = CustomFieldModel.filter(
            space_id=space_id, entity_type=CustomFieldEntityType.testcase
        ).order_by('sort', 'name', 'id')
        if connection is not None:
            definitions_query = definitions_query.using_db(connection)
        definitions = await definitions_query
        if not definitions:
            return result
        values_query = CustomFieldValueModel.filter(
            field_id__in=[field.id for field in definitions], entity_id__in=entity_ids
        )
        if connection is not None:
            values_query = values_query.using_db(connection)
        values = await values_query
        value_map = {(str(item.entity_id), str(item.field_id)): item.value for item in values}
        for entity_id in result:
            result[entity_id] = [
                {
                    'field_id': str(field.id),
                    'name': field.name,
                    'field_type': field.field_type.value if hasattr(field.field_type, 'value') else field.field_type,
                    'options': list(field.options or []),
                    'required': bool(field.required),
                    'value': value_map.get((entity_id, str(field.id))),
                }
                for field in definitions
            ]
        return result

    @staticmethod
    async def replace_case_values(testcase, values: list[dict] | None, connection) -> None:
        definitions = await CustomFieldModel.filter(
            space_id=testcase.space_id,
            entity_type=CustomFieldEntityType.testcase,
        ).using_db(connection).select_for_update().order_by('sort', 'name', 'id')
        definitions_by_id = {str(field.id): field for field in definitions}
        supplied: dict[str, Any] = {}
        for item in values or []:
            field_id = str(item.get('field_id') or '')
            if field_id in supplied:
                raise HTTPException(status_code=422, detail='A custom field may only be provided once')
            field = definitions_by_id.get(field_id)
            if not field:
                raise HTTPException(status_code=422, detail='Custom field is unavailable in this space')
            supplied[field_id] = validate_value(field, item.get('value'))

        for field in definitions:
            if field.required and str(field.id) not in supplied:
                raise HTTPException(status_code=422, detail=f'{field.name} is required')

        existing_values = CustomFieldValueModel.filter(
            entity_id=testcase.id, field_id__in=[field.id for field in definitions]
        ).using_db(connection)
        for existing in await existing_values:
            if str(existing.field_id) not in supplied:
                await CustomFieldValueModel.filter(id=existing.id).using_db(connection).delete()

        for field in definitions:
            field_id = str(field.id)
            if field_id not in supplied:
                continue
            existing = await CustomFieldValueModel.filter(
                field_id=field_id, entity_id=testcase.id
            ).using_db(connection).first()
            if supplied[field_id] is None:
                if existing:
                    await CustomFieldValueModel.filter(id=existing.id).using_db(connection).delete()
            elif existing:
                await CustomFieldValueModel.filter(id=existing.id).using_db(connection).update(value=supplied[field_id])
            else:
                await CustomFieldValueModel.create(
                    field_id=field_id,
                    entity_id=testcase.id,
                    value=supplied[field_id],
                    using_db=connection,
                )

    @staticmethod
    async def restore_case_values(testcase, snapshot: list[dict] | None, connection) -> None:
        if snapshot is None:
            return
        definitions = await CustomFieldModel.filter(
            space_id=testcase.space_id,
            entity_type=CustomFieldEntityType.testcase,
        ).using_db(connection).select_for_update().order_by('sort', 'name', 'id')
        by_id = {str(field.id): field for field in definitions}
        for saved in snapshot:
            field = by_id.get(str(saved.get('field_id')))
            if not field or field.field_type.value != saved.get('field_type'):
                continue
            try:
                value = validate_value(field, saved.get('value'), enforce_required=False)
            except HTTPException:
                continue
            if field.required and (value is None or (isinstance(value, str) and not value.strip()) or value == []):
                # A field made required after the historical version must not
                # be cleared by restoring that older version.
                continue
            existing = await CustomFieldValueModel.filter(
                field_id=field.id, entity_id=testcase.id
            ).using_db(connection).first()
            if existing:
                await CustomFieldValueModel.filter(id=existing.id).using_db(connection).update(value=value)
            elif value is not None:
                await CustomFieldValueModel.create(
                    field_id=field.id, entity_id=testcase.id, value=value, using_db=connection
                )

    @staticmethod
    async def get_values(entity_id: str, request) -> list[dict]:
        values = await CustomFieldValueModel.filter(entity_id=entity_id).prefetch_related('field')
        if values:
            entity = await CustomFieldValueService._resolve_entity(values[0].field.entity_type, entity_id)
            await CustomFieldService._authorize(str(entity.space_id), request)
            if any(str(value.field.space_id) != str(entity.space_id) for value in values):
                raise HTTPException(status_code=404, detail='Custom field entity not found')
        else:
            entity = None
            for entity_type in ('testcase', 'testrun'):
                try:
                    entity = await CustomFieldValueService._resolve_entity(entity_type, entity_id)
                    break
                except HTTPException as exc:
                    if exc.status_code != 404:
                        raise
            if not entity:
                raise HTTPException(status_code=404, detail='Custom field entity not found')
            await CustomFieldService._authorize(str(entity.space_id), request)
        return values
