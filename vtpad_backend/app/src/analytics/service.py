import json

from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from typing import Optional

from tortoise.expressions import Q

from ..test_run.model import TestRunModel, TestResultModel, TestResultStatus
from ..test_case.model import TestCaseModel, TestCaseType
from ..test_suite.model import TestSuiteModel


class AnalyticsService:
    RESULT_LINKS_PER_BUG_LIMIT = 25

    @staticmethod
    def _bug_link_filters(
        run_id: str | None = None,
        suite_id: str | None = None,
        status: str | None = None,
    ) -> tuple[str, list[str]]:
        """Build only value-parameterized predicates for UUID-link analytics."""
        predicates: list[str] = []
        params: list[str] = []
        if run_id is not None:
            params.append(run_id)
            predicates.append(f"scoped.run_id = ${len(params) + 1}::uuid")
        if suite_id is not None:
            params.append(suite_id)
            predicates.append(f"scoped.suite_id = ${len(params) + 1}")
        if status is not None:
            params.append(status)
            predicates.append(f"scoped.status_group = ${len(params) + 1}")
        return (" AND " + " AND ".join(predicates) if predicates else "", params)

    @staticmethod
    def _scoped_bug_links_cte(filter_sql: str = '') -> str:
        # Scope runs before bug joins and all aggregations. Legacy JSON links are
        # intentionally excluded; only explicit UUID link rows are authoritative.
        return """
            WITH scoped AS (
                SELECT l.result_id, r.run_id, tr.name AS run_name,
                       l.bug_uuid, b.short_name, b.title,
                       CASE WHEN upper(b.state) IN ('OPEN', 'FIXED', 'REOPEN')
                            THEN upper(b.state) ELSE 'OTHER' END AS status_group,
                       r.testcase_snapshot->>'suite_id' AS suite_id,
                       (r.testcase_snapshot IS NULL) AS missing_snapshot
                FROM test_run tr
                JOIN test_result r ON r.run_id = tr.id
                JOIN test_result_bug_link l ON l.result_id = r.id
                JOIN bugsmodel b ON b.link_uuid = l.bug_uuid
                               AND b.spaces_id = tr.space_id
                WHERE tr.space_id = $1::uuid
            ), filtered AS (
                SELECT * FROM scoped WHERE TRUE""" + filter_sql + """
            )
        """

    @staticmethod
    async def get_linked_bugs(
        space_id: str,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        run_id: str | None = None,
        suite_id: str | None = None,
    ) -> dict:
        from tortoise import Tortoise

        conn = Tortoise.get_connection('default')
        summary_rows = await conn.execute_query_dict(
            AnalyticsService._scoped_bug_links_cte() + """
            SELECT COUNT(DISTINCT bug_uuid)::int AS unique_bug_count,
                   COUNT(*)::int AS link_count,
                   COUNT(DISTINCT bug_uuid) FILTER (WHERE status_group = 'OPEN')::int AS open_count,
                   COUNT(DISTINCT bug_uuid) FILTER (WHERE status_group = 'FIXED')::int AS fixed_count,
                   COUNT(DISTINCT bug_uuid) FILTER (WHERE status_group = 'REOPEN')::int AS reopen_count,
                   COUNT(DISTINCT bug_uuid) FILTER (WHERE status_group = 'OTHER')::int AS other_count
            FROM scoped
            """, [space_id])

        filter_sql, filter_params = AnalyticsService._bug_link_filters(run_id, suite_id, status)
        filtered_cte = AnalyticsService._scoped_bug_links_cte(filter_sql)
        params: list[object] = [space_id, *filter_params]
        count_rows = await conn.execute_query_dict(
            filtered_cte + "SELECT COUNT(*)::int AS total FROM (SELECT bug_uuid FROM filtered GROUP BY bug_uuid) q",
            params,
        )
        params.extend([page_size, (page - 1) * page_size])
        item_query = filtered_cte + f"""
            , ranked AS (
                SELECT filtered.*,
                       row_number() OVER (
                           PARTITION BY bug_uuid ORDER BY run_id, result_id
                       ) AS link_rank
                FROM filtered
            ), grouped AS (
                SELECT bug_uuid, short_name, title, status_group,
                       COUNT(*)::int AS link_count,
                       jsonb_agg(jsonb_build_object('run_id', run_id, 'result_id', result_id)
                                 ORDER BY run_id, result_id)
                           FILTER (WHERE link_rank <= {AnalyticsService.RESULT_LINKS_PER_BUG_LIMIT}) AS result_links
                FROM ranked
                GROUP BY bug_uuid, short_name, title, status_group
            ), paged AS (
                SELECT * FROM grouped
                ORDER BY link_count DESC, short_name NULLS LAST, title, bug_uuid
                LIMIT ${len(params) - 1}::int OFFSET ${len(params)}::int
            )
            SELECT p.bug_uuid, p.short_name, p.title, p.status_group AS status,
                   p.link_count, p.result_links
            FROM paged p
            ORDER BY p.link_count DESC, p.short_name NULLS LAST, p.title, p.bug_uuid
        """
        item_rows = await conn.execute_query_dict(item_query, params)
        summary = summary_rows[0] if summary_rows else {}
        items = []
        for row in item_rows:
            result_links = row['result_links']
            if isinstance(result_links, str):
                result_links = json.loads(result_links)
            result_links = result_links or []
            items.append({
                **row,
                'bug_uuid': str(row['bug_uuid']),
                'result_links': [
                    {'run_id': str(link['run_id']), 'result_id': str(link['result_id'])}
                    for link in result_links
                ],
                'result_links_truncated': row['link_count'] > AnalyticsService.RESULT_LINKS_PER_BUG_LIMIT,
            })
        return {
            'summary': {
                'unique_bug_count': summary.get('unique_bug_count', 0),
                'link_count': summary.get('link_count', 0),
                'statuses': {
                    'OPEN': summary.get('open_count', 0),
                    'FIXED': summary.get('fixed_count', 0),
                    'REOPEN': summary.get('reopen_count', 0),
                    'OTHER': summary.get('other_count', 0),
                },
            },
            'items': items,
            'page': page,
            'page_size': page_size,
            'total': count_rows[0]['total'] if count_rows else 0,
        }

    @staticmethod
    async def get_linked_bugs_by_run(
        space_id: str,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        run_id: str | None = None,
        suite_id: str | None = None,
    ) -> dict:
        from tortoise import Tortoise

        conn = Tortoise.get_connection('default')
        filter_sql, filter_params = AnalyticsService._bug_link_filters(run_id, suite_id, status)
        cte = AnalyticsService._scoped_bug_links_cte(filter_sql)
        params: list[object] = [space_id, *filter_params]
        totals = await conn.execute_query_dict(cte + "SELECT COUNT(*)::int AS total FROM (SELECT run_id FROM filtered GROUP BY run_id) q", params)
        params.extend([page_size, (page - 1) * page_size])
        rows = await conn.execute_query_dict(
            cte + """
            SELECT run_id, run_name, COUNT(DISTINCT bug_uuid)::int AS unique_bug_count,
                   COUNT(*)::int AS link_count
            FROM filtered GROUP BY run_id, run_name
            ORDER BY COUNT(*) DESC, run_id
            LIMIT $""" + str(len(params) - 1) + "::int OFFSET $" + str(len(params)) + "::int",
            params,
        )
        return {'items': [{**row, 'run_id': str(row['run_id'])} for row in rows],
                'page': page, 'page_size': page_size,
                'total': totals[0]['total'] if totals else 0}

    @staticmethod
    async def get_linked_bugs_by_suite(
        space_id: str,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        run_id: str | None = None,
        suite_id: str | None = None,
    ) -> dict:
        from tortoise import Tortoise

        conn = Tortoise.get_connection('default')
        filter_sql, filter_params = AnalyticsService._bug_link_filters(run_id, suite_id, status)
        cte = AnalyticsService._scoped_bug_links_cte(filter_sql)
        # Text comparison avoids casting untrusted historical JSON text to UUID.
        grouped = """
            , grouped AS (
                SELECT s.id AS suite_id, f.missing_snapshot,
                       COUNT(DISTINCT f.bug_uuid)::int AS unique_bug_count,
                       COUNT(*)::int AS link_count
                FROM filtered f
                LEFT JOIN test_suite s
                  ON s.id::text = f.suite_id AND s.space_id = $1::uuid
                GROUP BY s.id, f.missing_snapshot
            )
        """
        params: list[object] = [space_id, *filter_params]
        totals = await conn.execute_query_dict(cte + grouped + "SELECT COUNT(*)::int AS total FROM grouped", params)
        params.extend([page_size, (page - 1) * page_size])
        rows = await conn.execute_query_dict(
            cte + grouped + """
            SELECT g.suite_id, s.name AS suite_name,
                   CASE WHEN g.missing_snapshot THEN 'legacy_missing_snapshot'
                        WHEN g.suite_id IS NULL THEN 'unknown_suite'
                        ELSE 'snapshot' END AS attribution,
                   CASE WHEN g.missing_snapshot THEN 'Unknown / legacy'
                        WHEN g.suite_id IS NULL THEN 'Unknown suite'
                        ELSE s.name END AS display_name,
                   g.unique_bug_count, g.link_count
            FROM grouped g
            LEFT JOIN test_suite s ON s.id = g.suite_id AND s.space_id = $1::uuid
            ORDER BY g.link_count DESC, g.suite_id NULLS LAST, g.missing_snapshot DESC
            LIMIT $""" + str(len(params) - 1) + "::int OFFSET $" + str(len(params)) + "::int",
            params,
        )
        items = []
        for row in rows:
            legacy = row['attribution'] == 'legacy_missing_snapshot'
            items.append({
                'suite_id': row['suite_id'],
                'suite_name': row['display_name'],
                'attribution': row['attribution'],
                'unique_bug_count': row['unique_bug_count'],
                'link_count': row['link_count'],
            })
            if items[-1]['suite_id'] is not None:
                items[-1]['suite_id'] = str(items[-1]['suite_id'])
            elif legacy:
                items[-1]['suite_id'] = None
        return {'items': items, 'page': page, 'page_size': page_size,
                'total': totals[0]['total'] if totals else 0}

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
    async def get_top_failed(space_id: str, limit: int = 10) -> list:
        from tortoise.functions import Count
        from ..test_case.model import TestCaseModel

        # Count failed results per testcase in this space
        results = await TestResultModel.filter(
            run__space_id=space_id,
            status=TestResultStatus.failed
        ).group_by('testcase_id').annotate(fail_count=Count('id')).order_by('-fail_count').limit(limit).values('testcase_id', 'fail_count')

        testcase_ids = [r['testcase_id'] for r in results]
        testcases = await TestCaseModel.filter(id__in=testcase_ids).all()
        tc_map = {str(tc.id): tc.title for tc in testcases}

        return [
            {
                'id': str(r['testcase_id']),
                'title': tc_map.get(str(r['testcase_id']), 'Unknown'),
                'fail_count': r['fail_count'],
            }
            for r in results
        ]

    @staticmethod
    async def get_trend(space_id: str, days: int = 30) -> list:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        runs = await TestRunModel.filter(
            space_id=space_id,
            status='completed',
            completed_at__gte=since
        ).order_by('completed_at').all()

        trend = []
        for run in runs:
            results = await TestResultModel.filter(run_id=str(run.id)).all()
            total = len(results)
            passed = sum(1 for r in results if r.status == TestResultStatus.passed)
            failed = sum(1 for r in results if r.status == TestResultStatus.failed)
            blocked = sum(1 for r in results if r.status == TestResultStatus.blocked)
            trend.append({
                'run_id': str(run.id),
                'run_name': run.name,
                'date': run.completed_at.strftime('%Y-%m-%d') if run.completed_at else '',
                'total': total,
                'passed': passed,
                'failed': failed,
                'blocked': blocked,
            })
        return trend

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
