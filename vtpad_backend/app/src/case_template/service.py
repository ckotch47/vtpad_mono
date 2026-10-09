import math
import uuid

from fastapi import HTTPException
from tortoise import Tortoise
from tortoise.exceptions import IntegrityError
from tortoise.functions import Count, Max
from tortoise.transactions import in_transaction

from ..space.model import SpaceModel
from ..test_case.dto import TestCaseCreateDto
from ..test_case.model import TestCaseModel
from ..test_case.service import TestCaseService
from ..test_suite.model import TestSuiteModel
from ..section.model import SectionModel
from .dto import (
    MAX_TEMPLATE_VERSIONS,
    CaseTemplateCreateDto,
    CaseTemplateFieldsDto,
    CaseTemplateUseDto,
    CaseTemplateUpdateDto,
)
from .model import TestCaseTemplateModel, TestCaseTemplateVersionModel

MAX_PAGE_SIZE = 100


def _uuid(value: str | uuid.UUID, label: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f'Invalid {label}') from exc


def _normalize_name(value: str) -> str:
    return ' '.join(value.split()).casefold()


def _iso(value):
    return value.isoformat() if value else None


def _version_dict(version: TestCaseTemplateVersionModel, include_fields: bool = False) -> dict:
    result = {
        'id': str(version.id),
        'version_number': version.version_number,
        'created_by_id': str(version.created_by_id) if version.created_by_id else None,
        'created_at': _iso(version.created_at),
    }
    if include_fields:
        result['fields'] = version.content
    return result


