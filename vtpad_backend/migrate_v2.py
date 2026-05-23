"""
Migration script: Legacy data → New V2 architecture

Migrates:
- PadModel → TestSuiteModel
- ItemsModel → SectionModel
- TestCasesModel → TestCaseModel (type=manual)
- ChecklistModel → TestCaseModel (type=checklist)
- RunModel + RunItemsModel + TestCaseRunItemModel → TestRunModel + TestResultModel

Usage:
    cd vtpad_backend && source .venv/bin/activate && python migrate_v2.py
"""

import asyncio
from tortoise import Tortoise
from app.main import config_orm


async def migrate():
    await Tortoise.init(config=config_orm)

    from app.src.pad.model import PadModel
    from app.src.items.model import ItemsModel
    from app.src.testcases.model import TestCasesModel
    from app.src.checklist.model import ChecklistModel
    from app.src.run.model import RunModel
    from app.src.runitems.model import RunItemsModel
    from app.src.testcases_runitem.model import TestCaseRunItemModel
    from app.src.testcases_paditem.model import TestCasePadItemModel
    from app.src.items_checklist_testcase.model import ItemChecklistTestcaseModel

    from app.src.test_suite.model import TestSuiteModel
    from app.src.section.model import SectionModel
    from app.src.test_case.model import TestCaseModel, TestCaseVersionModel, TestCaseType, TestCaseStatus
    from app.src.test_run.model import TestRunModel, TestResultModel, TestRunStatus, TestResultStatus
    from app.src.users.model import UserModel

    conn = Tortoise.get_connection('default')

    # --- 1. Pad → TestSuite ---
    print("Migrating Pad → TestSuite...")
    pads = await PadModel.all()
    pad_to_suite = {}
    for pad in pads:
        suite = await TestSuiteModel.create(
            name=pad.name or "Untitled Suite",
            sort=pad.sort or 10,
            space_id=str(pad.spaces_id) if pad.spaces_id else None,
            status="active",
        )
        pad_to_suite[str(pad.id)] = str(suite.id)
    print(f"  Migrated {len(pads)} pads")

    # --- 2. Items → Section ---
    print("Migrating Items → Section...")
    items = await ItemsModel.all().order_by('sort')
    item_to_section = {}
    for item in items:
        suite_id = pad_to_suite.get(str(item.pad_id))
        if not suite_id:
            continue
        section = await SectionModel.create(
            name=item.text or "Untitled Section",
            sort=item.sort or 10,
            suite_id=suite_id,
            parent_id=item_to_section.get(str(item.mainId)) if item.mainId else None,
        )
        item_to_section[str(item.id)] = str(section.id)
    print(f"  Migrated {len(items)} items")

    # --- 3. TestCases → TestCase (manual) ---
    print("Migrating TestCases → TestCase (manual)...")
    tcs = await TestCasesModel.all()
    tc_old_to_new = {}
    for tc in tcs:
        # find suite/section via TestCasePadItemModel
        link = await TestCasePadItemModel.filter(testcases_id=str(tc.id)).first()
        suite_id = None
        section_id = None
        if link:
            suite_id = pad_to_suite.get(str(link.pad_item_id))
            section_id = item_to_section.get(str(link.pad_item_id))

        new_tc = await TestCaseModel.create(
            title=tc.title or "Untitled Test Case",
            text=tc.text,
            steps=tc.steps,
            expected_results=tc.expected_results,
            sort=tc.sort or 10,
            short_name=tc.short_name,
            link=tc.link,
            type=TestCaseType.manual,
            status=TestCaseStatus.active if tc.title else TestCaseStatus.draft,
            space_id=str(tc.space_id) if tc.space_id else None,
            suite_id=suite_id,
            section_id=section_id,
        )
        tc_old_to_new[str(tc.id)] = str(new_tc.id)

        # create initial version
        await TestCaseVersionModel.create(
            testcase_id=str(new_tc.id),
            version_number=1,
            title=tc.title or "Untitled Test Case",
            text=tc.text,
            steps=tc.steps,
            expected_results=tc.expected_results,
        )
    print(f"  Migrated {len(tcs)} test cases")

    # --- 4. Checklist → TestCase (checklist) ---
    print("Migrating Checklist → TestCase (checklist)...")
    checklists = await ChecklistModel.all()
    checklist_old_to_new = {}
    for cl in checklists:
        # find section via ItemChecklistTestcaseModel
        link = await ItemChecklistTestcaseModel.filter(checklist_id=str(cl.id)).first()
        section_id = None
        suite_id = None
        if link:
            section_id = item_to_section.get(str(link.item_id))
            if section_id:
                section = await SectionModel.get_or_none(id=section_id)
                if section:
                    suite_id = str(section.suite_id)

        new_tc = await TestCaseModel.create(
            title=cl.title or "Untitled Checklist",
            text=cl.text,
            sort=cl.sort or 10,
            short_name=cl.short_name,
            type=TestCaseType.checklist,
            status=TestCaseStatus.active if cl.state == 'active' else TestCaseStatus.draft,
            space_id=str(cl.space_id) if cl.space_id else None,
            suite_id=suite_id,
            section_id=section_id,
        )
        checklist_old_to_new[str(cl.id)] = str(new_tc.id)

        await TestCaseVersionModel.create(
            testcase_id=str(new_tc.id),
            version_number=1,
            title=cl.title or "Untitled Checklist",
            text=cl.text,
        )
    print(f"  Migrated {len(checklists)} checklists")

    # --- 5. Run → TestRun, RunItems + TestCaseRunItem → TestResult ---
    print("Migrating Run → TestRun + TestResult...")
    runs = await RunModel.all()
    for run in runs:
        suite_id = pad_to_suite.get(str(run.pads_id))
        new_run = await TestRunModel.create(
            name=run.name or "Untitled Run",
            status=TestRunStatus.completed,
            space_id=str(run.pads.spaces_id) if run.pads and run.pads.spaces_id else None,
            suite_id=suite_id,
            created_at=run.date,
        )

        # find run items
        run_items = await RunItemsModel.filter(run_id=str(run.id)).all()
        for ri in run_items:
            # find testcase via TestCaseRunItemModel
            tc_link = await TestCaseRunItemModel.filter(run_item_id=str(ri.id)).first()
            if tc_link:
                old_tc_id = str(tc_link.testcases_id)
                new_tc_id = tc_old_to_new.get(old_tc_id) or checklist_old_to_new.get(old_tc_id)
                if new_tc_id:
                    status_map = {
                        'passed': TestResultStatus.passed,
                        'failed': TestResultStatus.failed,
                        'blocked': TestResultStatus.blocked,
                        'skipped': TestResultStatus.skipped,
                    }
                    await TestResultModel.create(
                        run_id=str(new_run.id),
                        testcase_id=new_tc_id,
                        status=status_map.get(str(ri.state), TestResultStatus.not_run),
                    )
    print(f"  Migrated {len(runs)} runs")

    await Tortoise.close_connections()
    print("\nMigration complete!")


if __name__ == "__main__":
    asyncio.run(migrate())
