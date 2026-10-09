import html
from uuid import UUID

from fastapi import HTTPException
from tortoise.transactions import in_transaction

from .model import TechDocTestCaseLinkModel


class TraceabilityService:
    _covered_statuses = {'passed', 'failed', 'blocked', 'skipped'}

    @staticmethod
    def _iso(value):
        return value.isoformat() if value else None

    @staticmethod
    async def get_matrix(space_id: str, tech_doc_ids: list[str] | None = None, connection=None) -> dict:
        """Return safe, space-scoped requirement coverage with the latest result per case."""
        from ..space.model import SpaceModel

        if connection is None:
            async with in_transaction() as transaction:
                return await TraceabilityService.get_matrix(space_id, tech_doc_ids, connection=transaction)

        try:
            space_uuid = UUID(str(space_id))
            requested_ids = list(dict.fromkeys(UUID(str(item)) for item in tech_doc_ids)) if tech_doc_ids is not None else None
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail='Invalid traceability scope') from exc
        if not await SpaceModel.filter(id=space_uuid).using_db(connection).exists():
            raise HTTPException(status_code=404, detail='Space not found')

        selected_doc_ids = requested_ids or []
        doc_rows = await connection.execute_query_dict(
            """SELECT id, space_id, title, doc_type, version, content, sort
                 FROM tech_doc
                WHERE space_id = $1
                  AND ($2::uuid[] IS NULL OR id = ANY($2::uuid[]))
                ORDER BY sort, id""",
            [space_uuid, requested_ids],
        )
        if tech_doc_ids is not None and len(doc_rows) != len(selected_doc_ids):
            # A foreign or unknown requirement is not disclosed through this endpoint.
            raise HTTPException(status_code=404, detail='One or more requirements were not found')

        doc_ids = [row['id'] for row in doc_rows]
        if not doc_ids:
            return {
                'space_id': str(space_uuid),
                'summary': {
                    'requirements_count': 0, 'requirements_without_cases': 0,
                    'case_links_count': 0, 'covered_case_links': 0,
                    'uncovered_case_links': 0, 'coverage_percent': None,
                    'case_links_without_results': 0,
                },
                'requirements': [],
            }

        # Every side of the relation is constrained to the authorized space before
        # any case/result aggregation; corrupt legacy links disappear from the view.
        link_rows = await connection.execute_query_dict(
            """SELECT l.id AS link_id, l.tech_doc_id, l.testcase_id,
                          c.id AS valid_case_id, c.title AS case_title,
                          c.short_name AS case_short_name, c.status AS case_status,
                          c.type AS case_type
                 FROM tech_doc_test_case_link l
                 JOIN tech_doc d ON d.id = l.tech_doc_id AND d.space_id = $1
                 LEFT JOIN test_case c ON c.id = l.testcase_id
                      AND c.space_id = $1 AND c.space_id = l.space_id
                WHERE l.space_id = $1 AND l.tech_doc_id = ANY($2::uuid[])
                ORDER BY l.created_at, l.id""",
            [space_uuid, doc_ids],
        )
        valid_links = [row for row in link_rows if row['valid_case_id'] is not None]
        case_ids = list(dict.fromkeys(row['valid_case_id'] for row in valid_links))
        result_by_case = {}
        if case_ids:
            result_rows = await connection.execute_query_dict(
                """SELECT DISTINCT ON (r.testcase_id)
                          r.testcase_id, r.id AS result_id, r.status AS result_status,
                          r.duration_seconds, r.updated_at AS result_updated_at,
                          run.id AS run_id, run.name AS run_name,
                          run.status AS run_status, run.completed_at
                     FROM test_result r
                     JOIN test_case c ON c.id = r.testcase_id AND c.space_id = $1
                     JOIN test_run run ON run.id = r.run_id AND run.space_id = $1
                    WHERE r.testcase_id = ANY($2::uuid[])
                    ORDER BY r.testcase_id, r.updated_at DESC NULLS LAST,
                             r.created_at DESC, r.id DESC""",
                [space_uuid, case_ids],
            )
            result_by_case = {str(row['testcase_id']): row for row in result_rows}

        links_by_doc = {str(doc_id): [] for doc_id in doc_ids}
        for row in valid_links:
            result = result_by_case.get(str(row['valid_case_id']))
            status = str(result['result_status']) if result else None
            covered = status in TraceabilityService._covered_statuses
            links_by_doc[str(row['tech_doc_id'])].append({
                'id': str(row['valid_case_id']),
                'link_id': str(row['link_id']),
                'title': row['case_title'],
                'short_name': row['case_short_name'],
                'status': str(row['case_status']),
                'type': str(row['case_type']),
                'covered': covered,
                'coverage_state': 'covered' if covered else 'not_run' if status == 'not_run' else 'no_result',
                'last_result': ({
                    'id': str(result['result_id']),
                    'status': status,
                    'duration_seconds': result['duration_seconds'],
                    'updated_at': TraceabilityService._iso(result['result_updated_at']),
                    'run': {
                        'id': str(result['run_id']), 'name': result['run_name'],
                        'status': str(result['run_status']),
                        'completed_at': TraceabilityService._iso(result['completed_at']),
                    },
                } if result else None),
            })

        requirements = []
        requirements_without_cases = 0
        case_links_count = covered_case_links = case_links_without_results = 0
        for doc in doc_rows:
            doc_id = str(doc['id'])
            cases = links_by_doc[doc_id]
            total = len(cases)
            covered = sum(1 for case in cases if case['covered'])
            no_results = sum(1 for case in cases if case['last_result'] is None)
            if not cases:
                requirements_without_cases += 1
            case_links_count += total
            covered_case_links += covered
            case_links_without_results += no_results
            requirements.append({
                'id': doc_id,
                'title': doc['title'],
                'doc_type': str(doc['doc_type']),
                'version': doc['version'],
                # Escaping all markup keeps rich text display-safe without adding a
                # server-side HTML sanitizer dependency or trusting stored HTML.
                'content_display': html.escape(doc['content'] or '', quote=True),
                'cases': cases,
                'coverage': {
                    'total_cases': total,
                    'covered_cases': covered,
                    'uncovered_cases': total - covered,
                    'coverage_percent': round(covered * 100 / total, 2) if total else None,
                    'state': 'no_testcases' if not total else 'covered' if covered == total else 'partial' if covered else 'uncovered',
                },
            })
        return {
            'space_id': str(space_uuid),
            'summary': {
                'requirements_count': len(requirements),
                'requirements_without_cases': requirements_without_cases,
                'case_links_count': case_links_count,
                'covered_case_links': covered_case_links,
                'uncovered_case_links': case_links_count - covered_case_links,
                'coverage_percent': round(covered_case_links * 100 / case_links_count, 2) if case_links_count else None,
                'case_links_without_results': case_links_without_results,
            },
            'requirements': requirements,
        }

    @staticmethod
    async def _get_same_space_pair(tech_doc_id: str, testcase_id: str):
        from ..tech_doc.model import TechDocModel
        from ..test_case.model import TestCaseModel

        tech_doc = await TechDocModel.get_or_none(id=tech_doc_id)
        if not tech_doc:
            raise HTTPException(status_code=404, detail='Tech doc not found')
        testcase = await TestCaseModel.get_or_none(id=testcase_id)
        if not testcase:
            raise HTTPException(status_code=404, detail='Test case not found')
        if str(tech_doc.space_id) != str(testcase.space_id):
            raise HTTPException(status_code=422, detail='Tech doc and testcase must belong to the same space')
        return tech_doc, testcase

    @staticmethod
    def _serialize_link(link: TechDocTestCaseLinkModel) -> dict:
        return {
            'id': str(link.id),
            'space_id': str(link.space_id),
            'tech_doc_id': str(link.tech_doc_id),
            'testcase_id': str(link.testcase_id),
            'created_at': link.created_at.isoformat() if link.created_at else None,
        }

    @staticmethod
    async def link(tech_doc_id: str, testcase_id: str) -> dict:
        tech_doc, testcase = await TraceabilityService._get_same_space_pair(tech_doc_id, testcase_id)
        link, _created = await TechDocTestCaseLinkModel.get_or_create(
            tech_doc_id=str(tech_doc.id),
            testcase_id=str(testcase.id),
            defaults={'space_id': str(tech_doc.space_id)},
        )
        return TraceabilityService._serialize_link(link)

    @staticmethod
    async def unlink(tech_doc_id: str, testcase_id: str) -> bool:
        # Enforce the relation invariant in the service as well as at the HTTP
        # boundary so MCP and future callers cannot remove cross-space links.
        await TraceabilityService._get_same_space_pair(tech_doc_id, testcase_id)
        deleted = await TechDocTestCaseLinkModel.filter(
            tech_doc_id=tech_doc_id,
            testcase_id=testcase_id,
        ).delete()
        if not deleted:
            raise HTTPException(status_code=404, detail='Traceability link not found')
        return True

    @staticmethod
    async def get_testcases_for_doc(tech_doc_id: str) -> list[dict]:
        from ..tech_doc.model import TechDocModel

        tech_doc = await TechDocModel.get_or_none(id=tech_doc_id)
        if not tech_doc:
            raise HTTPException(status_code=404, detail='Tech doc not found')
        links = await TechDocTestCaseLinkModel.filter(tech_doc_id=tech_doc_id).prefetch_related('testcase').order_by('created_at')
        return [
            {
                'id': str(link.testcase.id),
                'title': link.testcase.title,
                'status': link.testcase.status,
                'type': link.testcase.type,
                'link_id': str(link.id),
                'created_at': link.created_at.isoformat() if link.created_at else None,
            }
            for link in links
            if (
                str(link.space_id) == str(tech_doc.space_id)
                and str(link.testcase.space_id) == str(tech_doc.space_id)
            )
        ]

    @staticmethod
    async def get_docs_for_testcase(testcase_id: str) -> list[dict]:
        from ..test_case.model import TestCaseModel

        testcase = await TestCaseModel.get_or_none(id=testcase_id)
        if not testcase:
            raise HTTPException(status_code=404, detail='Test case not found')
        links = await TechDocTestCaseLinkModel.filter(testcase_id=testcase_id).prefetch_related('tech_doc').order_by('created_at')
        return [
            {
                'id': str(link.tech_doc.id),
                'title': link.tech_doc.title,
                'doc_type': link.tech_doc.doc_type,
                'source_url': link.tech_doc.source_url,
                'link_id': str(link.id),
                'created_at': link.created_at.isoformat() if link.created_at else None,
            }
            for link in links
            if (
                str(link.space_id) == str(testcase.space_id)
                and str(link.tech_doc.space_id) == str(testcase.space_id)
            )
        ]

    @staticmethod
    async def _replace_links(tech_doc_id: str, testcase_ids: list[str]) -> list[dict]:
        tech_doc_ids = list(dict.fromkeys(testcase_ids))
        from ..tech_doc.model import TechDocModel
        from ..test_case.model import TestCaseModel

        tech_doc = await TechDocModel.get_or_none(id=tech_doc_id)
        if not tech_doc:
            raise HTTPException(status_code=404, detail='Tech doc not found')
        testcases = await TestCaseModel.filter(id__in=tech_doc_ids, space_id=tech_doc.space_id)
        if len(testcases) != len(tech_doc_ids):
            raise HTTPException(status_code=422, detail='Every testcase must belong to the tech doc space')
        async with in_transaction() as connection:
            await TechDocTestCaseLinkModel.filter(tech_doc_id=tech_doc_id).using_db(connection).delete()
            for testcase_id in tech_doc_ids:
                await TechDocTestCaseLinkModel.create(
                    tech_doc_id=tech_doc_id,
                    testcase_id=testcase_id,
                    space_id=tech_doc.space_id,
                    using_db=connection,
                )
        return await TraceabilityService.get_testcases_for_doc(tech_doc_id)

    @staticmethod
    async def replace_testcases_for_doc(tech_doc_id: str, testcase_ids: list[str]) -> list[dict]:
        return await TraceabilityService._replace_links(tech_doc_id, testcase_ids)

    @staticmethod
    async def replace_docs_for_testcase(testcase_id: str, tech_doc_ids: list[str]) -> list[dict]:
        from ..test_case.model import TestCaseModel
        from ..tech_doc.model import TechDocModel

        testcase = await TestCaseModel.get_or_none(id=testcase_id)
        if not testcase:
            raise HTTPException(status_code=404, detail='Test case not found')
        unique_doc_ids = list(dict.fromkeys(tech_doc_ids))
        docs = await TechDocModel.filter(id__in=unique_doc_ids, space_id=testcase.space_id)
        if len(docs) != len(unique_doc_ids):
            raise HTTPException(status_code=422, detail='Every tech doc must belong to the testcase space')
        async with in_transaction() as connection:
            await TechDocTestCaseLinkModel.filter(testcase_id=testcase_id).using_db(connection).delete()
            for tech_doc_id in unique_doc_ids:
                await TechDocTestCaseLinkModel.create(
                    tech_doc_id=tech_doc_id,
                    testcase_id=testcase_id,
                    space_id=testcase.space_id,
                    using_db=connection,
                )
        return await TraceabilityService.get_docs_for_testcase(testcase_id)
