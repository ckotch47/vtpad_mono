from fastapi import HTTPException
from typing import Optional

from tortoise import Tortoise
from tortoise.transactions import in_transaction

from .model import (
    TestCaseModel, TestCaseVersionModel, TestCaseType, TestCaseStatus,
    TestCasePriority, TestCaseTagModel, TestCaseTagLinkModel,
)
from .dto import *
from ..common.crypto import get_user_id_by_token
from ..common.space_capabilities import require_space_capability
from ..embedding.service import EmbeddingService
from ..common.pagination import paginate


class TestCaseService:
    @staticmethod
    async def _require_tag_capability(space_id: str, user_id: str | None) -> None:
        await require_space_capability(str(user_id or ''), str(space_id), 'tags')

    @staticmethod
    def _serialize_list_item(
        testcase: TestCaseModel,
        tags: list[str],
        custom_fields: list[dict],
    ) -> dict:
        return {
            'id': str(testcase.id),
            'title': testcase.title,
            'text': testcase.text,
            'steps': testcase.steps,
            'expected_results': testcase.expected_results,
            'preconditions': testcase.preconditions,
            'postconditions': testcase.postconditions,
            'sort': testcase.sort,
            'short_name': testcase.short_name,
            'link': testcase.link,
            'type': testcase.type,
            'status': testcase.status,
            'priority': testcase.priority,
            'tags': tags,
            'custom_fields': custom_fields,
            'external_id': testcase.external_id,
            'estimated_duration_seconds': testcase.estimated_duration_seconds,
            'space_id': str(testcase.space_id),
            'suite_id': str(testcase.suite_id) if testcase.suite_id else None,
            'suite': {
                'id': str(testcase.suite.id),
                'name': testcase.suite.name,
            } if testcase.suite else None,
            'section_id': str(testcase.section_id) if testcase.section_id else None,
            'created_by_id': str(testcase.created_by_id) if testcase.created_by_id else None,
            'created_by': {
                'id': str(testcase.created_by.id),
                'username': testcase.created_by.username,
            } if testcase.created_by else None,
            'created_at': testcase.created_at.isoformat() if testcase.created_at else None,
            'updated_at': testcase.updated_at.isoformat() if testcase.updated_at else None,
        }

    @staticmethod
    async def _get_full_text_page(
        space_id: str,
        search: str,
        type_filter: Optional[str],
        status_filter: Optional[str],
        suite_id: Optional[str],
        priority_filter: Optional[str],
        tag_filters: Optional[list[str]],
        page: int,
        page_size: int,
    ) -> dict:
        """Search one space through its trigger-maintained PostgreSQL vector."""
        params: list = [space_id, search]
        filter_conditions = ['test_case.space_id = $1']
        exact_identifier = (
            "numnode(websearch_to_tsquery('simple', $2)) > 0 "
            "AND COALESCE(lower(test_case.short_name) = lower($2), FALSE)"
        )

        def add_filter(column: str, value) -> None:
            params.append(value.value if hasattr(value, 'value') else value)
            filter_conditions.append(f'test_case.{column} = ${len(params)}')

        if type_filter:
            add_filter('type', type_filter)
        if status_filter:
            add_filter('status', status_filter)
        if priority_filter:
            if priority_filter not in {item.value for item in TestCasePriority}:
                raise HTTPException(status_code=422, detail="priority must be P0, P1, P2, or P3")
            add_filter('priority', priority_filter)
        if suite_id == 'none':
            filter_conditions.append('test_case.suite_id IS NULL')
        elif suite_id:
            add_filter('suite_id', suite_id)

        normalized_tags = [
            tag.casefold() for tag in TestCaseService._normalize_tags(tag_filters)
        ]
        if normalized_tags:
            params.append(normalized_tags)
            tag_param = len(params)
            filter_conditions.append(
                '(SELECT count(DISTINCT tag.normalized_name) '
                'FROM test_case_tag_link AS link '
                'JOIN test_case_tag AS tag ON tag.id = link.tag_id '
                f'WHERE link.testcase_id = test_case.id AND tag.space_id = test_case.space_id '
                f'AND tag.normalized_name = ANY(${tag_param}::text[])) = ${tag_param + 1}'
            )
            params.append(len(normalized_tags))

        filter_sql = ' AND '.join(filter_conditions)
        where_sql = (
            f"{filter_sql} AND (test_case.search_vector @@ "
            "websearch_to_tsquery('simple', $2) "
            f"OR ({exact_identifier}))"
        )
        connection = Tortoise.get_connection('default')
        count_rows = await connection.execute_query_dict(
            f'SELECT count(*) AS total FROM test_case WHERE {where_sql}', params
        )
        total = count_rows[0]['total']

        page_params = [*params, page_size, (page - 1) * page_size]
        rows = await connection.execute_query_dict(
            "SELECT test_case.id, ts_rank(test_case.search_vector, "
            "websearch_to_tsquery('simple', $2)) AS rank "
            f'FROM test_case WHERE {filter_sql} '
            "AND test_case.search_vector @@ websearch_to_tsquery('simple', $2) "
            f'AND NOT ({exact_identifier}) '
            'UNION ALL '
            "SELECT test_case.id, ts_rank(test_case.search_vector, "
            "websearch_to_tsquery('simple', $2)) + 2.0 AS rank "
            f'FROM test_case WHERE {filter_sql} AND ({exact_identifier}) '
            f'ORDER BY rank DESC, id ASC LIMIT ${len(params) + 1} '
            f'OFFSET ${len(params) + 2}',
            page_params,
        )
        case_ids = [str(row['id']) for row in rows]
        cases = await TestCaseModel.filter(id__in=case_ids).prefetch_related(
            'suite', 'created_by'
        ) if case_ids else []
        cases_by_id = {str(case.id): case for case in cases}
        ordered_cases = [cases_by_id[case_id] for case_id in case_ids if case_id in cases_by_id]
        tags_by_case = await TestCaseService.get_tags_for_cases(case_ids)
        from ..custom_field.service import CustomFieldValueService
        custom_fields_by_case = await CustomFieldValueService.get_snapshot_values(
            space_id, case_ids
        )
        return {
            'items': [
                TestCaseService._serialize_list_item(
                    testcase,
                    tags_by_case.get(str(testcase.id), []),
                    custom_fields_by_case.get(str(testcase.id), []),
                )
                for testcase in ordered_cases
            ],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size,
        }

    @staticmethod
    def _normalize_tags(tags: Optional[list[str]]) -> list[str]:
        distinct: dict[str, str] = {}
        for value in tags or []:
            if not isinstance(value, str) or not value.strip() or len(value.strip()) > 255:
                raise HTTPException(status_code=422, detail="tag names must contain 1 to 255 characters")
            name = value.strip()
            if len(name.casefold()) > 255:
                raise HTTPException(status_code=422, detail="normalized tag names cannot exceed 255 characters")
            if name:
                distinct.setdefault(name.casefold(), name)
        return list(distinct.values())

    @staticmethod
    async def _replace_tags(testcase_id: str, space_id: str, tags: list[str], connection=None) -> None:
        conn = connection or Tortoise.get_connection('default')
        await TestCaseTagLinkModel.filter(testcase_id=testcase_id).using_db(conn).delete()
        for name in TestCaseService._normalize_tags(tags):
            normalized = name.casefold()
            rows = await conn.execute_query_dict(
                "INSERT INTO test_case_tag (space_id, name, normalized_name) "
                "VALUES ($1, $2, $3) ON CONFLICT (space_id, normalized_name) "
                "DO UPDATE SET normalized_name = EXCLUDED.normalized_name RETURNING id",
                [space_id, name, normalized],
            )
            tag_id = str(rows[0]['id'])
            await TestCaseTagLinkModel.create(
                testcase_id=testcase_id, tag_id=tag_id, using_db=conn
            )

    @staticmethod
    async def get_tags(testcase_id: str) -> list[str]:
        links = await TestCaseTagLinkModel.filter(testcase_id=testcase_id).prefetch_related('tag')
        return sorted((link.tag.name for link in links), key=str.casefold)

    @staticmethod
    async def get_tags_for_cases(testcase_ids: list[str], connection=None) -> dict[str, list[str]]:
        if not testcase_ids:
            return {}
        query = TestCaseTagLinkModel.filter(testcase_id__in=testcase_ids)
        if connection is not None:
            query = query.using_db(connection)
        links = await query.prefetch_related('tag')
        result: dict[str, list[str]] = {str(case_id): [] for case_id in testcase_ids}
        for link in links:
            result.setdefault(str(link.testcase_id), []).append(link.tag.name)
        for names in result.values():
            names.sort(key=str.casefold)
        return result

    @staticmethod
    async def get_tag_options(space_id: str) -> list[str]:
        tags = await TestCaseTagModel.filter(space_id=space_id).order_by('normalized_name')
        return [tag.name for tag in tags]

    @staticmethod
    async def _filter_ids_by_all_tags(
        space_id: str,
        tags: Optional[list[str]],
        connection=None,
    ) -> Optional[set[str]]:
        names = TestCaseService._normalize_tags(tags)
        if not names:
            return None
        normalized_names = [name.casefold() for name in names]
        name_placeholders = ', '.join(
            f'${index}' for index in range(2, len(normalized_names) + 2)
        )
        count_parameter = len(normalized_names) + 2
        connection = connection or Tortoise.get_connection('default')
        rows = await connection.execute_query_dict(
            "SELECT link.testcase_id "
            "FROM test_case_tag_link AS link "
            "JOIN test_case_tag AS tag ON tag.id = link.tag_id "
            f"WHERE tag.space_id = $1 AND tag.normalized_name IN ({name_placeholders}) "
            "GROUP BY link.testcase_id "
            f"HAVING COUNT(DISTINCT tag.normalized_name) = ${count_parameter}",
            [space_id, *normalized_names, len(normalized_names)],
        )
        return {str(row['testcase_id']) for row in rows}

    @staticmethod
    async def serialize_case(
        testcase: TestCaseModel,
        tags: Optional[list[str]] = None,
        custom_fields: Optional[list[dict]] = None,
    ) -> dict:
        if tags is None:
            tags = await TestCaseService.get_tags(str(testcase.id))
        if custom_fields is None:
            from ..custom_field.service import CustomFieldValueService
            custom_fields = await CustomFieldValueService.get_snapshot_values(
                str(testcase.space_id), [str(testcase.id)]
            )
            custom_fields = custom_fields.get(str(testcase.id), [])
        return {
            'id': str(testcase.id), 'title': testcase.title, 'text': testcase.text,
            'steps': testcase.steps, 'expected_results': testcase.expected_results,
            'preconditions': testcase.preconditions, 'postconditions': testcase.postconditions,
            'sort': testcase.sort, 'short_name': testcase.short_name, 'link': testcase.link,
            'type': testcase.type, 'status': testcase.status,
            'priority': testcase.priority, 'tags': tags,
            'external_id': testcase.external_id,
            'estimated_duration_seconds': testcase.estimated_duration_seconds,
            'custom_fields': custom_fields,
            'space_id': str(testcase.space_id),
            'suite_id': str(testcase.suite_id) if testcase.suite_id else None,
            'section_id': str(testcase.section_id) if testcase.section_id else None,
            'created_by_id': str(testcase.created_by_id) if testcase.created_by_id else None,
            'created_at': testcase.created_at.isoformat() if testcase.created_at else None,
            'updated_at': testcase.updated_at.isoformat() if testcase.updated_at else None,
        }

    @staticmethod
    async def serialize_cases(testcases: list[TestCaseModel]) -> list[dict]:
        case_ids = [str(testcase.id) for testcase in testcases]
        tags_by_case = await TestCaseService.get_tags_for_cases(
            case_ids
        )
        from ..custom_field.service import CustomFieldValueService
        custom_fields_by_case = await CustomFieldValueService.get_snapshot_values(
            str(testcases[0].space_id) if testcases else '', case_ids
        )
        return [
            await TestCaseService.serialize_case(
                testcase,
                tags=tags_by_case.get(str(testcase.id), []),
                custom_fields=custom_fields_by_case.get(str(testcase.id), []),
            )
            for testcase in testcases
        ]

    @staticmethod
    async def create(dto: TestCaseCreateDto, token: str) -> TestCaseModel:
        user_id = await get_user_id_by_token(token)
        if dto.tags:
            await TestCaseService._require_tag_capability(dto.space_id, str(user_id))
        section_id = dto.section_id
        suite_id = dto.suite_id

        if section_id:
            from ..section.model import SectionModel
            section = await SectionModel.get_or_none(id=section_id)
            if section:
                suite_id = str(section.suite_id)

        async with in_transaction() as connection:
            # Serialize testcase creation with creation/activation of required
            # custom fields in this space. Keep space -> testcase -> fields as
            # the shared lock order for these domain mutations.
            from ..space.model import SpaceModel
            space = await SpaceModel.filter(id=dto.space_id).using_db(connection).select_for_update().first()
            if not space:
                raise HTTPException(status_code=404, detail="Space not found")
            last = await TestCaseModel.filter(
                space_id=dto.space_id,
                suite_id=suite_id,
                section_id=section_id
            ).using_db(connection).order_by('-sort').first()
            sort = (last.sort + 10) if last else 10
            testcase = await TestCaseModel.create(
                title=dto.title,
                text=dto.text,
                steps=dto.steps,
                expected_results=dto.expected_results,
                preconditions=dto.preconditions,
                postconditions=dto.postconditions,
                type=dto.type,
                sort=sort,
                space_id=dto.space_id,
                suite_id=suite_id,
                section_id=section_id,
                short_name=dto.short_name,
                link=dto.link,
                external_id=dto.external_id,
                estimated_duration_seconds=dto.estimated_duration_seconds,
                priority=dto.priority,
                created_by_id=user_id,
                using_db=connection,
            )
            await TestCaseService._replace_tags(
                str(testcase.id), dto.space_id, dto.tags, connection=connection
            )
            from ..custom_field.service import CustomFieldValueService
            await CustomFieldValueService.replace_case_values(
                testcase,
                [item.model_dump() for item in dto.custom_fields] if dto.custom_fields is not None else None,
                connection,
            )
            await TestCaseService._create_test_case_version(
                testcase, user_id, connection=connection
            )

        # Index for semantic search
        await EmbeddingService.index_test_case(
            case_id=str(testcase.id),
            space_id=dto.space_id,
            title=dto.title,
            text=dto.text,
            steps=dto.steps,
            expected_results=dto.expected_results,
            preconditions=dto.preconditions,
        )
        return testcase

    @staticmethod
    async def get_by_space(
        space_id: str,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        suite_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
        sort_by: Optional[str] = 'created_at',
        sort_order: Optional[str] = 'desc',
        search: Optional[str] = None,
        priority_filter: Optional[str] = None,
        tag_filters: Optional[list[str]] = None,
    ) -> dict:
        normalized_search = search.strip() if isinstance(search, str) else ''
        if normalized_search:
            return await TestCaseService._get_full_text_page(
                space_id=space_id,
                search=normalized_search,
                type_filter=type_filter,
                status_filter=status_filter,
                suite_id=suite_id,
                priority_filter=priority_filter,
                tag_filters=tag_filters,
                page=page,
                page_size=page_size,
            )

        q = TestCaseModel.filter(space_id=space_id)
        if type_filter:
            q = q.filter(type=type_filter)
        if status_filter:
            q = q.filter(status=status_filter)
        if priority_filter:
            if priority_filter not in {item.value for item in TestCasePriority}:
                raise HTTPException(status_code=422, detail="priority must be P0, P1, P2, or P3")
            q = q.filter(priority=priority_filter)
        tag_case_ids = await TestCaseService._filter_ids_by_all_tags(space_id, tag_filters)
        if tag_case_ids is not None:
            q = q.filter(id__in=list(tag_case_ids))
        if suite_id == 'none':
            q = q.filter(suite_id__isnull=True)
        elif suite_id:
            q = q.filter(suite_id=suite_id)
        result = await paginate(
            q.prefetch_related('suite', 'created_by'), page, page_size, sort_by, sort_order
        )
        case_ids = [str(item.id) for item in result['items']]
        tags_by_case = await TestCaseService.get_tags_for_cases(case_ids)
        from ..custom_field.service import CustomFieldValueService
        custom_fields_by_case = await CustomFieldValueService.get_snapshot_values(
            space_id, case_ids
        )
        return {
            **result,
            'items': [
                TestCaseService._serialize_list_item(
                    testcase,
                    tags_by_case.get(str(testcase.id), []),
                    custom_fields_by_case.get(str(testcase.id), []),
                )
                for testcase in result['items']
            ],
        }

    @staticmethod
    async def get_by_suite(suite_id: str) -> list[TestCaseModel]:
        from ..test_suite.model import TestSuiteModel
        suite = await TestSuiteModel.get_or_none(id=suite_id)
        if not suite:
            return []
        return await TestCaseModel.filter(
            suite_id=suite_id, space_id=str(suite.space_id)
        ).order_by('sort')

    @staticmethod
    async def get_by_section(section_id: str) -> list[TestCaseModel]:
        from ..section.model import SectionModel
        from ..test_suite.model import TestSuiteModel
        section = await SectionModel.get_or_none(id=section_id)
        if not section:
            return []
        suite = await TestSuiteModel.get_or_none(id=section.suite_id)
        if not suite:
            return []
        return await TestCaseModel.filter(
            section_id=section_id,
            suite_id=str(suite.id),
            space_id=str(suite.space_id),
        ).order_by('sort')

    @staticmethod
    async def get_by_id(testcase_id: str) -> TestCaseModel:
        testcase = await TestCaseModel.get_or_none(id=testcase_id)
        if not testcase:
            raise HTTPException(status_code=404, detail="Test case not found")
        return testcase

    @staticmethod
    async def get_with_versions(testcase_id: str) -> dict:
        testcase = await TestCaseModel.get_or_none(id=testcase_id).prefetch_related('created_by')
        if not testcase:
            raise HTTPException(status_code=404, detail="Test case not found")
        from ..custom_field.service import CustomFieldValueService
        custom_fields = await CustomFieldValueService.get_snapshot_values(
            str(testcase.space_id), [testcase_id]
        )
        return {
            'id': str(testcase.id),
            'title': testcase.title,
            'text': testcase.text,
            'steps': testcase.steps,
            'expected_results': testcase.expected_results,
            'preconditions': testcase.preconditions,
            'postconditions': testcase.postconditions,
            'sort': testcase.sort,
            'short_name': testcase.short_name,
            'link': testcase.link,
            'type': testcase.type,
            'status': testcase.status,
            'priority': testcase.priority,
            'tags': await TestCaseService.get_tags(testcase_id),
            'external_id': testcase.external_id,
            'estimated_duration_seconds': testcase.estimated_duration_seconds,
            'custom_fields': custom_fields.get(testcase_id, []),
            'space_id': str(testcase.space_id),
            'suite_id': str(testcase.suite_id) if testcase.suite_id else None,
            'section_id': str(testcase.section_id) if testcase.section_id else None,
            'created_by_id': str(testcase.created_by_id) if testcase.created_by_id else None,
            'created_by': {
                'id': str(testcase.created_by.id),
                'username': testcase.created_by.username,
            } if testcase.created_by else None,
            'created_at': testcase.created_at.isoformat() if testcase.created_at else None,
            'updated_at': testcase.updated_at.isoformat() if testcase.updated_at else None,
            'versions': await TestCaseService.get_versions(testcase_id),
        }

    @staticmethod
    async def update(testcase_id: str, dto: TestCaseUpdateDto, token: Optional[str] = None) -> TestCaseModel:
        data = dto.model_dump(exclude_unset=True)
        tag_values = data.pop('tags', None)
        custom_field_values = data.pop('custom_fields', None)
        # PATCH omits nullable fields by default.  `section_id: null` is the
        # one intentional exception: it moves a case to the suite's virtual
        # Default section without changing its suite.  Keep all other nulls
        # out of the update so existing callers can still omit fields safely.
        data = {
            key: value
            for key, value in data.items()
            if value is not None or key in ('section_id', 'estimated_duration_seconds')
        }
        user_id = await get_user_id_by_token(token) if token else None
        async with in_transaction() as connection:
            testcase = await TestCaseModel.filter(id=testcase_id).using_db(connection).select_for_update().first()
            if not testcase:
                raise HTTPException(status_code=404, detail="Test case not found")
            if not data and tag_values is None and custom_field_values is None:
                return testcase
            if tag_values is not None:
                await TestCaseService._require_tag_capability(str(testcase.space_id), str(user_id))
            from ..section.model import SectionModel
            from ..test_suite.model import TestSuiteModel

            target_suite_id = data.get("suite_id", str(testcase.suite_id) if testcase.suite_id else None)
            target_section_id = data.get("section_id", str(testcase.section_id) if testcase.section_id else None)
            if target_suite_id:
                target_suite = await TestSuiteModel.filter(id=target_suite_id).using_db(connection).first()
                if not target_suite or str(target_suite.space_id) != str(testcase.space_id):
                    raise HTTPException(status_code=404, detail="Test case destination not found")
            if target_section_id:
                target_section = await SectionModel.filter(id=target_section_id).using_db(connection).first()
                target_section_suite = (
                    await TestSuiteModel.filter(id=target_section.suite_id).using_db(connection).first()
                    if target_section else None
                )
                if not target_section_suite or str(target_section_suite.space_id) != str(testcase.space_id):
                    raise HTTPException(status_code=404, detail="Test case destination not found")
                if str(target_section.suite_id) != str(target_suite_id):
                    raise HTTPException(status_code=422, detail="Section must belong to destination suite")
            if data:
                await TestCaseModel.filter(id=testcase_id).using_db(connection).update(**data)
            if tag_values is not None:
                await TestCaseService._replace_tags(
                    testcase_id, str(testcase.space_id), tag_values, connection=connection
                )
            if custom_field_values is not None:
                from ..custom_field.service import CustomFieldValueService
                await CustomFieldValueService.replace_case_values(
                    testcase,
                    [item.model_dump() if hasattr(item, 'model_dump') else item for item in custom_field_values],
                    connection,
                )
            updated = await TestCaseModel.filter(id=testcase_id).using_db(connection).first()
            await TestCaseService._create_test_case_version(
                updated, user_id, next_version=True, connection=connection
            )

        # Re-index for semantic search
        await EmbeddingService.index_test_case(
            case_id=testcase_id,
            space_id=str(updated.space_id),
            title=updated.title,
            text=updated.text,
            steps=updated.steps,
            expected_results=updated.expected_results,
            preconditions=updated.preconditions,
        )
        return updated

    @staticmethod
    async def move(testcase_id: str, dto: TestCaseMoveDto) -> TestCaseModel:
        """Move a case to a suite location without creating a content version."""
        from ..section.model import SectionModel
        from ..test_suite.model import TestSuiteModel

        async with in_transaction() as connection:
            testcase = await TestCaseModel.filter(id=testcase_id).using_db(connection).select_for_update().first()
            if not testcase:
                raise HTTPException(status_code=404, detail="Test case not found")

            suite = await TestSuiteModel.filter(id=dto.suite_id).using_db(connection).first()
            if not suite or str(suite.space_id) != str(testcase.space_id):
                # Do not reveal whether a foreign-space suite exists.
                raise HTTPException(status_code=404, detail="Test case destination not found")

            if dto.section_id is not None:
                section = await SectionModel.filter(id=dto.section_id).using_db(connection).first()
                if not section:
                    raise HTTPException(status_code=404, detail="Test case destination not found")
                section_suite = await TestSuiteModel.filter(id=section.suite_id).using_db(connection).first()
                if not section_suite or str(section_suite.space_id) != str(testcase.space_id):
                    # Hide section identifiers outside the testcase's space.
                    raise HTTPException(status_code=404, detail="Test case destination not found")
                if str(section.suite_id) != str(suite.id):
                    raise HTTPException(status_code=422, detail="Section must belong to destination suite")

            if str(testcase.suite_id) == str(suite.id) and (
                str(testcase.section_id) if testcase.section_id else None
            ) == dto.section_id:
                return testcase

            last = await TestCaseModel.filter(
                space_id=testcase.space_id,
                suite_id=suite.id,
                section_id=dto.section_id,
            ).using_db(connection).order_by('-sort').first()
            next_sort = (last.sort + 10) if last else 10
            await TestCaseModel.filter(id=testcase_id).using_db(connection).update(
                suite_id=suite.id,
                section_id=dto.section_id,
                sort=next_sort,
            )
            return await TestCaseModel.filter(id=testcase_id).using_db(connection).first()

    @staticmethod
    async def delete(testcase_id: str) -> bool:
        testcase = await TestCaseService.get_by_id(testcase_id)
        from ..test_run.model import TestResultModel
        if await TestResultModel.filter(testcase_id=testcase_id).exists():
            # Preserve case/version/result snapshots for historical runs.
            await TestCaseModel.filter(id=testcase_id).update(status=TestCaseStatus.deprecated)
            await EmbeddingService.delete_embeddings('test_case', testcase_id)
            return True
        from ..custom_field.model import CustomFieldEntityType, CustomFieldModel, CustomFieldValueModel
        async with in_transaction() as connection:
            locked_case = await TestCaseModel.filter(id=testcase_id).using_db(connection).select_for_update().first()
            if not locked_case:
                return True
            # The polymorphic entity_id has no FK, so remove custom-field
            # values explicitly when permanently deleting a testcase.
            testcase_field_ids = await CustomFieldModel.filter(
                space_id=locked_case.space_id,
                entity_type=CustomFieldEntityType.testcase,
            ).using_db(connection).values_list('id', flat=True)
            if testcase_field_ids:
                await CustomFieldValueModel.filter(
                    entity_id=testcase_id,
                    field_id__in=testcase_field_ids,
                ).using_db(connection).delete()
            await TestCaseVersionModel.filter(testcase_id=testcase_id).using_db(connection).delete()
            await TestCaseModel.filter(id=testcase_id).using_db(connection).delete()
        return True

    @staticmethod
    async def update_sort(testcase_id: str, dto: TestCaseSortDto) -> list[TestCaseModel]:
        testcase = await TestCaseService.get_by_id(testcase_id)
        space_id = str(testcase.space_id)
        suite_id = testcase.suite_id
        section_id = testcase.section_id

        if dto.sort_before_id:
            before = await TestCaseService.get_by_id(dto.sort_before_id)
            target = await TestCaseService.get_by_id(testcase_id)
            if (
                str(before.space_id) != str(target.space_id)
                or str(before.suite_id) != str(target.suite_id)
                or str(before.section_id) != str(target.section_id)
            ):
                raise HTTPException(status_code=422, detail="Cases must be reordered within the same section")
            await TestCaseModel.filter(id=dto.sort_before_id).update(sort=target.sort)
            await TestCaseModel.filter(id=testcase_id).update(sort=before.sort)

        if dto.sort_after_id:
            after = await TestCaseService.get_by_id(dto.sort_after_id)
            target = await TestCaseService.get_by_id(testcase_id)
            await TestCaseModel.filter(id=dto.sort_after_id).update(sort=target.sort)
            await TestCaseModel.filter(id=testcase_id).update(sort=after.sort)

        return await TestCaseModel.filter(space_id=space_id, suite_id=suite_id, section_id=section_id).order_by('sort')

    @staticmethod
    async def get_run_history(testcase_id: str, page: int = 1, page_size: int = 25) -> dict:
        from ..test_run.model import TestResultModel
        from ..test_run.service import TestRunService

        q = TestResultModel.filter(testcase_id=testcase_id).prefetch_related('run').order_by('-created_at')
        result = await paginate(q, page, page_size)
        items = result['items']
        timers_by_run = await TestRunService.get_timers([
            str(r.run_id) for r in items if r.run_id
        ])

        results = []
        for r in items:
            run = r.run
            duration_seconds = r.duration_seconds
            if duration_seconds is not None and duration_seconds < 0:
                duration_seconds = None
            results.append({
                'id': str(r.id),
                'run_id': str(run.id) if run else None,
                'run_name': run.name if run else None,
                'status': r.status,
                'duration_seconds': duration_seconds,
                'estimated_duration_seconds': (
                    (r.testcase_snapshot or {}).get('estimated_duration_seconds')
                    if r.testcase_snapshot else None
                ),
                'run_timer': timers_by_run.get(str(run.id)) if run else None,
                'comment': r.comment,
                'executed_at': r.executed_at.isoformat() if r.executed_at else None,
                'created_at': r.created_at.isoformat() if r.created_at else None,
            })

        return {**result, 'items': results}

    @staticmethod
    async def _compute_next_sort(original, connection=None):
        query = TestCaseModel.filter(
            space_id=str(original.space_id),
            suite_id=original.suite_id,
            section_id=original.section_id
        )
        if connection is not None:
            query = query.using_db(connection)
        last = await query.order_by('-sort').first()
        return (last.sort + 10) if last else 10

    @staticmethod
    def _generate_copy_short_name(short_name):
        if not short_name:
            return short_name
        import re
        m = re.search(r'(_copy(\d+))$', short_name)
        if m:
            n = int(m.group(2)) + 1
            return short_name[:m.start()] + f'_copy{n}'
        return short_name + '_copy'

    @staticmethod
    async def _create_test_case_version(testcase, user_id, next_version: bool = False, connection=None):
        query = TestCaseVersionModel.filter(testcase_id=str(testcase.id))
        if connection is not None:
            query = query.using_db(connection)
        last_version = await query.order_by('-version_number').first()
        version_number = (last_version.version_number + 1) if last_version and next_version else 1
        tag_query = await (connection or Tortoise.get_connection('default')).execute_query_dict(
            "SELECT tag.name FROM test_case_tag_link link "
            "JOIN test_case_tag tag ON tag.id = link.tag_id "
            "WHERE link.testcase_id = $1 ORDER BY tag.normalized_name",
            [str(testcase.id)],
        )
        from ..custom_field.service import CustomFieldValueService
        custom_fields = await CustomFieldValueService.get_snapshot_values(
            str(testcase.space_id), [str(testcase.id)], connection
        )
        create_kwargs = {
            'testcase_id': str(testcase.id),
            'version_number': version_number,
            'title': testcase.title,
            'text': testcase.text,
            'steps': testcase.steps,
            'expected_results': testcase.expected_results,
            'preconditions': testcase.preconditions,
            'postconditions': testcase.postconditions,
            'estimated_duration_seconds': testcase.estimated_duration_seconds,
            'type': testcase.type,
            'priority': testcase.priority,
            'tag_labels': [row['name'] for row in tag_query],
            'custom_fields': custom_fields.get(str(testcase.id), []),
            'created_by_id': user_id,
        }
        if connection is not None:
            create_kwargs['using_db'] = connection
        await TestCaseVersionModel.create(
            **create_kwargs,
        )

    @staticmethod
    async def _index_test_case_for_search(testcase):
        await EmbeddingService.index_test_case(
            case_id=str(testcase.id),
            space_id=str(testcase.space_id),
            title=testcase.title,
            text=testcase.text,
            steps=testcase.steps,
            expected_results=testcase.expected_results,
            preconditions=testcase.preconditions,
        )

    @staticmethod
    async def duplicate(testcase_id: str, token: str) -> TestCaseModel:
        user_id = await get_user_id_by_token(token)
        original = await TestCaseService.get_by_id(testcase_id)

        new_short_name = TestCaseService._generate_copy_short_name(original.short_name)
        original_tags = await TestCaseService.get_tags(str(original.id))
        if original_tags:
            await TestCaseService._require_tag_capability(str(original.space_id), str(user_id))

        async with in_transaction() as connection:
            from ..space.model import SpaceModel
            space = await SpaceModel.filter(id=original.space_id).using_db(connection).select_for_update().first()
            if not space:
                raise HTTPException(status_code=404, detail="Space not found")
            sort = await TestCaseService._compute_next_sort(original, connection)
            duplicated = await TestCaseModel.create(
                title=f"{original.title} (Copy)",
                text=original.text,
                steps=original.steps,
                expected_results=original.expected_results,
                preconditions=original.preconditions,
                postconditions=original.postconditions,
                estimated_duration_seconds=original.estimated_duration_seconds,
                priority=original.priority,
                type=original.type,
                status=original.status,
                sort=sort,
                space_id=str(original.space_id),
                suite_id=original.suite_id,
                section_id=original.section_id,
                short_name=new_short_name,
                link=original.link,
                external_id=original.external_id,
                created_by_id=user_id,
                using_db=connection,
            )
            await TestCaseService._replace_tags(
                str(duplicated.id), str(duplicated.space_id), original_tags, connection=connection
            )
            from ..custom_field.service import CustomFieldValueService
            original_fields = await CustomFieldValueService.get_snapshot_values(
                str(original.space_id), [str(original.id)], connection
            )
            await CustomFieldValueService.replace_case_values(
                duplicated,
                [
                    {'field_id': field['field_id'], 'value': field['value']}
                    for field in original_fields.get(str(original.id), [])
                ],
                connection,
            )
            await TestCaseService._create_test_case_version(
                duplicated, user_id, connection=connection
            )
        await TestCaseService._index_test_case_for_search(duplicated)

        return duplicated

    @staticmethod
    def _serialize_version(version: TestCaseVersionModel) -> dict:
        return {
            'id': str(version.id),
            'testcase_id': str(version.testcase_id),
            'version_number': version.version_number,
            'title': version.title,
            'text': version.text,
            'steps': version.steps,
            'expected_results': version.expected_results,
            'preconditions': version.preconditions,
            'postconditions': version.postconditions,
            'estimated_duration_seconds': version.estimated_duration_seconds,
            'type': version.type,
            'priority': version.priority,
            'tags': version.tag_labels,
            'custom_fields': version.custom_fields,
            'created_by_id': str(version.created_by_id) if version.created_by_id else None,
            'created_at': version.created_at.isoformat() if version.created_at else None,
        }

    @staticmethod
    async def get_versions(testcase_id: str) -> list[dict]:
        await TestCaseService.get_by_id(testcase_id)
        versions = await TestCaseVersionModel.filter(testcase_id=testcase_id).order_by('-version_number')
        return [TestCaseService._serialize_version(version) for version in versions]

    @staticmethod
    async def get_version(testcase_id: str, version_id: str) -> dict:
        version = await TestCaseVersionModel.get_or_none(id=version_id, testcase_id=testcase_id)
        if not version:
            raise HTTPException(status_code=404, detail="Test case version not found")
        return TestCaseService._serialize_version(version)

    @staticmethod
    async def diff_versions(testcase_id: str, from_version_id: str, to_version_id: str) -> dict:
        from_version = await TestCaseService.get_version(testcase_id, from_version_id)
        to_version = await TestCaseService.get_version(testcase_id, to_version_id)
        fields = (
            'title', 'type', 'priority', 'tags', 'text', 'steps',
            'expected_results', 'preconditions', 'postconditions',
            'estimated_duration_seconds',
            'custom_fields',
        )
        changes = {
            field: {'from': from_version[field], 'to': to_version[field]}
            for field in fields
            if from_version[field] != to_version[field]
        }
        return {
            'testcase_id': testcase_id,
            'from_version': from_version,
            'to_version': to_version,
            'changes': changes,
        }

    @staticmethod
    async def restore_version(testcase_id: str, version_id: str, token: str) -> TestCaseModel:
        user_id = await get_user_id_by_token(token)
        async with in_transaction() as connection:
            restored = await TestCaseModel.filter(id=testcase_id).using_db(connection).select_for_update().first()
            if not restored:
                raise HTTPException(status_code=404, detail="Test case not found")
            version = await TestCaseVersionModel.filter(
                id=version_id, testcase_id=testcase_id
            ).using_db(connection).first()
            if not version:
                raise HTTPException(status_code=404, detail="Test case version not found")
            if version.tag_labels is not None:
                await TestCaseService._require_tag_capability(str(restored.space_id), str(user_id))
            await TestCaseModel.filter(id=testcase_id).using_db(connection).update(
                title=version.title,
                text=version.text,
                steps=version.steps,
                expected_results=version.expected_results,
                preconditions=version.preconditions,
                postconditions=version.postconditions,
                estimated_duration_seconds=version.estimated_duration_seconds,
                **({'type': version.type} if version.type is not None else {}),
                **({'priority': version.priority} if version.priority is not None else {}),
            )
            if version.tag_labels is not None:
                await TestCaseService._replace_tags(
                    testcase_id, str(restored.space_id), version.tag_labels, connection=connection
                )
            from ..custom_field.service import CustomFieldValueService
            await CustomFieldValueService.restore_case_values(
                restored, version.custom_fields, connection
            )
            restored = await TestCaseModel.filter(id=testcase_id).using_db(connection).first()
            await TestCaseService._create_test_case_version(
                restored, user_id, next_version=True, connection=connection
            )
        await TestCaseService._index_test_case_for_search(restored)
        return restored
