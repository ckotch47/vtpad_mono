from fastapi import HTTPException
from starlette.requests import Request
import hashlib
import json

from typing import Optional, List
from datetime import datetime, timezone

from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from .model import TestRunModel, TestResultModel, TestRunStatus, TestResultStatus
from .dto import *
from ..common.crypto import get_user_id_by_token
from ..common.pagination import paginate
from ..common.right_guard import check_user_into_space


class TestRunService:
    @staticmethod
    async def _resolve_testcases_for_run(dto: TestRunCreateDto):
        """Resolve exactly one source, always scoped to active cases in its space."""
        from ..test_case.model import TestCaseModel, TestCaseStatus

        has_explicit_cases = bool(dto.testcase_ids)
        source_count = sum(bool(value) for value in (dto.suite_id, dto.plan_id, has_explicit_cases))
        if source_count != 1:
            raise HTTPException(
                status_code=422,
                detail="Exactly one test run source is required: suite_id, plan_id, or testcase_ids",
            )

        if dto.suite_id:
            from ..test_suite.model import TestSuiteModel
            suite = await TestSuiteModel.get_or_none(id=dto.suite_id, space_id=dto.space_id)
            if not suite:
                raise HTTPException(status_code=404, detail="Test suite not found in space")
            testcases = await TestCaseModel.filter(
                suite_id=dto.suite_id,
                space_id=dto.space_id,
                status=TestCaseStatus.active,
            ).prefetch_related('section').order_by('section__sort', 'sort')
            source = {'type': 'suite', 'id': str(suite.id), 'name': suite.name}
        elif dto.plan_id:
            from ..test_plan.service import TestPlanService
            plan = await TestPlanService.get_by_id(dto.plan_id)
            if str(plan.space_id) != str(dto.space_id):
                raise HTTPException(status_code=404, detail="Test plan not found in space")
            plan_cases = await TestPlanService.get_cases(dto.plan_id)
            active_cases = [
                testcase for testcase in plan_cases
                if str(testcase.space_id) == str(dto.space_id)
                and testcase.status == TestCaseStatus.active
            ]
            testcases = active_cases
            source = {'type': 'plan', 'id': str(plan.id), 'name': plan.name}
        else:
            requested_ids = list(dict.fromkeys(dto.testcase_ids or []))
            testcases = await TestCaseModel.filter(
                id__in=requested_ids,
                space_id=dto.space_id,
                status=TestCaseStatus.active,
            ).prefetch_related('section')
            testcase_by_id = {str(testcase.id): testcase for testcase in testcases}
            if len(testcase_by_id) != len(requested_ids):
                raise HTTPException(
                    status_code=422,
                    detail="Every selected testcase must exist in the space and be active",
                )
            testcases = [testcase_by_id[testcase_id] for testcase_id in requested_ids]
            source = {'type': 'selected_cases', 'id': None, 'name': None}

        if not testcases:
            raise HTTPException(status_code=422, detail="The selected source has no active testcases")
        return source, testcases

    @staticmethod
    def _build_case_snapshot(testcase, version=None):
        # The run snapshot always reflects the case at selection time.  Some
        # legacy version rows were written before the corresponding update, so
        # they are useful as identifiers but must not replace current content.
        fields_source = testcase
        return {
            'testcase_id': str(testcase.id),
            'testcase_version_id': str(version.id) if version else None,
            'version_number': version.version_number if version else None,
            'title': fields_source.title,
            'text': fields_source.text,
            'steps': fields_source.steps,
            'expected_results': fields_source.expected_results,
            'preconditions': fields_source.preconditions,
            'postconditions': fields_source.postconditions,
            'type': testcase.type.value if hasattr(testcase.type, 'value') else testcase.type,
            'status': testcase.status.value if hasattr(testcase.status, 'value') else testcase.status,
            'short_name': testcase.short_name,
            'link': testcase.link,
            'suite_id': str(testcase.suite_id) if testcase.suite_id else None,
            'section': {
                'id': str(testcase.section.id),
                'name': testcase.section.name,
            } if getattr(testcase, 'section', None) else None,
            'captured_at': datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _selection_hash(source: dict, snapshots: list[dict]) -> str:
        payload = {
            'source': source,
            'testcases': [
                {
                    'testcase_id': snapshot['testcase_id'],
                    'testcase_version_id': snapshot['testcase_version_id'],
                    'version_number': snapshot['version_number'],
                    'title': snapshot['title'],
                    'text': snapshot['text'],
                    'steps': snapshot['steps'],
                    'expected_results': snapshot['expected_results'],
                    'preconditions': snapshot['preconditions'],
                    'postconditions': snapshot['postconditions'],
                    'type': snapshot['type'],
                    'status': snapshot['status'],
                    'suite_id': snapshot['suite_id'],
                    'section': snapshot['section'],
                }
                for snapshot in snapshots
            ],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        ).hexdigest()

    @staticmethod
    async def _resolve_selection(dto: TestRunCreateDto):
        from ..test_case.model import TestCaseVersionModel

        source, testcases = await TestRunService._resolve_testcases_for_run(dto)
        versions = await TestCaseVersionModel.filter(
            testcase_id__in=[str(testcase.id) for testcase in testcases]
        ).order_by('testcase_id', '-version_number')
        latest_versions = {}
        for version in versions:
            latest_versions.setdefault(str(version.testcase_id), version)
        snapshots = [
            TestRunService._build_case_snapshot(
                testcase, latest_versions.get(str(testcase.id))
            )
            for testcase in testcases
        ]
        return source, testcases, snapshots, TestRunService._selection_hash(source, snapshots)

    @staticmethod
    async def preview(dto: TestRunCreateDto) -> dict:
        source, _testcases, snapshots, source_hash = await TestRunService._resolve_selection(dto)
        return {
            'source': source,
            'source_hash': source_hash,
            'total': len(snapshots),
            'testcases': [
                {
                    'id': snapshot['testcase_id'],
                    'version_id': snapshot['testcase_version_id'],
                    'version_number': snapshot['version_number'],
                    'title': snapshot['title'],
                    'section': snapshot['section'],
                }
                for snapshot in snapshots
            ],
        }

    @staticmethod
    async def _create_results_for_run(run_id: str, testcases, snapshots, connection=None):
        for tc, snapshot in zip(testcases, snapshots):
            create_kwargs = {
                'run_id': run_id,
                'testcase_id': str(tc.id),
                'testcase_version_id': snapshot['testcase_version_id'],
                'testcase_snapshot': snapshot,
                'status': TestResultStatus.not_run,
            }
            if connection is not None:
                create_kwargs['using_db'] = connection
            await TestResultModel.create(
                **create_kwargs,
            )

    @staticmethod
    async def create(dto: TestRunCreateDto, token: str) -> TestRunModel:
        user_id = await get_user_id_by_token(token)

        source, testcases, snapshots, source_hash = await TestRunService._resolve_selection(dto)
        if dto.source_hash and dto.source_hash != source_hash:
            raise HTTPException(
                status_code=409,
                detail="Test run source changed; refresh the preview before creating the run",
            )

        async with in_transaction() as connection:
            run = await TestRunModel.create(
                name=dto.name,
                description=dto.description,
                space_id=dto.space_id,
                suite_id=dto.suite_id,
                plan_id=dto.plan_id,
                milestone_id=dto.milestone_id,
                environment_id=dto.environment_id,
                status=TestRunStatus.draft,
                created_by_id=user_id,
                source_snapshot={
                    'source': source,
                    'source_hash': source_hash,
                    'total': len(snapshots),
                    'captured_at': datetime.now(timezone.utc).isoformat(),
                },
                using_db=connection,
            )
            await TestRunService._create_results_for_run(
                str(run.id), testcases, snapshots, connection
            )

        return run

    @staticmethod
    async def get_by_space(
        space_id: str,
        page: int = 1,
        page_size: int = 25,
        sort_by: Optional[str] = 'created_at',
        sort_order: Optional[str] = 'desc',
        search: Optional[str] = None,
        milestone_id: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> dict:
        q = TestRunModel.filter(space_id=space_id)
        if search:
            q = q.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if milestone_id:
            q = q.filter(milestone_id=milestone_id)
        if environment_id:
            q = q.filter(environment_id=environment_id)

        q = q.prefetch_related('milestone', 'environment')
        result = await paginate(q, page, page_size, sort_by, sort_order)
        items = result['items']

        return {
            **result,
            'items': [
                {
                    'id': str(r.id),
                    'name': r.name,
                    'description': r.description,
                    'status': r.status,
                    'suite_id': str(r.suite_id) if r.suite_id else None,
                    'plan_id': str(r.plan_id) if r.plan_id else None,
                    'milestone_id': str(r.milestone_id) if r.milestone_id else None,
                    'milestone': {
                        'id': str(r.milestone.id),
                        'title': r.milestone.title,
                        'status': r.milestone.status,
                    } if r.milestone else None,
                    'environment_id': str(r.environment_id) if r.environment_id else None,
                    'environment': {
                        'id': str(r.environment.id),
                        'name': r.environment.name,
                    } if r.environment else None,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                }
                for r in items
            ],
        }

    @staticmethod
    async def get_by_id(run_id: str) -> TestRunModel:
        run = await TestRunModel.get_or_none(id=run_id).prefetch_related('milestone', 'environment')
        if not run:
            raise HTTPException(status_code=404, detail="Test run not found")
        return run

    @staticmethod
    def _compute_result_stats(results):
        return {
            'total': len(results),
            'not_run': sum(1 for r in results if r.status == TestResultStatus.not_run),
            'passed': sum(1 for r in results if r.status == TestResultStatus.passed),
            'failed': sum(1 for r in results if r.status == TestResultStatus.failed),
            'blocked': sum(1 for r in results if r.status == TestResultStatus.blocked),
            'skipped': sum(1 for r in results if r.status == TestResultStatus.skipped),
        }

    @staticmethod
    def _serialize_result(r):
        testcase = r.testcase
        snapshot = r.testcase_snapshot
        if snapshot:
            testcase_data = {
                'id': snapshot['testcase_id'],
                'title': snapshot['title'],
                'type': snapshot.get('type'),
                'section': snapshot.get('section'),
                'version_id': snapshot.get('testcase_version_id'),
                'version_number': snapshot.get('version_number'),
                'text': snapshot.get('text'),
                'steps': snapshot.get('steps'),
                'expected_results': snapshot.get('expected_results'),
                'preconditions': snapshot.get('preconditions'),
                'postconditions': snapshot.get('postconditions'),
                'is_snapshot': True,
            }
        else:
            testcase_data = {
                'id': str(testcase.id),
                'title': testcase.title,
                'type': testcase.type,
                'section': {
                    'id': str(testcase.section.id),
                    'name': testcase.section.name,
                } if testcase.section else None,
                'is_snapshot': False,
            } if testcase else None
        return {
            'id': str(r.id),
            'status': r.status,
            'duration_seconds': r.duration_seconds,
            'comment': r.comment,
            'testcase_id': str(r.testcase_id),
            'testcase': testcase_data,
            'testcase_snapshot': snapshot,
            'executed_at': r.executed_at.isoformat() if r.executed_at else None,
        }

    @staticmethod
    async def get_with_results(run_id: str) -> dict:
        run = await TestRunService.get_by_id(run_id)
        results = await TestResultModel.filter(run_id=run_id).prefetch_related('testcase', 'testcase__section').order_by('testcase__section__sort', 'testcase__sort')
        stats = TestRunService._compute_result_stats(results)
        results_data = [TestRunService._serialize_result(r) for r in results]
        return {
            'run': {
                'id': str(run.id),
                'name': run.name,
                'description': run.description,
                'status': run.status,
                'suite_id': str(run.suite_id) if run.suite_id else None,
                'plan_id': str(run.plan_id) if run.plan_id else None,
                'milestone_id': str(run.milestone_id) if run.milestone_id else None,
                'milestone': {
                    'id': str(run.milestone.id),
                    'title': run.milestone.title,
                    'status': run.milestone.status,
                } if run.milestone else None,
                'environment_id': str(run.environment_id) if run.environment_id else None,
                'environment': {
                    'id': str(run.environment.id),
                    'name': run.environment.name,
                } if run.environment else None,
                'created_at': run.created_at.isoformat() if run.created_at else None,
                'started_at': run.started_at.isoformat() if run.started_at else None,
                'completed_at': run.completed_at.isoformat() if run.completed_at else None,
                'source_snapshot': run.source_snapshot,
            },
            'stats': stats,
            'results': results_data,
        }

    @staticmethod
    async def update(run_id: str, dto: TestRunUpdateDto) -> TestRunModel:
        await TestRunService.get_by_id(run_id)
        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}
        if 'status' in data:
            raise HTTPException(
                status_code=422,
                detail="Use the start and complete actions to change test run status",
            )
        if data:
            await TestRunModel.filter(id=run_id).update(**data)
        return await TestRunService.get_by_id(run_id)

    @staticmethod
    async def start(run_id: str) -> TestRunModel:
        run = await TestRunService.get_by_id(run_id)
        if run.status != TestRunStatus.draft:
            raise HTTPException(status_code=400, detail="Run is not in draft status")
        await TestRunModel.filter(id=run_id).update(status=TestRunStatus.active, started_at=datetime.now(timezone.utc))
        return await TestRunService.get_by_id(run_id)

    @staticmethod
    async def complete(run_id: str) -> TestRunModel:
        run = await TestRunService.get_by_id(run_id)
        if run.status != TestRunStatus.active:
            raise HTTPException(status_code=400, detail="Run is not active")
        await TestRunModel.filter(id=run_id).update(status=TestRunStatus.completed, completed_at=datetime.now(timezone.utc))
        return await TestRunService.get_by_id(run_id)

    @staticmethod
    async def delete(run_id: str) -> bool:
        await TestRunService.get_by_id(run_id)
        await TestResultModel.filter(run_id=run_id).delete()
        await TestRunModel.filter(id=run_id).delete()
        return True


class TestResultService:
    @staticmethod
    def _parse_result_status(target_status: str) -> TestResultStatus:
        try:
            return TestResultStatus(target_status)
        except ValueError:
            raise HTTPException(status_code=422, detail="Unsupported test result status")

    @staticmethod
    async def update_result(result_id: str, dto: TestResultUpdateDto, token: str, request: Request) -> TestResultModel:
        user_id = await get_user_id_by_token(token)
        async with in_transaction() as connection:
            result = await TestResultModel.filter(id=result_id).using_db(connection).select_for_update().first()
            if not result:
                raise HTTPException(status_code=404, detail="Test result not found")
            run = await TestRunModel.filter(id=result.run_id).using_db(connection).select_for_update().first()
            if not run:
                raise HTTPException(status_code=404, detail="Test run not found")
            await check_user_into_space(str(run.space_id), request)
            if run.status != TestRunStatus.active:
                raise HTTPException(status_code=409, detail="Test results may be changed only in an active run")
            data = dto.model_dump(exclude_unset=True)
            if data.get('status') is None:
                data.pop('status', None)
            if 'status' in data:
                target_status = TestResultService._parse_result_status(data['status'])
                data['status'] = target_status
                if target_status != result.status:
                    if target_status == TestResultStatus.not_run:
                        data['executed_by_id'] = None
                        data['executed_at'] = None
                    else:
                        data['executed_by_id'] = user_id
                        data['executed_at'] = datetime.now(timezone.utc)
            if not data:
                return result
            await TestResultModel.filter(id=result_id).using_db(connection).update(**data)
        return await TestResultModel.get(id=result_id)

    @staticmethod
    async def bulk_update(dto: TestResultBulkUpdateDto, token: str, request: Request) -> int:
        user_id = await get_user_id_by_token(token)
        result_ids = list(dict.fromkeys(dto.result_ids))
        if not result_ids:
            raise HTTPException(status_code=422, detail="At least one result is required")

        async with in_transaction() as connection:
            results = await TestResultModel.filter(id__in=result_ids).using_db(connection).select_for_update()
            if len(results) != len(result_ids):
                raise HTTPException(status_code=404, detail="One or more test results were not found")
            run_ids = {str(result.run_id) for result in results}
            if len(run_ids) != 1:
                raise HTTPException(status_code=422, detail="Bulk update accepts results from exactly one run")
            run = await TestRunModel.filter(id=next(iter(run_ids))).using_db(connection).select_for_update().first()
            if not run:
                raise HTTPException(status_code=404, detail="Test run not found")
            await check_user_into_space(str(run.space_id), request)
            if run.status != TestRunStatus.active:
                raise HTTPException(status_code=409, detail="Test results may be changed only in an active run")
            target_status = TestResultService._parse_result_status(dto.status)
            update_data = {'status': target_status}
            await TestResultModel.filter(id__in=result_ids).using_db(connection).update(**update_data)
            changed_ids = [result.id for result in results if result.status != target_status]
            if changed_ids:
                if target_status == TestResultStatus.not_run:
                    attribution_data = {'executed_by_id': None, 'executed_at': None}
                else:
                    attribution_data = {'executed_by_id': user_id, 'executed_at': datetime.now(timezone.utc)}
                await TestResultModel.filter(id__in=changed_ids).using_db(connection).update(**attribution_data)
            return len(result_ids)
