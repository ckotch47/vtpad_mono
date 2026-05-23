from fastapi import HTTPException
from typing import Optional, List
from datetime import datetime

from .model import TestRunModel, TestResultModel, TestRunStatus, TestResultStatus
from .dto import *
from ..common.crypto import get_user_id_by_token


class TestRunService:
    @staticmethod
    async def create(dto: TestRunCreateDto, token: str) -> TestRunModel:
        user_id = await get_user_id_by_token(token)

        run = await TestRunModel.create(
            name=dto.name,
            description=dto.description,
            space_id=dto.space_id,
            suite_id=dto.suite_id,
            milestone_id=dto.milestone_id,
            environment_id=dto.environment_id,
            status=TestRunStatus.draft,
            created_by_id=user_id,
        )

        # Create test results
        from ..test_case.model import TestCaseModel, TestCaseVersionModel

        if dto.testcase_ids:
            testcases = await TestCaseModel.filter(id__in=dto.testcase_ids).all()
        elif dto.suite_id:
            testcases = await TestCaseModel.filter(suite_id=dto.suite_id).all()
        else:
            testcases = await TestCaseModel.filter(space_id=dto.space_id).all()

        for tc in testcases:
            last_version = await TestCaseVersionModel.filter(testcase_id=str(tc.id)).order_by('-version_number').first()
            await TestResultModel.create(
                run_id=str(run.id),
                testcase_id=str(tc.id),
                testcase_version_id=str(last_version.id) if last_version else None,
                status=TestResultStatus.not_run,
            )

        return run

    @staticmethod
    async def get_by_space(space_id: str) -> list[TestRunModel]:
        return await TestRunModel.filter(space_id=space_id).order_by('-created_at')

    @staticmethod
    async def get_by_id(run_id: str) -> TestRunModel:
        run = await TestRunModel.get_or_none(id=run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Test run not found")
        return run

    @staticmethod
    async def get_with_results(run_id: str) -> dict:
        run = await TestRunService.get_by_id(run_id)
        results = await TestResultModel.filter(run_id=run_id).prefetch_related('testcase')
        stats = {
            'total': len(results),
            'not_run': sum(1 for r in results if r.status == TestResultStatus.not_run),
            'passed': sum(1 for r in results if r.status == TestResultStatus.passed),
            'failed': sum(1 for r in results if r.status == TestResultStatus.failed),
            'blocked': sum(1 for r in results if r.status == TestResultStatus.blocked),
            'skipped': sum(1 for r in results if r.status == TestResultStatus.skipped),
        }
        return {
            'run': run,
            'stats': stats,
            'results': results,
        }

    @staticmethod
    async def update(run_id: str, dto: TestRunUpdateDto) -> TestRunModel:
        await TestRunService.get_by_id(run_id)
        data = dto.model_dump(exclude_unset=True)
        if data:
            await TestRunModel.filter(id=run_id).update(**data)
        return await TestRunService.get_by_id(run_id)

    @staticmethod
    async def start(run_id: str) -> TestRunModel:
        run = await TestRunService.get_by_id(run_id)
        if run.status != TestRunStatus.draft:
            raise HTTPException(status_code=400, detail="Run is not in draft status")
        await TestRunModel.filter(id=run_id).update(status=TestRunStatus.active, started_at=datetime.utcnow())
        return await TestRunService.get_by_id(run_id)

    @staticmethod
    async def complete(run_id: str) -> TestRunModel:
        run = await TestRunService.get_by_id(run_id)
        if run.status != TestRunStatus.active:
            raise HTTPException(status_code=400, detail="Run is not active")
        await TestRunModel.filter(id=run_id).update(status=TestRunStatus.completed, completed_at=datetime.utcnow())
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
        data['executed_by_id'] = user_id
        data['executed_at'] = datetime.utcnow()
        await TestResultModel.filter(id=result_id).update(**data)
        return await TestResultModel.get(id=result_id)

    @staticmethod
    async def bulk_update(dto: TestResultBulkUpdateDto, token: str) -> int:
        user_id = await get_user_id_by_token(token)
        count = await TestResultModel.filter(id__in=dto.result_ids).update(
            status=dto.status,
            executed_by_id=user_id,
            executed_at=datetime.utcnow(),
        )
        return count
