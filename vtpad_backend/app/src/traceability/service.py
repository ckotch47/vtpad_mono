from fastapi import HTTPException
from tortoise.transactions import in_transaction

from .model import TechDocTestCaseLinkModel


class TraceabilityService:
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
