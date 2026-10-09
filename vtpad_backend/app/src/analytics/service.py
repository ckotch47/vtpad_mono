import json

from fastapi import HTTPException
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from tortoise.expressions import Q

from ..test_run.model import TestRunModel, TestResultModel, TestResultStatus
from ..test_case.model import TestCaseModel, TestCaseType
from ..test_suite.model import TestSuiteModel


class AnalyticsService:
    RESULT_LINKS_PER_BUG_LIMIT = 25

    @staticmethod
    def _analytics_range(
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[date, date, datetime, datetime]:
        """Return inclusive UTC calendar dates and their half-open timestamp range."""
        today = datetime.now(timezone.utc).date()
        current_monday = today - timedelta(days=today.weekday())
        if start_date is None and end_date is None:
            start_date = current_monday - timedelta(weeks=12)
            end_date = current_monday - timedelta(days=1)
        elif start_date is None:
            end_date = end_date or today
            start_date = end_date - timedelta(days=30)
        elif end_date is None:
            end_date = today
        if end_date < start_date:
            raise HTTPException(status_code=422, detail='end_date must be on or after start_date')
        start_at = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
        end_at = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
        return start_date, end_date, start_at, end_at

    @staticmethod
    def _validate_suite_filter(suite_id: str | None) -> None:
        if suite_id is None:
            return
        try:
            import uuid
            uuid.UUID(str(suite_id))
        except (TypeError, ValueError, AttributeError) as exc:
            raise HTTPException(status_code=422, detail='suite_id must be a UUID') from exc

    @staticmethod
    async def get_quality_trends(
        space_id: str,
        suite_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        """Weekly outcome rate and recurrent failures, attributed from result snapshots."""
        from tortoise import Tortoise

        AnalyticsService._validate_suite_filter(suite_id)
        start_date, end_date, start_at, end_at = AnalyticsService._analytics_range(start_date, end_date)
        conn = Tortoise.get_connection('default')
        params: list[object] = [space_id, start_at, end_at]
        suite_filter = ''
        if suite_id is not None:
            params.append(suite_id)
            suite_filter = f' AND s.suite_id = ${len(params)}::uuid'

        # Resolve suite IDs only through a same-space join. A corrupt historical
        # snapshot can therefore never disclose or filter on a foreign suite ID.
        rate_rows = await conn.execute_query_dict(
            """
            WITH scoped AS (
                SELECT date_trunc('week', tr.completed_at AT TIME ZONE 'UTC')::date AS week_start,
                       s.id AS suite_id, s.name AS suite_name,
                       CASE WHEN s.id IS NULL THEN 'unknown_suite' ELSE 'suite' END AS attribution,
                       r.status
                FROM test_run tr
                JOIN test_result r ON r.run_id = tr.id
                LEFT JOIN test_suite s
                  ON s.id::text = r.testcase_snapshot->>'suite_id'
                 AND s.space_id = tr.space_id
                WHERE tr.space_id = $1::uuid
                  AND tr.status = 'completed'
                  AND tr.completed_at >= $2::timestamptz
                  AND tr.completed_at < $3::timestamptz
            ), counted AS (
                SELECT week_start, suite_id, suite_name, attribution,
                       COUNT(*) FILTER (WHERE status IN ('passed','failed','blocked','skipped'))::int AS denominator,
                       COUNT(*) FILTER (WHERE status = 'failed')::int AS failed,
                       COUNT(*)::int AS total_results,
                       COUNT(*) FILTER (WHERE status = 'not_run')::int AS not_run
                FROM scoped s
                WHERE TRUE""" + suite_filter + """
                GROUP BY week_start, suite_id, suite_name, attribution
            )
            SELECT * FROM counted ORDER BY week_start, suite_name NULLS LAST, attribution
            """,
            params,
        )

        params_recurrent: list[object] = [space_id, start_at, end_at]
        recurrent_filter = ''
        if suite_id is not None:
            params_recurrent.append(suite_id)
            recurrent_filter = f' AND s.id = ${len(params_recurrent)}::uuid'
        recurrent_rows = await conn.execute_query_dict(
            """
            WITH case_runs AS (
                SELECT DISTINCT tr.id AS run_id, tr.completed_at, s.id AS suite_id
                FROM test_run tr
                JOIN test_result r ON r.run_id = tr.id
                JOIN test_suite s
                  ON s.id::text = r.testcase_snapshot->>'suite_id'
                 AND s.space_id = tr.space_id
                WHERE tr.space_id = $1::uuid AND tr.status = 'completed'
                  AND tr.completed_at >= $2::timestamptz
                  AND tr.completed_at < $3::timestamptz""" + recurrent_filter + """
            ), ranked_runs AS (
                SELECT *, row_number() OVER (
                    PARTITION BY suite_id ORDER BY completed_at DESC, run_id DESC
                ) AS run_rank FROM case_runs
            ), selected_runs AS (
                SELECT * FROM ranked_runs WHERE run_rank <= 20
            ), failures AS (
                SELECT s.id AS suite_id, s.name AS suite_name,
                       r.testcase_id AS testcase_id,
                       COALESCE(r.testcase_snapshot->>'title', '(untitled snapshot)') AS testcase_title,
                       tr.id AS run_id, tr.name AS run_name, tr.completed_at, r.id AS result_id
                FROM selected_runs sr
                JOIN test_run tr ON tr.id = sr.run_id
                JOIN test_result r ON r.run_id = tr.id AND r.status = 'failed'
                JOIN test_suite s ON s.id = sr.suite_id AND s.space_id = tr.space_id
                WHERE r.testcase_snapshot IS NOT NULL
                  AND r.testcase_snapshot->>'suite_id' = s.id::text
            )
            SELECT suite_id, suite_name, testcase_id,
                   (array_agg(testcase_title ORDER BY completed_at DESC, run_id DESC, result_id))[1] AS testcase_title,
                   COUNT(DISTINCT run_id)::int AS failed_run_count,
                   jsonb_agg(jsonb_build_object(
                       'run_id', run_id, 'run_name', run_name,
                       'completed_at', completed_at, 'result_id', result_id
                   ) ORDER BY completed_at DESC, run_id DESC, result_id) AS failures
            FROM failures
            GROUP BY suite_id, suite_name, testcase_id
            HAVING COUNT(DISTINCT run_id) >= 2
            ORDER BY suite_name, testcase_title, testcase_id
            """,
            params_recurrent,
        )

        week_starts: list[date] = []
        cursor = start_date - timedelta(days=start_date.weekday())
        final_week = end_date - timedelta(days=end_date.weekday())
        while cursor <= final_week:
            week_starts.append(cursor)
            cursor += timedelta(weeks=1)
        by_suite: dict[tuple[str | None, str], dict] = {}
        for row in rate_rows:
            week = row['week_start'].date() if isinstance(row['week_start'], datetime) else row['week_start']
            key = (str(row['suite_id']) if row['suite_id'] else None, row['attribution'])
            group = by_suite.setdefault(key, {
                'suite_id': key[0],
                'suite_name': row['suite_name'] or {
                    'unknown_suite': 'Unknown suite',
                }.get(row['attribution'], 'Unknown suite'),
                'attribution': row['attribution'],
                '_weeks': {},
            })
            group['_weeks'][week.isoformat()] = {
                'failed': row['failed'],
                'denominator': row['denominator'],
                'total_results': row['total_results'],
                'not_run': row['not_run'],
            }
        failed_rate_series = []
        for group in by_suite.values():
            points = []
            for week in week_starts:
                counts = group['_weeks'].get(week.isoformat(), {
                    'failed': 0, 'denominator': 0, 'total_results': 0, 'not_run': 0,
                })
                points.append({
                    'week_start': week.isoformat(),
                    **counts,
                    'coverage_percent': round(counts['denominator'] * 100 / counts['total_results'], 1)
                    if counts['total_results'] else None,
                    'failed_rate_percent': round(counts['failed'] * 100 / counts['denominator'], 1)
                    if counts['denominator'] else None,
                })
            failed_rate_series.append({
                'suite_id': group['suite_id'], 'suite_name': group['suite_name'],
                'attribution': group['attribution'], 'weeks': points,
            })
        recurrent_cases = []
        for row in recurrent_rows:
            failures = row['failures']
            if isinstance(failures, str):
                failures = json.loads(failures)
            recurrent_cases.append({
                'suite_id': str(row['suite_id']), 'suite_name': row['suite_name'],
                'testcase_id': str(row['testcase_id']), 'testcase_title': row['testcase_title'],
                'failed_run_count': row['failed_run_count'],
                'failures': [
                    {**failure,
                     'run_id': str(failure['run_id']), 'result_id': str(failure['result_id']),
                     'completed_at': failure['completed_at'].isoformat()
                     if isinstance(failure['completed_at'], datetime) else failure['completed_at']}
                    for failure in failures or []
                ],
            })
        return {
            'range': {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat(),
                      'timezone': 'UTC', 'bucket': 'week'},
            'suite_filter': suite_id,
            'has_data': any(row['denominator'] > 0 for row in rate_rows),
            'failed_rate_by_suite': failed_rate_series,
            'recurrent_cases': recurrent_cases,
            'recurrent_window_runs_per_suite': 20,
        }

    @staticmethod
    async def get_quality_results(
        space_id: str,
        suite_id: str,
        week_start: date,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
    ) -> dict:
        """Return a bounded source-result page contributing to one weekly rate."""
        from tortoise import Tortoise

        AnalyticsService._validate_suite_filter(suite_id)
        if week_start.weekday() != 0:
            raise HTTPException(status_code=422, detail='week_start must be a Monday in UTC')
        if page < 1 or page_size < 1 or page_size > 100:
            raise HTTPException(status_code=422, detail='page must be positive and page_size must be between 1 and 100')
        contributing_statuses = {'passed', 'failed', 'blocked', 'skipped'}
        if status is not None and status not in contributing_statuses:
            raise HTTPException(status_code=422, detail='status must be passed, failed, blocked, or skipped')

        start_at = datetime.combine(week_start, datetime.min.time(), tzinfo=timezone.utc)
        end_at = start_at + timedelta(weeks=1)
        params: list[object] = [space_id, suite_id, start_at, end_at]
        status_sql = ''
        if status is not None:
            params.append(status)
            status_sql = f' AND r.status = ${len(params)}'
        cte = """
            WITH filtered AS (
                SELECT tr.id AS run_id, tr.name AS run_name, tr.completed_at,
                       r.id AS result_id, r.testcase_id,
                       COALESCE(r.testcase_snapshot->>'title', '(untitled snapshot)') AS testcase_title,
                       r.status
                FROM test_run tr
                JOIN test_result r ON r.run_id = tr.id
                JOIN test_suite s
                  ON s.id::text = r.testcase_snapshot->>'suite_id'
                 AND s.space_id = tr.space_id
                WHERE tr.space_id = $1::uuid AND s.id = $2::uuid
                  AND tr.status = 'completed'
                  AND tr.completed_at >= $3::timestamptz
                  AND tr.completed_at < $4::timestamptz
                  AND r.status IN ('passed','failed','blocked','skipped')""" + status_sql + """
            )
        """
        conn = Tortoise.get_connection('default')
        total_rows = await conn.execute_query_dict(cte + ' SELECT COUNT(*)::int AS total FROM filtered', params)
        params.extend([page_size, (page - 1) * page_size])
        rows = await conn.execute_query_dict(
            cte + f"""
            SELECT run_id, run_name, completed_at, result_id, testcase_id,
                   testcase_title, status
            FROM filtered
            ORDER BY completed_at DESC, run_id DESC, result_id
            LIMIT ${len(params) - 1}::int OFFSET ${len(params)}::int
            """,
            params,
        )
        items = [{
            'run_id': str(row['run_id']), 'run_name': row['run_name'],
            'completed_at': row['completed_at'].isoformat(),
            'result_id': str(row['result_id']), 'testcase_id': str(row['testcase_id']),
            'testcase_title': row['testcase_title'], 'status': row['status'],
        } for row in rows]
        return {
            'suite_id': suite_id, 'week_start': week_start.isoformat(),
            'week_end_exclusive': end_at.date().isoformat(), 'timezone': 'UTC',
            'status_filter': status, 'items': items, 'page': page,
            'page_size': page_size, 'total': total_rows[0]['total'] if total_rows else 0,
        }

    @staticmethod
    async def get_time_trends(
        space_id: str,
        suite_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        """Completed-run duration series; all bucket attribution uses UTC snapshots."""
        from tortoise import Tortoise

        AnalyticsService._validate_suite_filter(suite_id)
        start_date, end_date, start_at, end_at = AnalyticsService._analytics_range(start_date, end_date)
        daily = (end_date - start_date).days + 1 <= 31
        bucket_expression = (
            "date_trunc('day', tr.completed_at AT TIME ZONE 'UTC')::date"
            if daily else "date_trunc('week', tr.completed_at AT TIME ZONE 'UTC')::date"
        )
        conn = Tortoise.get_connection('default')
        params: list[object] = [space_id, start_at, end_at]
        snapshot_suite_filter = ''
        run_suite_filter = ''
        if suite_id is not None:
            params.append(suite_id)
            filter_param = len(params)
            snapshot_suite_filter = f' AND s.suite_id = ${filter_param}::uuid'
            run_suite_filter = f' AND timer_suite.id = ${filter_param}::uuid'

        # Case duration and estimate follow each result's immutable snapshot suite.
        # A run's single shared timer follows run.suite_id once; it is never copied
        # to every snapshot suite. Multi-suite runs without a valid run suite are
        # shown in one non-disclosing unknown/mixed-suite series.
        case_rows = await conn.execute_query_dict(
            f"""
            WITH scoped AS (
                SELECT {bucket_expression} AS bucket_start,
                       s.id AS suite_id, s.name AS suite_name,
                       CASE WHEN s.id IS NULL THEN 'unknown_suite' ELSE 'suite' END AS attribution,
                       r.duration_seconds,
                       CASE WHEN jsonb_typeof(r.testcase_snapshot->'estimated_duration_seconds') = 'number'
                            THEN (r.testcase_snapshot->>'estimated_duration_seconds')::int
                            ELSE NULL END AS estimate_seconds
                FROM test_run tr
                JOIN test_result r ON r.run_id = tr.id
                LEFT JOIN test_suite s
                  ON s.id::text = r.testcase_snapshot->>'suite_id'
                 AND s.space_id = tr.space_id
                WHERE tr.space_id = $1::uuid AND tr.status = 'completed'
                  AND tr.completed_at >= $2::timestamptz
                  AND tr.completed_at < $3::timestamptz
            )
            SELECT bucket_start, suite_id, suite_name, attribution,
                   COUNT(*)::int AS total_count,
                   COUNT(*) FILTER (WHERE estimate_seconds IS NOT NULL AND estimate_seconds >= 0)::int AS estimated_count,
                   SUM(estimate_seconds) FILTER (WHERE estimate_seconds >= 0)::bigint AS estimate_seconds,
                   COUNT(*) FILTER (WHERE duration_seconds IS NOT NULL AND duration_seconds >= 0)::int AS measured_count,
                   SUM(duration_seconds) FILTER (WHERE duration_seconds >= 0)::bigint AS actual_seconds
            FROM scoped s WHERE TRUE""" + snapshot_suite_filter + """
            GROUP BY bucket_start, suite_id, suite_name, attribution
            ORDER BY bucket_start, suite_name NULLS LAST, attribution
            """,
            params,
        )
        timer_rows = await conn.execute_query_dict(
            f"""
            WITH scoped AS (
                SELECT {bucket_expression} AS bucket_start,
                       timer_suite.id AS suite_id, timer_suite.name AS suite_name,
                       CASE WHEN timer_suite.id IS NULL THEN 'unknown_suite' ELSE 'suite' END AS attribution,
                       tr.id AS run_id,
                       COUNT(ti.id) AS interval_count,
                   SUM(GREATEST(0, FLOOR(EXTRACT(EPOCH FROM
                           (LEAST(COALESCE(ti.ended_at, tr.completed_at), tr.completed_at) - ti.started_at)))))
                           FILTER (WHERE ti.id IS NOT NULL) AS active_seconds
                FROM test_run tr
                LEFT JOIN test_suite timer_suite
                  ON timer_suite.id = tr.suite_id AND timer_suite.space_id = tr.space_id
                LEFT JOIN test_run_timer_interval ti ON ti.run_id = tr.id
                WHERE tr.space_id = $1::uuid AND tr.status = 'completed'
                  AND tr.completed_at >= $2::timestamptz
                  AND tr.completed_at < $3::timestamptz""" + run_suite_filter + """
                GROUP BY bucket_start, timer_suite.id, timer_suite.name, tr.suite_id, tr.id
            )
            SELECT bucket_start, suite_id, suite_name, attribution,
                   COUNT(*) FILTER (WHERE interval_count > 0)::int AS measured_run_count,
                   COUNT(*)::int AS total_run_count,
                   SUM(active_seconds) FILTER (WHERE interval_count > 0)::bigint AS active_seconds
            FROM scoped GROUP BY bucket_start, suite_id, suite_name, attribution
            ORDER BY bucket_start, suite_name NULLS LAST, attribution
            """,
            params,
        )

        def bucket_start_for(day: date) -> date:
            return day if daily else day - timedelta(days=day.weekday())

        bucket_starts: list[date] = []
        cursor = bucket_start_for(start_date)
        last = bucket_start_for(end_date)
        step = timedelta(days=1) if daily else timedelta(weeks=1)
        while cursor <= last:
            bucket_starts.append(cursor)
            cursor += step

        groups: dict[tuple[str | None, str], dict] = {}
        for row in case_rows + timer_rows:
            suite_id_value = str(row['suite_id']) if row['suite_id'] else None
            key = (suite_id_value, row['attribution'])
            group = groups.setdefault(key, {
                'suite_id': suite_id_value,
                'suite_name': row['suite_name'] or {
                    'unknown_suite': 'Unknown / mixed suite',
                }.get(row['attribution'], 'Unknown suite'),
                'attribution': row['attribution'], '_buckets': {},
            })
            bucket = row['bucket_start'].date() if isinstance(row['bucket_start'], datetime) else row['bucket_start']
            slot = group['_buckets'].setdefault(bucket.isoformat(), {})
            if 'total_count' in row:
                slot.update({
                    'total_results': row['total_count'],
                    'estimated_count': row['estimated_count'],
                    'estimate_seconds': row['estimate_seconds'],
                    'measured_count': row['measured_count'],
                    'actual_seconds': row['actual_seconds'],
                })
            else:
                slot.update({
                    'timer_measured_runs': row['measured_run_count'],
                    'timer_total_runs': row['total_run_count'],
                    'active_run_seconds': row['active_seconds'],
                })

        series = []
        for group in groups.values():
            points = []
            for bucket in bucket_starts:
                values = group['_buckets'].get(bucket.isoformat(), {})
                total_results = values.get('total_results', 0)
                measured = values.get('measured_count', 0)
                estimated = values.get('estimated_count', 0)
                timer_measured = values.get('timer_measured_runs', 0)
                points.append({
                    'bucket_start': bucket.isoformat(),
                    'estimated_seconds': values.get('estimate_seconds'),
                    'estimated_count': estimated,
                    'total_results': total_results,
                    'actual_seconds': values.get('actual_seconds'),
                    'measured_count': measured,
                    'average_actual_seconds': round(values['actual_seconds'] / measured, 2)
                    if measured and values.get('actual_seconds') is not None else None,
                    'measurement_coverage': f'{measured}/{total_results}',
                    'measurement_coverage_percent': round(measured * 100 / total_results, 1)
                    if total_results else None,
                    'active_run_seconds': values.get('active_run_seconds'),
                    'timer_measured_runs': timer_measured,
                    'timer_total_runs': values.get('timer_total_runs', 0),
                })
            series.append({
                'suite_id': group['suite_id'], 'suite_name': group['suite_name'],
                'attribution': group['attribution'], 'buckets': points,
            })
        return {
            'range': {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat(),
                      'timezone': 'UTC', 'bucket': 'day' if daily else 'week'},
            'suite_filter': suite_id,
            'has_data': bool(case_rows or timer_rows),
            'timer_attribution': 'The shared run timer is counted once under run.suite_id; missing or invalid suite attribution is grouped as Unknown / mixed suite.',
            'series': series,
        }

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
        filter_sql, filter_params = AnalyticsService._bug_link_filters(run_id, suite_id, status)
        filtered_cte = AnalyticsService._scoped_bug_links_cte(filter_sql)
        params: list[object] = [space_id, *filter_params]
        summary_rows = await conn.execute_query_dict(
            filtered_cte + """
            SELECT COUNT(DISTINCT bug_uuid)::int AS unique_bug_count,
                   COUNT(*)::int AS link_count,
                   COUNT(DISTINCT bug_uuid) FILTER (WHERE status_group = 'OPEN')::int AS open_count,
                   COUNT(DISTINCT bug_uuid) FILTER (WHERE status_group = 'FIXED')::int AS fixed_count,
                   COUNT(DISTINCT bug_uuid) FILTER (WHERE status_group = 'REOPEN')::int AS reopen_count,
                   COUNT(DISTINCT bug_uuid) FILTER (WHERE status_group = 'OTHER')::int AS other_count
            FROM filtered
            """, params)

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