class TestCaseTemplateService:
    @staticmethod
    async def _get_template(space_id: str, template_id: str, connection=None) -> TestCaseTemplateModel:
        conn = connection or Tortoise.get_connection('default')
        template = await TestCaseTemplateModel.filter(
            id=_uuid(template_id, 'template ID'), space_id=_uuid(space_id, 'space ID')
        ).using_db(conn).first()
        if not template:
            raise HTTPException(status_code=404, detail='Case template not found')
        return template

    @staticmethod
    async def _latest_version(template_id: uuid.UUID, connection=None):
        query = TestCaseTemplateVersionModel.filter(template_id=template_id)
        if connection is not None:
            query = query.using_db(connection)
        return await query.order_by('-version_number').first()

    @staticmethod
    async def list_templates(space_id: str, page: int = 1, page_size: int = 50) -> dict:
        if page < 1 or page_size < 1 or page_size > MAX_PAGE_SIZE:
            raise HTTPException(status_code=422, detail='Invalid template pagination')
        space_uuid = _uuid(space_id, 'space ID')
        if not await SpaceModel.filter(id=space_uuid).exists():
            raise HTTPException(status_code=404, detail='Space not found')
        query = TestCaseTemplateModel.filter(space_id=space_uuid).order_by('name', 'id')
        total = await query.count()
        templates = await query.offset((page - 1) * page_size).limit(page_size)
        if not templates:
            return {'items': [], 'total': total, 'page': page, 'page_size': page_size, 'pages': math.ceil(total / page_size)}
        version_stats = await TestCaseTemplateVersionModel.filter(
            template_id__in=[template.id for template in templates]
        ).annotate(
            version_count=Count('id'), latest_version=Max('version_number')
        ).group_by('template_id').values('template_id', 'version_count', 'latest_version')
        stats_by_template = {str(row['template_id']): row for row in version_stats}
        items = []
        for template in templates:
            stats = stats_by_template.get(str(template.id), {})
            items.append({
                'id': str(template.id), 'space_id': str(template.space_id),
                'name': template.name, 'description': template.description,
                'current_version': stats.get('latest_version'),
                'version_count': stats.get('version_count', 0),
                'created_at': _iso(template.created_at), 'updated_at': _iso(template.updated_at),
            })
        return {
            'items': items, 'total': total, 'page': page, 'page_size': page_size,
            'pages': math.ceil(total / page_size),
        }

    @staticmethod
    async def get_template(space_id: str, template_id: str) -> dict:
        async with in_transaction() as connection:
            await connection.execute_query('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            template = await TestCaseTemplateService._get_template(space_id, template_id, connection)
            versions_query = TestCaseTemplateVersionModel.filter(template_id=template.id).using_db(connection)
            version_count = await versions_query.count()
            latest = await versions_query.order_by('-version_number').first()
            history = await versions_query.order_by('-version_number').only(
                'id', 'template_id', 'version_number', 'created_by_id', 'created_at'
            ).limit(10)
        return {
            'id': str(template.id), 'space_id': str(template.space_id),
            'name': template.name, 'description': template.description,
            'current_version': latest.version_number if latest else None,
            'version_count': version_count,
            'fields': latest.content if latest else None,
            'versions': [_version_dict(version) for version in history],
            'created_at': _iso(template.created_at), 'updated_at': _iso(template.updated_at),
        }

    @staticmethod
    async def list_versions(space_id: str, template_id: str, page: int = 1, page_size: int = 20) -> dict:
        if page < 1 or page_size < 1 or page_size > 50:
            raise HTTPException(status_code=422, detail='Invalid version pagination')
        async with in_transaction() as connection:
            await connection.execute_query('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            template = await TestCaseTemplateService._get_template(space_id, template_id, connection)
            query = TestCaseTemplateVersionModel.filter(template_id=template.id).using_db(connection)
            total = await query.count()
            versions = await query.order_by('-version_number').only(
                'id', 'template_id', 'version_number', 'created_by_id', 'created_at'
            ).offset((page - 1) * page_size).limit(page_size)
        return {
            'items': [_version_dict(version) for version in versions],
            'total': total, 'page': page, 'page_size': page_size,
            'pages': math.ceil(total / page_size),
        }

    @staticmethod
    async def get_version(space_id: str, template_id: str, version_number: int) -> dict:
        if version_number < 1 or version_number > MAX_TEMPLATE_VERSIONS:
            raise HTTPException(status_code=422, detail='Invalid template version number')
        template = await TestCaseTemplateService._get_template(space_id, template_id)
        version = await TestCaseTemplateVersionModel.filter(
            template_id=template.id, version_number=version_number
        ).first()
        if not version:
            raise HTTPException(status_code=404, detail='Template version not found')
        return _version_dict(version, include_fields=True)

    @staticmethod
    async def create_template(space_id: str, dto: CaseTemplateCreateDto, actor_id: str | None) -> dict:
        space_uuid = _uuid(space_id, 'space ID')
        template_id = uuid.uuid4()
        fields = dto.fields.model_dump()
        try:
            async with in_transaction() as connection:
                space = await SpaceModel.filter(id=space_uuid).using_db(connection).select_for_update().first()
                if not space:
                    raise HTTPException(status_code=404, detail='Space not found')
                template = await TestCaseTemplateModel.create(
                    id=template_id, space_id=space_uuid, name=dto.name,
                    normalized_name=_normalize_name(dto.name), description=dto.description,
                    created_by_id=_uuid(actor_id, 'actor ID') if actor_id else None,
                    using_db=connection,
                )
                version = await TestCaseTemplateVersionModel.create(
                    id=uuid.uuid4(), template_id=template.id, version_number=1,
                    content=fields, created_by_id=_uuid(actor_id, 'actor ID') if actor_id else None,
                    using_db=connection,
                )
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail='A template with this name already exists') from exc
        return {
            'id': str(template.id), 'space_id': str(template.space_id),
            'name': template.name, 'description': template.description,
            'current_version': 1, 'version_count': 1,
            'fields': version.content, 'versions': [_version_dict(version)],
            'created_at': _iso(template.created_at), 'updated_at': _iso(template.updated_at),
        }

    @staticmethod
    async def update_template(space_id: str, template_id: str, dto: CaseTemplateUpdateDto, actor_id: str | None) -> dict:
        space_uuid = _uuid(space_id, 'space ID')
        template_uuid = _uuid(template_id, 'template ID')
        fields = dto.fields.model_dump()
        try:
            async with in_transaction() as connection:
                space = await SpaceModel.filter(id=space_uuid).using_db(connection).select_for_update().first()
                if not space:
                    raise HTTPException(status_code=404, detail='Space not found')
                template = await TestCaseTemplateModel.filter(
                    id=template_uuid, space_id=space_uuid
                ).using_db(connection).select_for_update().first()
                if not template:
                    raise HTTPException(status_code=404, detail='Case template not found')
                latest = await TestCaseTemplateService._latest_version(template.id, connection)
                if not latest:
                    raise HTTPException(status_code=409, detail='Case template has no version')
                template.name = dto.name
                template.normalized_name = _normalize_name(dto.name)
                template.description = dto.description
                await template.save(using_db=connection)
                if latest.content != fields:
                    if latest.version_number >= MAX_TEMPLATE_VERSIONS:
                        raise HTTPException(status_code=409, detail='Template version limit reached')
                    latest = await TestCaseTemplateVersionModel.create(
                        id=uuid.uuid4(), template_id=template.id,
                        version_number=latest.version_number + 1, content=fields,
                        created_by_id=_uuid(actor_id, 'actor ID') if actor_id else None,
                        using_db=connection,
                    )
                version_count = await TestCaseTemplateVersionModel.filter(
                    template_id=template.id
                ).using_db(connection).count()
        except IntegrityError as exc:
            raise HTTPException(status_code=409, detail='A template with this name already exists') from exc
        return {
            'id': str(template.id), 'space_id': str(template.space_id),
            'name': template.name, 'description': template.description,
            'current_version': latest.version_number, 'version_count': version_count,
            'fields': latest.content, 'versions': [_version_dict(latest)],
            'created_at': _iso(template.created_at), 'updated_at': _iso(template.updated_at),
        }

    @staticmethod
    async def use_template(
        space_id: str,
        template_id: str,
        dto: CaseTemplateUseDto,
        token: str,
    ) -> TestCaseModel:
        space_uuid = _uuid(space_id, 'space ID')
        template = await TestCaseTemplateService._get_template(space_id, template_id)
        if dto.version_number is None:
            version = await TestCaseTemplateService._latest_version(template.id)
        else:
            version = await TestCaseTemplateVersionModel.filter(
                template_id=template.id, version_number=dto.version_number
            ).first()
        if not version:
            raise HTTPException(status_code=404, detail='Template version not found')
        content = dict(version.content)
        content.update(dto.overrides.model_dump(exclude_none=True))
        content = CaseTemplateFieldsDto.model_validate(content).model_dump()
        suite_id = str(dto.suite_id) if dto.suite_id else None
        section_id = str(dto.section_id) if dto.section_id else None
        if suite_id:
            suite = await TestSuiteModel.get_or_none(id=suite_id, space_id=space_uuid)
            if not suite:
                raise HTTPException(status_code=404, detail='Test suite not found')
        if section_id:
            section = await SectionModel.filter(
                id=section_id, suite__space_id=space_uuid
            ).first()
            if not section:
                raise HTTPException(status_code=404, detail='Section not found')
            if suite_id and str(section.suite_id) != suite_id:
                raise HTTPException(status_code=422, detail='Section must belong to the selected space and suite')
            suite_id = str(section.suite_id)
        dto_case = TestCaseCreateDto(
            space_id=str(space_uuid), title=dto.title,
            text=content.get('text'), preconditions=content.get('preconditions'),
            steps=content.get('steps'), expected_results=content.get('expected_results'),
            postconditions=content.get('postconditions'), type=content.get('type', 'manual'),
            priority=content.get('priority', 'P2'),
            estimated_duration_seconds=content.get('estimated_duration_seconds'),
            custom_fields=[item.model_dump() for item in dto.custom_fields] if dto.custom_fields is not None else None,
            suite_id=suite_id, section_id=section_id,
        )
        return await TestCaseService.create(dto_case, token)
