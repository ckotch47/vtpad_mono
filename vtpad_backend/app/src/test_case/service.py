from fastapi import HTTPException
from typing import Optional

from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from .model import TestCaseModel, TestCaseVersionModel, TestCaseType, TestCaseStatus
from .dto import *
from ..common.crypto import get_user_id_by_token
from ..embedding.service import EmbeddingService
from ..common.pagination import paginate


class TestCaseService:
    @staticmethod
    async def create(dto: TestCaseCreateDto, token: str) -> TestCaseModel:
        user_id = await get_user_id_by_token(token)
        section_id = dto.section_id
        suite_id = dto.suite_id

        if section_id:
            from ..section.model import SectionModel
            section = await SectionModel.get_or_none(id=section_id)
            if section:
                suite_id = str(section.suite_id)

        last = await TestCaseModel.filter(
            space_id=dto.space_id,
            suite_id=suite_id,
            section_id=section_id
        ).order_by('-sort').first()
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
            created_by_id=user_id,
        )

        # Create initial version snapshot
        await TestCaseVersionModel.create(
            testcase_id=str(testcase.id),
            version_number=1,
            title=dto.title,
            text=dto.text,
            steps=dto.steps,
            expected_results=dto.expected_results,
            preconditions=dto.preconditions,
            postconditions=dto.postconditions,
            created_by_id=user_id,
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
        search: Optional[str] = None
    ) -> dict:
        q = TestCaseModel.filter(space_id=space_id)
        if type_filter:
            q = q.filter(type=type_filter)
        if status_filter:
            q = q.filter(status=status_filter)
        if suite_id == 'none':
            q = q.filter(suite_id__isnull=True)
        elif suite_id:
            q = q.filter(suite_id=suite_id)
        if search:
            search_q = (
                Q(title__icontains=search)
                | Q(short_name__icontains=search)
                | Q(text__icontains=search)
                | Q(steps__icontains=search)
                | Q(expected_results__icontains=search)
                | Q(preconditions__icontains=search)
                | Q(postconditions__icontains=search)
                | Q(external_id__icontains=search)
                | Q(link__icontains=search)
            )
            q = q.filter(search_q)

        result = await paginate(
            q.prefetch_related('suite', 'created_by'), page, page_size, sort_by, sort_order
        )
        return {
            **result,
            'items': [
                {
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
                    'external_id': testcase.external_id,
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
                for testcase in result['items']
            ],
        }

    @staticmethod
    async def get_by_suite(suite_id: str) -> list[TestCaseModel]:
        return await TestCaseModel.filter(suite_id=suite_id).order_by('sort')

    @staticmethod
    async def get_by_section(section_id: str) -> list[TestCaseModel]:
        return await TestCaseModel.filter(section_id=section_id).order_by('sort')

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
            'external_id': testcase.external_id,
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
        # PATCH omits nullable fields by default.  `section_id: null` is the
        # one intentional exception: it moves a case to the suite's virtual
        # Default section without changing its suite.  Keep all other nulls
        # out of the update so existing callers can still omit fields safely.
        data = {
            key: value
            for key, value in data.items()
            if value is not None or key == 'section_id'
        }
        user_id = await get_user_id_by_token(token) if token else None
        async with in_transaction() as connection:
            testcase = await TestCaseModel.filter(id=testcase_id).using_db(connection).select_for_update().first()
            if not testcase:
                raise HTTPException(status_code=404, detail="Test case not found")
            if not data:
                return testcase
            await TestCaseModel.filter(id=testcase_id).using_db(connection).update(**data)
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
    async def delete(testcase_id: str) -> bool:
        await TestCaseService.get_by_id(testcase_id)
        from ..test_run.model import TestResultModel
        if await TestResultModel.filter(testcase_id=testcase_id).exists():
            # Preserve case/version/result snapshots for historical runs.
            await TestCaseModel.filter(id=testcase_id).update(status=TestCaseStatus.deprecated)
            await EmbeddingService.delete_embeddings('test_case', testcase_id)
            return True
        await TestCaseVersionModel.filter(testcase_id=testcase_id).delete()
        await TestCaseModel.filter(id=testcase_id).delete()
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
        from ..test_run.model import TestResultModel, TestRunModel

        q = TestResultModel.filter(testcase_id=testcase_id).prefetch_related('run').order_by('-created_at')
        result = await paginate(q, page, page_size)
        items = result['items']

        results = []
        for r in items:
            run = r.run
            results.append({
                'id': str(r.id),
                'run_id': str(run.id) if run else None,
                'run_name': run.name if run else None,
                'status': r.status,
                'duration_seconds': r.duration_seconds,
                'comment': r.comment,
                'executed_at': r.executed_at.isoformat() if r.executed_at else None,
                'created_at': r.created_at.isoformat() if r.created_at else None,
            })

        return {**result, 'items': results}

    @staticmethod
    async def _compute_next_sort(original):
        last = await TestCaseModel.filter(
            space_id=str(original.space_id),
            suite_id=original.suite_id,
            section_id=original.section_id
        ).order_by('-sort').first()
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
        create_kwargs = {
            'testcase_id': str(testcase.id),
            'version_number': version_number,
            'title': testcase.title,
            'text': testcase.text,
            'steps': testcase.steps,
            'expected_results': testcase.expected_results,
            'preconditions': testcase.preconditions,
            'postconditions': testcase.postconditions,
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

        sort = await TestCaseService._compute_next_sort(original)
        new_short_name = TestCaseService._generate_copy_short_name(original.short_name)

        duplicated = await TestCaseModel.create(
            title=f"{original.title} (Copy)",
            text=original.text,
            steps=original.steps,
            expected_results=original.expected_results,
            preconditions=original.preconditions,
            postconditions=original.postconditions,
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
        )

        await TestCaseService._create_test_case_version(duplicated, user_id)
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
        fields = ('title', 'text', 'steps', 'expected_results', 'preconditions', 'postconditions')
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
            await TestCaseModel.filter(id=testcase_id).using_db(connection).update(
                title=version.title,
                text=version.text,
                steps=version.steps,
                expected_results=version.expected_results,
                preconditions=version.preconditions,
                postconditions=version.postconditions,
            )
            restored = await TestCaseModel.filter(id=testcase_id).using_db(connection).first()
            await TestCaseService._create_test_case_version(
                restored, user_id, next_version=True, connection=connection
            )
        await TestCaseService._index_test_case_for_search(restored)
        return restored
