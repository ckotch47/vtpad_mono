from fastapi import HTTPException
from starlette.requests import Request
import hashlib
import json
import uuid

from typing import Any, Optional, List
from datetime import datetime, timezone

from tortoise.expressions import Q
from tortoise import Tortoise
from tortoise.transactions import in_transaction
from tortoise.exceptions import IntegrityError

from .model import (
    TestRunModel, TestResultModel, TestRunTimerIntervalModel, TestRunStatus,
    TestResultStatus, TestResultBugCreateOperationModel, TestResultBugLinkModel,
)
from .dto import *
from ..common.crypto import get_user_id_by_token
from ..common.pagination import paginate
from ..common.right_guard import check_user_into_space
from ..bug.model import BugsModel
from ..bug.service import BugsService
from ..bug.dto.create_bug_dto import CreateBugDto
from ..bug.enum import StateBugEnum


class TestRunService:
    @staticmethod
    async def _resolve_testcases_for_run(dto: TestRunCreateDto):
        """Resolve exactly one source, scoped to test cases in its space."""
        from ..test_case.model import TestCaseModel

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
            ).prefetch_related('section').order_by('section__sort', 'sort')
            source = {'type': 'suite', 'id': str(suite.id), 'name': suite.name}
        elif dto.plan_id:
            from ..test_plan.service import TestPlanService
            plan = await TestPlanService.get_by_id(dto.plan_id)
            if str(plan.space_id) != str(dto.space_id):
                raise HTTPException(status_code=404, detail="Test plan not found in space")
            plan_cases = await TestPlanService.get_cases(dto.plan_id)
            testcases = [
                testcase for testcase in plan_cases
                if str(testcase.space_id) == str(dto.space_id)
            ]
            source = {'type': 'plan', 'id': str(plan.id), 'name': plan.name}
        else:
            requested_ids = list(dict.fromkeys(dto.testcase_ids or []))
            testcases = await TestCaseModel.filter(
                id__in=requested_ids,
                space_id=dto.space_id,
            ).prefetch_related('section')
            testcase_by_id = {str(testcase.id): testcase for testcase in testcases}
            if len(testcase_by_id) != len(requested_ids):
                raise HTTPException(
                    status_code=422,
                    detail="Every selected testcase must exist in the space",
                )
            testcases = [testcase_by_id[testcase_id] for testcase_id in requested_ids]
            source = {'type': 'selected_cases', 'id': None, 'name': None}

        if not testcases:
            raise HTTPException(status_code=422, detail="The selected source has no testcases")
        return source, testcases

    @staticmethod
    def _build_case_snapshot(testcase, version=None, location=None):
        # The run snapshot always reflects the case at selection time.  Some
        # legacy version rows were written before the corresponding update, so
        # they are useful as identifiers but must not replace current content.
        fields_source = testcase
        location = location or {}
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
            'estimated_duration_seconds': fields_source.estimated_duration_seconds,
            'type': testcase.type.value if hasattr(testcase.type, 'value') else testcase.type,
            'status': testcase.status.value if hasattr(testcase.status, 'value') else testcase.status,
            'short_name': testcase.short_name,
            'link': testcase.link,
            'suite_id': location.get('suite_id'),
            'suite_name': location.get('suite_name'),
            'section_path': location.get('section_path', []),
            'section': location.get('section'),
            'captured_at': datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    async def _resolve_case_locations(testcases):
        """Return only suite/section labels proven to belong to each testcase space."""
        from ..section.model import SectionModel
        from ..test_suite.model import TestSuiteModel

        direct_section_ids = {
            str(testcase.section_id)
            for testcase in testcases
            if getattr(testcase, 'section_id', None)
        }
        direct_sections = await SectionModel.filter(id__in=list(direct_section_ids)).all() if direct_section_ids else []
        direct_by_id = {str(section.id): section for section in direct_sections}
        candidate_suite_ids = {
            str(testcase.suite_id)
            for testcase in testcases
            if getattr(testcase, 'suite_id', None)
        }
        candidate_suite_ids.update(
            str(section.suite_id) for section in direct_sections if section.suite_id
        )
        suites = await TestSuiteModel.filter(id__in=list(candidate_suite_ids)).all() if candidate_suite_ids else []
        suites_by_id = {str(suite.id): suite for suite in suites}
        all_sections = await SectionModel.filter(suite_id__in=list(candidate_suite_ids)).all() if candidate_suite_ids else []
        sections_by_id = {str(section.id): section for section in all_sections}
        sections_by_id.update(direct_by_id)

        locations = {}
        for testcase in testcases:
            direct = direct_by_id.get(str(testcase.section_id)) if testcase.section_id else None
            suite_id = str(testcase.suite_id) if testcase.suite_id else (
                str(direct.suite_id) if direct and direct.suite_id else None
            )
            suite = suites_by_id.get(suite_id) if suite_id else None
            if not suite or str(suite.space_id) != str(testcase.space_id):
                locations[str(testcase.id)] = {
                    'suite_id': None,
                    'suite_name': None,
                    'section_path': [],
                    'section': None,
                }
                continue

            path = []
            current = direct
            visited = set()
            valid_path = True
            while current:
                current_id = str(current.id)
                if current_id in visited or str(current.suite_id) != suite_id:
                    valid_path = False
                    break
                visited.add(current_id)
                path.append({'id': current_id, 'name': current.name, 'sort': current.sort})
                parent_id = str(current.parent_id) if current.parent_id else None
                if not parent_id:
                    break
                current = sections_by_id.get(parent_id)
                if current is None:
                    valid_path = False
                    break
            if not valid_path:
                locations[str(testcase.id)] = {
                    'suite_id': None,
                    'suite_name': None,
                    'section_path': [],
                    'section': None,
                }
                continue

            path.reverse()
            locations[str(testcase.id)] = {
                'suite_id': suite_id,
                'suite_name': suite.name,
                'section_path': path,
                'section': {'id': str(direct.id), 'name': direct.name} if direct else None,
            }
        return locations

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
                    'estimated_duration_seconds': snapshot['estimated_duration_seconds'],
                    'type': snapshot['type'],
                    'status': snapshot['status'],
                    'suite_id': snapshot['suite_id'],
                    'section': snapshot['section'],
                    'suite_name': snapshot['suite_name'],
                    'section_path': snapshot['section_path'],
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
        locations = await TestRunService._resolve_case_locations(testcases)
        snapshots = []
        for testcase in testcases:
            snapshots.append(TestRunService._build_case_snapshot(
                testcase,
                latest_versions.get(str(testcase.id)),
                location=locations.get(str(testcase.id)),
            ))
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
                    'suite_id': snapshot['suite_id'],
                    'suite_name': snapshot['suite_name'],
                    'section_path': snapshot['section_path'],
                    'estimated_duration_seconds': snapshot['estimated_duration_seconds'],
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

        q = q.prefetch_related('milestone', 'environment', 'created_by')
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
                    'created_by_id': str(r.created_by_id) if r.created_by_id else None,
                    'created_by': {
                        'id': str(r.created_by.id),
                        'username': r.created_by.username,
                    } if r.created_by else None,
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
        known_durations = [
            r.duration_seconds
            for r in results
            if r.duration_seconds is not None and r.duration_seconds >= 0
        ]
        return {
            'total': len(results),
            'not_run': sum(1 for r in results if r.status == TestResultStatus.not_run),
            'passed': sum(1 for r in results if r.status == TestResultStatus.passed),
            'failed': sum(1 for r in results if r.status == TestResultStatus.failed),
            'blocked': sum(1 for r in results if r.status == TestResultStatus.blocked),
            'skipped': sum(1 for r in results if r.status == TestResultStatus.skipped),
            'duration_seconds_total': sum(known_durations),
            'duration_measured_count': len(known_durations),
            'duration_unmeasured_count': len(results) - len(known_durations),
        }

    @staticmethod
    def _serialize_result(r, legacy_location=None, linked_bugs=None):
        testcase = r.testcase
        snapshot = r.testcase_snapshot
        if snapshot:
            testcase_data = {
                'id': snapshot['testcase_id'],
                'title': snapshot['title'],
                'type': snapshot.get('type'),
                'section': snapshot.get('section'),
                'suite_id': snapshot.get('suite_id'),
                'suite_name': snapshot.get('suite_name'),
                'section_path': snapshot.get('section_path') or [],
                'version_id': snapshot.get('testcase_version_id'),
                'version_number': snapshot.get('version_number'),
                'text': snapshot.get('text'),
                'steps': snapshot.get('steps'),
                'expected_results': snapshot.get('expected_results'),
                'preconditions': snapshot.get('preconditions'),
                'postconditions': snapshot.get('postconditions'),
                'estimated_duration_seconds': snapshot.get('estimated_duration_seconds'),
                'is_snapshot': True,
            }
        else:
            legacy_location = legacy_location or {}
            testcase_data = {
                'id': str(testcase.id),
                'title': testcase.title,
                'type': testcase.type,
                'section': legacy_location.get('section'),
                'suite_id': legacy_location.get('suite_id'),
                'suite_name': legacy_location.get('suite_name'),
                'section_path': legacy_location.get('section_path', []),
                'estimated_duration_seconds': None,
                'is_snapshot': False,
            } if testcase else None
        return {
            'id': str(r.id),
            'status': r.status,
            'duration_seconds': (
                r.duration_seconds if r.duration_seconds is not None and r.duration_seconds >= 0 else None
            ),
            'comment': r.comment,
            'linked_bug_ids': r.linked_bug_ids or [],
            'linked_bug_ids_raw': r.linked_bug_ids,
            'linked_bugs': linked_bugs or [],
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
        legacy_cases = [
            result.testcase for result in results
            if not result.testcase_snapshot and result.testcase
        ]
        legacy_locations = await TestRunService._resolve_case_locations(legacy_cases) if legacy_cases else {}
        bug_links_by_result = await TestResultService._get_linked_bugs([str(result.id) for result in results])
        results_data = []
        for result in results:
            location = legacy_locations.get(str(result.testcase.id)) if not result.testcase_snapshot and result.testcase else None
            results_data.append(TestRunService._serialize_result(
                result, location, bug_links_by_result.get(str(result.id), [])
            ))
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
                'timer': await TestRunService.get_timer(run.id),
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
    def _timer_summary(run: TestRunModel, intervals: list[TestRunTimerIntervalModel], now: datetime) -> dict:
        if not intervals:
            state = 'not_started' if run.status == TestRunStatus.draft else 'untracked'
            if run.status == TestRunStatus.completed:
                state = 'untracked'
            calendar_seconds = None
            if run.started_at:
                end_at = run.completed_at or now
                calendar_seconds = max(0, int((end_at - run.started_at).total_seconds()))
            return {
                'state': state,
                'calendar_seconds': calendar_seconds,
                'active_seconds': None,
                'paused_seconds': None,
                'interval_count': 0,
            }

        active_seconds = sum(
            max(0, int(((interval.ended_at or now) - interval.started_at).total_seconds()))
            for interval in intervals
        )
        calendar_seconds = None
        if run.started_at:
            end_at = run.completed_at or now
            calendar_seconds = max(0, int((end_at - run.started_at).total_seconds()))
        paused_seconds = (
            max(0, calendar_seconds - active_seconds)
            if calendar_seconds is not None else None
        )
        if run.status == TestRunStatus.completed:
            state = 'stopped'
        elif intervals[-1].ended_at is None:
            state = 'running'
        else:
            state = 'paused'
        return {
            'state': state,
            'calendar_seconds': calendar_seconds,
            'active_seconds': active_seconds,
            'paused_seconds': paused_seconds,
            'interval_count': len(intervals),
        }

    @staticmethod
    async def get_timer(run_id: str) -> dict:
        normalized_run_id = str(run_id)
        timers = await TestRunService.get_timers([normalized_run_id])
        if normalized_run_id not in timers:
            raise HTTPException(status_code=404, detail="Test run not found")
        return timers[normalized_run_id]

    @staticmethod
    async def get_timers(run_ids: list[str]) -> dict[str, dict]:
        unique_ids = list(dict.fromkeys(str(run_id) for run_id in run_ids if run_id))
        if not unique_ids:
            return {}

        async with in_transaction() as connection:
            await connection.execute_query("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            runs = await TestRunModel.filter(id__in=unique_ids).using_db(connection)
            intervals = await TestRunTimerIntervalModel.filter(
                run_id__in=unique_ids
            ).using_db(connection).order_by('run_id', 'started_at')

        intervals_by_run: dict[str, list[TestRunTimerIntervalModel]] = {}
        for interval in intervals:
            intervals_by_run.setdefault(str(interval.run_id), []).append(interval)

        now = datetime.now(timezone.utc)
        return {
            str(run.id): TestRunService._timer_summary(
                run, intervals_by_run.get(str(run.id), []), now
            )
            for run in runs
        }

    @staticmethod
    async def _transition_timer(run_id: str, token: str, action: str) -> TestRunModel:
        actor_id = await get_user_id_by_token(token)
        async with in_transaction() as connection:
            run = await TestRunModel.filter(id=run_id).using_db(connection).select_for_update().first()
            if not run:
                raise HTTPException(status_code=404, detail="Test run not found")
            now = datetime.now(timezone.utc)
            open_interval = await TestRunTimerIntervalModel.filter(
                run_id=run_id, ended_at__isnull=True
            ).using_db(connection).first()

            if action == 'start':
                if run.status != TestRunStatus.draft:
                    raise HTTPException(status_code=400, detail="Run is not in draft status")
                await TestRunModel.filter(id=run_id).using_db(connection).update(
                    status=TestRunStatus.active, started_at=now
                )
                await TestRunTimerIntervalModel.create(
                    run_id=run_id, started_at=now, actor_id=actor_id, using_db=connection
                )
            elif action == 'pause':
                if run.status != TestRunStatus.active:
                    raise HTTPException(status_code=409, detail="Run is not active")
                if open_interval:
                    await TestRunTimerIntervalModel.filter(id=open_interval.id).using_db(connection).update(
                        ended_at=now
                    )
                elif not await TestRunTimerIntervalModel.filter(run_id=run_id).using_db(connection).exists():
                    raise HTTPException(status_code=409, detail="Timer is not tracked for this legacy run")
            elif action == 'resume':
                if run.status != TestRunStatus.active:
                    raise HTTPException(status_code=409, detail="Run is not active")
                if not open_interval:
                    if not await TestRunTimerIntervalModel.filter(run_id=run_id).using_db(connection).exists():
                        raise HTTPException(status_code=409, detail="Timer is not tracked for this legacy run")
                    await TestRunTimerIntervalModel.create(
                        run_id=run_id, started_at=now, actor_id=actor_id, using_db=connection
                    )
            elif action == 'complete':
                if run.status != TestRunStatus.active:
                    raise HTTPException(status_code=400, detail="Run is not active")
                if open_interval:
                    await TestRunTimerIntervalModel.filter(id=open_interval.id).using_db(connection).update(
                        ended_at=now
                    )
                await TestRunModel.filter(id=run_id).using_db(connection).update(
                    status=TestRunStatus.completed, completed_at=now
                )
        return await TestRunService.get_by_id(run_id)

    @staticmethod
    async def start(run_id: str, token: str) -> TestRunModel:
        return await TestRunService._transition_timer(run_id, token, 'start')

    @staticmethod
    async def pause(run_id: str, token: str) -> TestRunModel:
        return await TestRunService._transition_timer(run_id, token, 'pause')

    @staticmethod
    async def resume(run_id: str, token: str) -> TestRunModel:
        return await TestRunService._transition_timer(run_id, token, 'resume')

    @staticmethod
    async def complete(run_id: str, token: str) -> TestRunModel:
        return await TestRunService._transition_timer(run_id, token, 'complete')

    @staticmethod
    async def delete(run_id: str) -> bool:
        async with in_transaction() as connection:
            run = await TestRunModel.filter(id=run_id).using_db(connection).select_for_update().first()
            if not run:
                raise HTTPException(status_code=404, detail="Test run not found")
            await TestRunTimerIntervalModel.filter(run_id=run_id).using_db(connection).delete()
            await TestResultModel.filter(run_id=run_id).using_db(connection).delete()
            await TestRunModel.filter(id=run_id).using_db(connection).delete()
        return True


class TestResultService:
    @staticmethod
    async def _serialize_updated_result(result: TestResultModel) -> dict[str, Any]:
        return {
            "id": str(result.id),
            "status": result.status.value if hasattr(result.status, "value") else result.status,
            "duration_seconds": result.duration_seconds,
            "comment": result.comment,
            "linked_bug_ids": result.linked_bug_ids or [],
            "linked_bug_ids_raw": result.linked_bug_ids,
            "linked_bugs": await TestResultService._load_result_bug_links(str(result.id)),
            "run_id": str(result.run_id),
            "testcase_id": str(result.testcase_id),
            "testcase_version_id": str(result.testcase_version_id) if result.testcase_version_id else None,
            "testcase_snapshot": result.testcase_snapshot,
            "executed_by_id": str(result.executed_by_id) if result.executed_by_id else None,
            "executed_at": result.executed_at.isoformat() if result.executed_at else None,
            "created_at": result.created_at.isoformat() if result.created_at else None,
            "updated_at": result.updated_at.isoformat() if result.updated_at else None,
        }

    @staticmethod
    def _parse_result_status(target_status: str) -> TestResultStatus:
        try:
            return TestResultStatus(target_status)
        except ValueError:
            raise HTTPException(status_code=422, detail="Unsupported test result status")

    @staticmethod
    async def _lock_result_run(result_id: str, connection: Any) -> tuple[TestRunModel, TestResultModel]:
        result_ref = await TestResultModel.filter(id=result_id).using_db(connection).first()
        if not result_ref:
            raise HTTPException(status_code=404, detail="Test result not found")
        run = await TestRunModel.filter(id=result_ref.run_id).using_db(connection).select_for_update().first()
        if not run:
            raise HTTPException(status_code=404, detail="Test run not found")
        result = await TestResultModel.filter(id=result_id).using_db(connection).select_for_update().first()
        if not result:
            raise HTTPException(status_code=404, detail="Test result not found")
        return run, result

    @staticmethod
    async def _get_linked_bugs(result_ids: list[str]) -> dict[str, list[dict[str, Any]]]:
        if not result_ids:
            return {}
        conn = Tortoise.get_connection("default")
        rows = await conn.execute_query_dict(
            "SELECT l.result_id, b.link_uuid, b.short_name, b.title "
            "FROM test_result_bug_link l JOIN bugsmodel b ON b.link_uuid = l.bug_uuid "
            "WHERE l.result_id = ANY($1::uuid[]) ORDER BY b.short_name NULLS LAST, b.link_uuid",
            [result_ids],
        )
        linked: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            linked.setdefault(str(row["result_id"]), []).append({
                "id": str(row["link_uuid"]), "short_name": row["short_name"], "title": row["title"]
            })
        return linked

    @staticmethod
    async def _load_result_bug_links(result_id: str) -> list[dict[str, Any]]:
        return (await TestResultService._get_linked_bugs([result_id])).get(result_id, [])

    @staticmethod
    async def _validate_linkable_bug(
        run: TestRunModel, bug_uuid: uuid.UUID, connection: Any
    ) -> BugsModel:
        bug = await BugsModel.filter(link_uuid=bug_uuid, spaces_id=run.space_id).using_db(connection).first()
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found in run space")
        if run.status != TestRunStatus.active:
            raise HTTPException(status_code=409, detail="Test results may be changed only in an active run")
        return bug

    @staticmethod
    async def link_bug_id(result_id: str, bug_uuid: uuid.UUID, request: Request) -> dict[str, Any]:
        async with in_transaction() as connection:
            run, result = await TestResultService._lock_result_run(result_id, connection)
            await check_user_into_space(str(run.space_id), request)
            bug = await TestResultService._validate_linkable_bug(run, bug_uuid, connection)
            await TestResultBugLinkModel.get_or_create(
                result_id=result.id, bug_uuid=bug.link_uuid, using_db=connection
            )
        return {
            "id": str(result.id), "linked_bug_ids": result.linked_bug_ids or [],
            "linked_bug_ids_raw": result.linked_bug_ids,
            "linked_bugs": await TestResultService._load_result_bug_links(str(result.id)),
        }

    @staticmethod
    async def unlink_bug_id(result_id: str, bug_uuid: uuid.UUID, request: Request) -> dict[str, Any]:
        async with in_transaction() as connection:
            run, result = await TestResultService._lock_result_run(result_id, connection)
            await check_user_into_space(str(run.space_id), request)
            await TestResultService._validate_linkable_bug(run, bug_uuid, connection)
            await TestResultBugLinkModel.filter(
                result_id=result.id, bug_uuid=bug_uuid
            ).using_db(connection).delete()
        return {
            "id": str(result.id), "linked_bug_ids": result.linked_bug_ids or [],
            "linked_bug_ids_raw": result.linked_bug_ids,
            "linked_bugs": await TestResultService._load_result_bug_links(str(result.id)),
        }

    @staticmethod
    async def _legacy_short_name_bug_id(
        run: TestRunModel, short_name: str, connection: Any
    ) -> uuid.UUID:
        matches = await BugsModel.filter(
            short_name=short_name, spaces_id=run.space_id
        ).using_db(connection).values_list("link_uuid", flat=True)
        if not matches:
            raise HTTPException(status_code=404, detail="Bug not found in run space")
        if len(matches) != 1:
            raise HTTPException(status_code=409, detail="Bug short name is ambiguous in run space; use bug UUID")
        return matches[0]

    @staticmethod
    async def link_bug(result_id: str, bug_short_name: str, request: Request) -> dict[str, Any]:
        async with in_transaction() as connection:
            run, result = await TestResultService._lock_result_run(result_id, connection)
            await check_user_into_space(str(run.space_id), request)
            bug_id = await TestResultService._legacy_short_name_bug_id(run, bug_short_name, connection)
            await TestResultService._validate_linkable_bug(run, bug_id, connection)
            await TestResultBugLinkModel.get_or_create(
                result_id=result.id, bug_uuid=bug_id, using_db=connection
            )
        return {
            "id": str(result.id), "linked_bug_ids": result.linked_bug_ids or [],
            "linked_bug_ids_raw": result.linked_bug_ids,
            "linked_bugs": await TestResultService._load_result_bug_links(str(result.id)),
        }

    @staticmethod
    async def unlink_bug(result_id: str, bug_short_name: str, request: Request) -> dict[str, Any]:
        async with in_transaction() as connection:
            run, result = await TestResultService._lock_result_run(result_id, connection)
            await check_user_into_space(str(run.space_id), request)
            bug_id = await TestResultService._legacy_short_name_bug_id(run, bug_short_name, connection)
            await TestResultService._validate_linkable_bug(run, bug_id, connection)
            await TestResultBugLinkModel.filter(
                result_id=result.id, bug_uuid=bug_id
            ).using_db(connection).delete()
        return {
            "id": str(result.id), "linked_bug_ids": result.linked_bug_ids or [],
            "linked_bug_ids_raw": result.linked_bug_ids,
            "linked_bugs": await TestResultService._load_result_bug_links(str(result.id)),
        }

    @staticmethod
    async def update_legacy_bug_reference(
        result_id: str, bug_short_name: str, request: Request, *, add: bool
    ) -> dict[str, Any]:
        """Preserve the established MCP short-name tools' legacy JSON behavior."""
        async with in_transaction() as connection:
            run, result = await TestResultService._lock_result_run(result_id, connection)
            await check_user_into_space(str(run.space_id), request)
            await TestResultService._legacy_short_name_bug_id(run, bug_short_name, connection)
            if run.status != TestRunStatus.active:
                raise HTTPException(status_code=409, detail="Test results may be changed only in an active run")
            identifiers = list(result.linked_bug_ids or [])
            if add:
                if bug_short_name not in identifiers:
                    identifiers.append(bug_short_name)
            else:
                identifiers = [value for value in identifiers if value != bug_short_name]
            await TestResultModel.filter(id=result.id).using_db(connection).update(linked_bug_ids=identifiers)
            result.linked_bug_ids = identifiers
        return {
            "id": str(result.id),
            "linked_bug_ids": result.linked_bug_ids or [],
            "linked_bug_ids_raw": result.linked_bug_ids,
            "linked_bugs": await TestResultService._load_result_bug_links(str(result.id)),
        }

    @staticmethod
    def _bug_payload_hash(payload: TestResultBugCreateDto) -> str:
        canonical = json.dumps(
            {"title": payload.title, "text": payload.text, "steps": payload.steps},
            sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _operation_replay(
        operation: TestResultBugCreateOperationModel, actor_id: str, result_id: str, payload_hash: str
    ) -> bool:
        if (str(operation.actor_id) != str(actor_id) or str(operation.result_id) != str(result_id)
                or operation.payload_hash != payload_hash):
            raise HTTPException(status_code=409, detail="Operation id was already used for a different request")
        return True

    @staticmethod
    async def create_and_link_bug(
        result_id: str,
        dto: TestResultBugCreateDto,
        token: str,
        request: Request,
    ) -> dict[str, Any]:
        actor_id = await get_user_id_by_token(token)
        payload_hash = TestResultService._bug_payload_hash(dto)
        try:
            async with in_transaction() as connection:
                run, result = await TestResultService._lock_result_run(result_id, connection)
                await check_user_into_space(str(run.space_id), request)
                operation = await TestResultBugCreateOperationModel.filter(
                    operation_id=dto.operation_id
                ).using_db(connection).first()
                if operation:
                    TestResultService._operation_replay(operation, actor_id, result_id, payload_hash)
                    bug = await BugsModel.get_or_none(link_uuid=operation.bug_uuid).using_db(connection)
                    if not bug:
                        raise HTTPException(status_code=410, detail="The bug from this operation was deleted")
                else:
                    if run.status != TestRunStatus.active:
                        raise HTTPException(status_code=409, detail="Test results may be changed only in an active run")
                    create_dto = CreateBugDto(
                        title=dto.title,
                        text=dto.text,
                        steps=dto.steps,
                        space_id=run.space_id,
                        state=StateBugEnum.open,
                    )
                    bug = await BugsService.create_bug_in_transaction(
                        create_dto, {"id": actor_id}, connection
                    )
                    await TestResultBugLinkModel.get_or_create(
                        result_id=result.id, bug_uuid=bug.link_uuid, using_db=connection
                    )
                    await TestResultBugCreateOperationModel.create(
                        operation_id=dto.operation_id,
                        actor_id=actor_id,
                        result_id=result.id,
                        payload_hash=payload_hash,
                        bug_uuid=bug.link_uuid,
                        using_db=connection,
                    )
            return {
                "id": str(result.id),
                "linked_bug_ids": result.linked_bug_ids or [],
                "linked_bug_ids_raw": result.linked_bug_ids,
                "linked_bugs": await TestResultService._load_result_bug_links(str(result.id)),
                "bug_uuid": str(bug.link_uuid),
                "bug_short_name": bug.short_name,
                "bug": await BugsService.get_bug_detail(str(bug.id)),
            }
        except IntegrityError:
            operation = await TestResultBugCreateOperationModel.get_or_none(operation_id=dto.operation_id)
            if not operation:
                raise
            TestResultService._operation_replay(operation, actor_id, result_id, payload_hash)
            bug = await BugsModel.get_or_none(link_uuid=operation.bug_uuid)
            if not bug:
                raise HTTPException(status_code=410, detail="The bug from this operation was deleted")
            result = await TestResultModel.get(id=result_id)
            return {
                "id": str(result.id),
                "linked_bug_ids": result.linked_bug_ids or [],
                "linked_bug_ids_raw": result.linked_bug_ids,
                "linked_bugs": await TestResultService._load_result_bug_links(str(result.id)),
                "bug_uuid": str(bug.link_uuid),
                "bug_short_name": bug.short_name,
                "bug": await BugsService.get_bug_detail(str(bug.id)),
            }

    @staticmethod
    async def update_result(result_id: str, dto: TestResultUpdateDto, token: str, request: Request) -> dict[str, Any]:
        user_id = await get_user_id_by_token(token)
        async with in_transaction() as connection:
            result_ref = await TestResultModel.filter(id=result_id).using_db(connection).first()
            if not result_ref:
                raise HTTPException(status_code=404, detail="Test result not found")
            run = await TestRunModel.filter(id=result_ref.run_id).using_db(connection).select_for_update().first()
            if not run:
                raise HTTPException(status_code=404, detail="Test run not found")
            result = await TestResultModel.filter(id=result_id).using_db(connection).select_for_update().first()
            if not result:
                raise HTTPException(status_code=404, detail="Test result not found")
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
            if 'linked_bug_ids' in data:
                identifiers = data['linked_bug_ids']
                if identifiers is None:
                    identifiers = None
                elif identifiers:
                    matching = await BugsModel.filter(
                        short_name__in=identifiers, spaces_id=run.space_id
                    ).using_db(connection).values_list("short_name", flat=True)
                    if set(matching) != set(identifiers):
                        raise HTTPException(status_code=422, detail="Every legacy bug short name must belong to the run space")
                if identifiers is not None and any(not value for value in identifiers):
                    raise HTTPException(status_code=422, detail="Every linked bug must belong to the run space")
                data['linked_bug_ids'] = identifiers
            if not data:
                return await TestResultService._serialize_updated_result(result)
            await TestResultModel.filter(id=result_id).using_db(connection).update(**data)
        updated = await TestResultModel.get(id=result_id)
        return await TestResultService._serialize_updated_result(updated)

    @staticmethod
    async def bulk_update(dto: TestResultBulkUpdateDto, token: str, request: Request) -> int:
        user_id = await get_user_id_by_token(token)
        result_ids = list(dict.fromkeys(dto.result_ids))
        if not result_ids:
            raise HTTPException(status_code=422, detail="At least one result is required")

        async with in_transaction() as connection:
            result_refs = await TestResultModel.filter(id__in=result_ids).using_db(connection)
            if len(result_refs) != len(result_ids):
                raise HTTPException(status_code=404, detail="One or more test results were not found")
            run_ids = {str(result.run_id) for result in result_refs}
            if len(run_ids) != 1:
                raise HTTPException(status_code=422, detail="Bulk update accepts results from exactly one run")
            run = await TestRunModel.filter(id=next(iter(run_ids))).using_db(connection).select_for_update().first()
            if not run:
                raise HTTPException(status_code=404, detail="Test run not found")
            results = await TestResultModel.filter(id__in=result_ids).using_db(connection).order_by('id').select_for_update()
            if len(results) != len(result_ids):
                raise HTTPException(status_code=404, detail="One or more test results were not found")
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
