from fastapi import HTTPException
from typing import Optional

from tortoise.expressions import Q

from .model import TestCaseModel, TestCaseVersionModel, TestCaseType, TestCaseStatus
from .dto import *
from ..common.crypto import get_user_id_by_token


class TestCaseService:
    @staticmethod
    async def create(dto: TestCaseCreateDto, token: str) -> TestCaseModel:
        user_id = await get_user_id_by_token(token)
        section_id = dto.section_id
        suite_id = dto.suite_id

        if section_id:
            from ..section.model import SectionModel
            section = await SectionModel.get_or_none(id=section_id)
            if section:
                suite_id = str(section.suite_id)

        last = await TestCaseModel.filter(
            space_id=dto.space_id,
            suite_id=suite_id,
            section_id=section_id
        ).order_by('-sort').first()
        sort = (last.sort + 10) if last else 10

        testcase = await TestCaseModel.create(
            title=dto.title,
            text=dto.text,
            steps=dto.steps,
            expected_results=dto.expected_results,
            preconditions=dto.preconditions,
            postconditions=dto.postconditions,
            type=dto.type,
            sort=sort,
            space_id=dto.space_id,
            suite_id=suite_id,
            section_id=section_id,
            short_name=dto.short_name,
            link=dto.link,
            external_id=dto.external_id,
            created_by_id=user_id,
        )

        # Create initial version snapshot
        await TestCaseVersionModel.create(
            testcase_id=str(testcase.id),
            version_number=1,
            title=dto.title,
            text=dto.text,
            steps=dto.steps,
            expected_results=dto.expected_results,
            preconditions=dto.preconditions,
            postconditions=dto.postconditions,
            created_by_id=user_id,
        )

        return testcase

    @staticmethod
    async def get_by_space(
        space_id: str,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
        sort_by: Optional[str] = 'created_at',
        sort_order: Optional[str] = 'desc',
        search: Optional[str] = None
    ) -> dict:
        q = TestCaseModel.filter(space_id=space_id)
        if type_filter:
            q = q.filter(type=type_filter)
        if status_filter:
            q = q.filter(status=status_filter)
        if search:
            q = q.filter(Q(title__icontains=search) | Q(short_name__icontains=search))

        order = f'{"-" if sort_order == "desc" else ""}{sort_by}'
        q = q.order_by(order)

        total = await q.count()
        items = await q.offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

    @staticmethod
    async def get_by_suite(suite_id: str) -> list[TestCaseModel]:
        return await TestCaseModel.filter(suite_id=suite_id).order_by('sort')

    @staticmethod
    async def get_by_section(section_id: str) -> list[TestCaseModel]:
        return await TestCaseModel.filter(section_id=section_id).order_by('sort')

    @staticmethod
    async def get_by_id(testcase_id: str) -> TestCaseModel:
        testcase = await TestCaseModel.get_or_none(id=testcase_id)
        if not testcase:
            raise HTTPException(status_code=404, detail="Test case not found")
        return testcase

    @staticmethod
    async def update(testcase_id: str, dto: TestCaseUpdateDto) -> TestCaseModel:
        testcase = await TestCaseService.get_by_id(testcase_id)

        # Create version snapshot before update
        last_version = await TestCaseVersionModel.filter(testcase_id=testcase_id).order_by('-version_number').first()
        version_number = (last_version.version_number + 1) if last_version else 1
        await TestCaseVersionModel.create(
            testcase_id=testcase_id,
            version_number=version_number,
            title=testcase.title,
            text=testcase.text,
            steps=testcase.steps,
            expected_results=testcase.expected_results,
            preconditions=testcase.preconditions,
            postconditions=testcase.postconditions,
        )

        data = dto.model_dump(exclude_unset=True)
        if data:
            await TestCaseModel.filter(id=testcase_id).update(**data)
        return await TestCaseService.get_by_id(testcase_id)

    @staticmethod
    async def delete(testcase_id: str) -> bool:
        await TestCaseService.get_by_id(testcase_id)
        await TestCaseModel.filter(id=testcase_id).update(status=TestCaseStatus.deprecated)
        return True

    @staticmethod
    async def update_sort(testcase_id: str, dto: TestCaseSortDto) -> list[TestCaseModel]:
        testcase = await TestCaseService.get_by_id(testcase_id)
        space_id = str(testcase.space_id)
        suite_id = testcase.suite_id
        section_id = testcase.section_id

        if dto.sort_before_id:
            before = await TestCaseService.get_by_id(dto.sort_before_id)
            target = await TestCaseService.get_by_id(testcase_id)
            await TestCaseModel.filter(id=dto.sort_before_id).update(sort=target.sort)
            await TestCaseModel.filter(id=testcase_id).update(sort=before.sort)

        if dto.sort_after_id:
            after = await TestCaseService.get_by_id(dto.sort_after_id)
            target = await TestCaseService.get_by_id(testcase_id)
            await TestCaseModel.filter(id=dto.sort_after_id).update(sort=target.sort)
            await TestCaseModel.filter(id=testcase_id).update(sort=after.sort)

        return await TestCaseModel.filter(space_id=space_id, suite_id=suite_id, section_id=section_id).order_by('sort')
