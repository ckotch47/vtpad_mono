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
    async def get_space_trend(space_id: str, days: int = 30) -> list:
        """Return daily pass/fail counts for the last N days."""
        from tortoise.functions import Count

        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get all completed runs in range with their results
        runs = await TestRunModel.filter(
            space_id=space_id,
            status='completed',
            completed_at__gte=start_date
        ).order_by('completed_at').all()

        trend = []
        for run in runs:
            if not run.completed_at:
                continue
            results = await TestResultModel.filter(run_id=str(run.id)).all()
            trend.append({
                'date': run.completed_at.strftime('%Y-%m-%d'),
                'run_id': str(run.id),
                'run_name': run.name,
                'total': len(results),
                'passed': sum(1 for r in results if r.status == TestResultStatus.passed),
                'failed': sum(1 for r in results if r.status == TestResultStatus.failed),
                'blocked': sum(1 for r in results if r.status == TestResultStatus.blocked),
                'skipped': sum(1 for r in results if r.status == TestResultStatus.skipped),
            })

        return trend

    @staticmethod
    async def get_top_failed_cases(space_id: str, limit: int = 10) -> list:
        """Return cases with the most failures across all runs."""
        # Get all failed results grouped by case
        failed_results = await TestResultModel.filter(
            run__space_id=space_id,
            status=TestResultStatus.failed
        ).prefetch_related('testcase').all()

        case_failures = {}
        for r in failed_results:
            tc = r.testcase
            if not tc:
                continue
            tc_id = str(tc.id)
            if tc_id not in case_failures:
                case_failures[tc_id] = {
                    'id': tc_id,
                    'title': tc.title,
                    'short_name': tc.short_name,
                    'type': tc.type,
                    'fail_count': 0,
                    'last_failed': None,
                }
            case_failures[tc_id]['fail_count'] += 1
            if r.executed_at:
                current = case_failures[tc_id]['last_failed']
                if current is None or r.executed_at > current:
                    case_failures[tc_id]['last_failed'] = r.executed_at

        sorted_cases = sorted(case_failures.values(), key=lambda x: x['fail_count'], reverse=True)[:limit]
        for c in sorted_cases:
            if c['last_failed']:
                c['last_failed'] = c['last_failed'].isoformat()

        return sorted_cases

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
