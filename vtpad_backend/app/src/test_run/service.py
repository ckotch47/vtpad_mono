from fastapi import HTTPException
from typing import Optional, List
from datetime import datetime, timezone

from tortoise.expressions import Q

from .model import TestRunModel, TestResultModel, TestStepResultModel, TestRunStatus, TestResultStatus
from .dto import *
from ..common.crypto import get_user_id_by_token


class TestRunService:
    @staticmethod
    async def create(dto: TestRunCreateDto, token: str) -> TestRunModel:
        user_id = await get_user_id_by_token(token)

        # Determine testcase_ids if plan_id is provided
        suite_id = dto.suite_id
        testcase_ids = dto.testcase_ids

        if dto.plan_id:
            from ..test_plan.service import TestPlanService
            plan_cases = await TestPlanService.get_cases(dto.plan_id)
            testcase_ids = [str(tc.id) for tc in plan_cases]

        run = await TestRunModel.create(
            name=dto.name,
            description=dto.description,
            space_id=dto.space_id,
            suite_id=suite_id,
            plan_id=dto.plan_id,
            milestone_id=dto.milestone_id,
            environment_id=dto.environment_id,
            status=TestRunStatus.draft,
            created_by_id=user_id,
        )

        # Create test results
        from ..test_case.model import TestCaseModel, TestCaseVersionModel

        if testcase_ids:
            testcases = await TestCaseModel.filter(id__in=testcase_ids).all()
        elif suite_id:
            testcases = await TestCaseModel.filter(suite_id=suite_id).all()
        else:
            testcases = await TestCaseModel.filter(space_id=dto.space_id).all()

        for tc in testcases:
            last_version = await TestCaseVersionModel.filter(testcase_id=str(tc.id)).order_by('-version_number').first()
            result = await TestResultModel.create(
                run_id=str(run.id),
                testcase_id=str(tc.id),
                testcase_version_id=str(last_version.id) if last_version else None,
                status=TestResultStatus.not_run,
            )

            # Create step-level results from testcase steps (if steps exist)
            if tc.steps:
                # Simple split by newlines for now; can be enhanced with structured steps
                step_lines = [s.strip() for s in tc.steps.split('\n') if s.strip()]
                for idx, step_text in enumerate(step_lines):
                    await TestStepResultModel.create(
                        result_id=str(result.id),
                        step_index=idx,
                        step_text=step_text,
                        status=TestResultStatus.not_run,
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

        order = f'{"-" if sort_order == "desc" else ""}{sort_by}'
        q = q.order_by(order)

        total = await q.count()
        items = await q.offset((page - 1) * page_size).limit(page_size).prefetch_related('milestone', 'environment').all()

        return {
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
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

    @staticmethod
    async def get_by_id(run_id: str) -> TestRunModel:
        run = await TestRunModel.get_or_none(id=run_id).prefetch_related('milestone', 'environment')
        if not run:
            raise HTTPException(status_code=404, detail="Test run not found")
        return run

    @staticmethod
    async def get_with_results(run_id: str) -> dict:
        run = await TestRunService.get_by_id(run_id)
        results = await TestResultModel.filter(run_id=run_id).prefetch_related('testcase', 'testcase__section').order_by('testcase__section__sort', 'testcase__sort')
        stats = {
            'total': len(results),
            'not_run': sum(1 for r in results if r.status == TestResultStatus.not_run),
            'passed': sum(1 for r in results if r.status == TestResultStatus.passed),
            'failed': sum(1 for r in results if r.status == TestResultStatus.failed),
            'blocked': sum(1 for r in results if r.status == TestResultStatus.blocked),
            'skipped': sum(1 for r in results if r.status == TestResultStatus.skipped),
        }
        results_data = []
        for r in results:
            testcase = r.testcase
            results_data.append({
                'id': str(r.id),
                'status': r.status,
                'duration_seconds': r.duration_seconds,
                'comment': r.comment,
                'testcase_id': str(r.testcase_id),
                'testcase': {
                    'id': str(testcase.id),
                    'title': testcase.title,
                    'type': testcase.type,
                    'section': {
                        'id': str(testcase.section.id),
                        'name': testcase.section.name,
                    } if testcase.section else None,
                } if testcase else None,
                'executed_at': r.executed_at.isoformat() if r.executed_at else None,
            })
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
            },
            'stats': stats,
            'results': results_data,
        }

    @staticmethod
    async def update(run_id: str, dto: TestRunUpdateDto) -> TestRunModel:
        await TestRunService.get_by_id(run_id)
        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}
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
    async def update_result(result_id: str, dto: TestResultUpdateDto, token: str) -> TestResultModel:
        user_id = await get_user_id_by_token(token)
        result = await TestResultModel.get_or_none(id=result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Test result not found")

        data = dto.model_dump(exclude_unset=True)
        data = {k: v for k, v in data.items() if v is not None}
        data['executed_by_id'] = user_id
        data['executed_at'] = datetime.now(timezone.utc)
        await TestResultModel.filter(id=result_id).update(**data)
        return await TestResultModel.get(id=result_id)

    @staticmethod
    async def bulk_update(dto: TestResultBulkUpdateDto, token: str) -> int:
        user_id = await get_user_id_by_token(token)
        count = await TestResultModel.filter(id__in=dto.result_ids).update(
            status=dto.status,
            executed_by_id=user_id,
            executed_at=datetime.now(timezone.utc),
        )
        return count

    @staticmethod
    async def get_step_results(result_id: str) -> list:
        result = await TestResultModel.get_or_none(id=result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Test result not found")
        steps = await TestStepResultModel.filter(result_id=result_id).order_by('step_index').all()
        return [
            {
                'id': str(s.id),
                'step_index': s.step_index,
                'step_text': s.step_text,
                'status': s.status,
                'comment': s.comment,
                'screenshot_url': s.screenshot_url,
            }
            for s in steps
        ]

    @staticmethod
    async def update_step_results(result_id: str, dto: TestStepResultBulkUpdateDto, token: str) -> list:
        result = await TestResultModel.get_or_none(id=result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Test result not found")

        for step_dto in dto.steps:
            await TestStepResultModel.update_or_create(
                result_id=result_id,
                step_index=step_dto.step_index,
                defaults={
                    'step_text': step_dto.step_text,
                    'status': step_dto.status,
                    'comment': step_dto.comment,
                    'screenshot_url': step_dto.screenshot_url,
                }
            )

        return await TestResultService.get_step_results(result_id)
