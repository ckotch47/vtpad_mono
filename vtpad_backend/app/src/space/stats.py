
from tortoise import Tortoise
from .queries import get_space_by_id
import logging
logger = logging.getLogger(__name__)

async def get_all_runs_spaces(space_id):
    from ..test_run.model import TestRunModel, TestResultModel
    space = await get_space_by_id({}, space_id)
    runs = await TestRunModel.filter(space_id=space_id).order_by('-created_at')
    res = []
    for run in runs:
        results = await TestResultModel.filter(run_id=str(run.id))
        passed = sum(1 for r in results if str(r.status) == 'passed')
        failed = sum(1 for r in results if str(r.status) == 'failed')
        total = len(results)
        res.append({
            "run_id": str(run.id),
            "run_name": run.name,
            "date": run.created_at.isoformat() if run.created_at else None,
            "items_count": {
                "pass": passed,
                "fail": failed,
                "all": total
            }
        })
    return {
        "space_id": str(space['id']),
        "space_name": space['name'],
        "pad": res
    }
async def get_statistic_for_space(space_id: str):
    from ..test_suite.model import TestSuiteModel
    from ..section.model import SectionModel
    from ..test_run.model import TestRunModel, TestResultModel
    conn = Tortoise.get_connection('default')

    suite_count = await TestSuiteModel.filter(space_id=space_id).count()
    section_count = await SectionModel.filter(suite__space_id=space_id).count()

    run_count = await TestRunModel.filter(space_id=space_id).count()
    runs = await TestRunModel.filter(space_id=space_id).all()
    run_ids = [str(r.id) for r in runs]
    results = await TestResultModel.filter(run_id__in=run_ids) if run_ids else []
    runs_state_map = {}
    for r in results:
        st = str(r.status)
        runs_state_map[st] = runs_state_map.get(st, 0) + 1
    runs_state = [{"item_count": v, "state": k} for k, v in runs_state_map.items()]

    sql_bugs = "SELECT count(bugsmodel.id) as item_count, state FROM bugsmodel \
                WHERE bugsmodel.spaces_id = $1 \
                GROUP BY state;"
    sql_all_bugs = "SELECT count(bugsmodel.id) FROM bugsmodel \
                        WHERE bugsmodel.spaces_id = $1;"

    bugs = await conn.execute_query_dict(sql_bugs, [space_id])
    all_bugs = await conn.execute_query_dict(sql_all_bugs, [space_id])

    return {
        'pads': {"count": suite_count, "items_count": section_count},
        'runs': {
            'count': run_count,
            'state': runs_state
        },
        'bugs': {
            'count': SpaceService.get_arg(all_bugs, 'count'),
            'state': bugs
        }
    }
def get_arg(obj: list, name: str):
    try:
        return obj[0][name]
    except Exception as e:
        logger.error('Unexpected error: %s', e, exc_info=True)
        return 0
async def get_statistic_for_space_old(space_id: str):
    return {
        "pads": await SpaceService.get_pads_count(space_id),
        "runs": await SpaceService.get_runs_statistic(space_id),
        "bugs": {
            "count": await SpaceService.get_bugs_count(space_id),
            "open": await SpaceService.get_bugs_count(space_id, 'OPEN'),
            "reopen": await SpaceService.get_bugs_count(space_id, 'REOPEN'),
            "closed": await SpaceService.get_bugs_count(space_id, 'CLOSED'),
            "fixed": await SpaceService.get_bugs_count(space_id, 'FIXED'),
            "hold": await SpaceService.get_bugs_count(space_id, 'HOLD')
        }
    }
async def get_bugs_count(space_id, state=None):
    conn = Tortoise.get_connection('default')
    sql = "SELECT count(id) FROM bugsmodel " \
          "WHERE spaces_id = $1"

    params = [space_id]
    if state:
        ALLOWED_STATES = {'OPEN', 'REOPEN', 'CLOSED', 'FIXED', 'HOLD', 'READY'}
        if state.upper() in ALLOWED_STATES:
            sql += " AND state = $2"
            params.append(state.upper())
    return (await conn.execute_query_dict(sql, params))[0]['count']
async def get_pads_count(space_id):
    from ..test_suite.model import TestSuiteModel
    from ..section.model import SectionModel
    suites = await TestSuiteModel.filter(space_id=space_id)
    suite_ids = [str(s.id) for s in suites]
    sections_count = 0
    if suite_ids:
        sections_count = await SectionModel.filter(suite_id__in=suite_ids).count()
    return {
        "count": len(suites),
        "items_count": sections_count
    }
async def get_runs_statistic(space_id: str):
    from ..test_run.model import TestRunModel, TestResultModel
    runs = await TestRunModel.filter(space_id=space_id)
    run_ids = [str(r.id) for r in runs]
    total = 0
    passed = 0
    failed = 0
    not_run = 0
    if run_ids:
        results = await TestResultModel.filter(run_id__in=run_ids)
        total = len(results)
        passed = sum(1 for r in results if str(r.status) == 'passed')
        failed = sum(1 for r in results if str(r.status) == 'failed')
        not_run = sum(1 for r in results if str(r.status) == 'not_run')
    return {
        "count": len(runs),
        "items_count": total,
        "passed": passed,
        "fail": failed,
        "not_status": not_run
    }
