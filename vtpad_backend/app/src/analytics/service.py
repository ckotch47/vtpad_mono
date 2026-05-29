from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from typing import Optional

from tortoise.expressions import Q

from ..test_run.model import TestRunModel, TestResultModel, TestResultStatus
from ..test_case.model import TestCaseModel, TestCaseType
from ..test_suite.model import TestSuiteModel


class AnalyticsService:
    @staticmethod
    async def get_space_stats(space_id: str) -> dict:
        total_cases = await TestCaseModel.filter(space_id=space_id).count()
        total_suites = await TestSuiteModel.filter(space_id=space_id).count()
        total_runs = await TestRunModel.filter(space_id=space_id).count()
        active_runs = await TestRunModel.filter(space_id=space_id, status='active').count()

        # Case type breakdown
        manual_count = await TestCaseModel.filter(space_id=space_id, type=TestCaseType.manual).count()
        checklist_count = await TestCaseModel.filter(space_id=space_id, type=TestCaseType.checklist).count()
        automated_count = await TestCaseModel.filter(space_id=space_id, type=TestCaseType.automated).count()

        # Latest run results
        latest_results = await TestResultModel.filter(
            run__space_id=space_id
        ).order_by('-created_at').limit(100).all()

        passed = sum(1 for r in latest_results if r.status == TestResultStatus.passed)
        failed = sum(1 for r in latest_results if r.status == TestResultStatus.failed)
        blocked = sum(1 for r in latest_results if r.status == TestResultStatus.blocked)
        skipped = sum(1 for r in latest_results if r.status == TestResultStatus.skipped)
        not_run = sum(1 for r in latest_results if r.status == TestResultStatus.not_run)

        return {
            'cases': {
                'total': total_cases,
                'manual': manual_count,
                'checklist': checklist_count,
                'automated': automated_count,
            },
            'suites': total_suites,
            'runs': {
                'total': total_runs,
                'active': active_runs,
            },
            'latest_results': {
                'total': len(latest_results),
                'passed': passed,
                'failed': failed,
                'blocked': blocked,
                'skipped': skipped,
                'not_run': not_run,
            }
        }

    @staticmethod
    async def get_suite_coverage(suite_id: str) -> dict:
        total = await TestCaseModel.filter(suite_id=suite_id).count()
        if total == 0:
            return {'total': 0, 'manual': 0, 'checklist': 0, 'automated': 0, 'percentages': {}}

        manual = await TestCaseModel.filter(suite_id=suite_id, type=TestCaseType.manual).count()
        checklist = await TestCaseModel.filter(suite_id=suite_id, type=TestCaseType.checklist).count()
        automated = await TestCaseModel.filter(suite_id=suite_id, type=TestCaseType.automated).count()

        return {
            'total': total,
            'manual': manual,
            'checklist': checklist,
            'automated': automated,
            'percentages': {
                'manual': round(manual / total * 100, 1),
                'checklist': round(checklist / total * 100, 1),
                'automated': round(automated / total * 100, 1),
            }
        }
