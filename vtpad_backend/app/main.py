import tortoise
from opentelemetry.instrumentation.tortoiseorm import TortoiseORMInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator  # prom client
from starlette.middleware.cors import CORSMiddleware  # midelware

from fastapi import FastAPI  # fatapi requeriments
from starlette.responses import PlainTextResponse  # response for try
from starlette.staticfiles import StaticFiles  # static file for picture
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise  # tortoise ORM

# cprofiler import
# from fastapi_cprofile.profiler import CProfileMiddleware

# imporn modules
import app.src.common as common
import app.src.space as space
import app.src.users as users
import app.src.auth as auth
import app.src.file as file
import app.src.bug as bug
import app.src.comments as comments_bug
import app.src.tag as tag
import app.src.notification as notification
from app.src.qa_report import router as qa_report_router

# new v2 modules
import app.src.test_suite as test_suite
import app.src.section as section
import app.src.test_case as test_case
import app.src.test_run as test_run
import app.src.environment as environment
import app.src.milestone as milestone
import app.src.custom_field as custom_field
import app.src.attachment as attachment
import app.src.api_token as api_token
import app.src.tech_doc as tech_doc
import app.src.test_plan as test_plan
import app.src.analytics as analytics

# MCP server
from app.src.mcp.server import get_mcp_app

# end import


# fastapi exception filter import
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
# end


# import opentelemetry for jager tools
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry.instrumentation.requests import RequestsInstrumentor

# init config module and models
config = common.EnvConfig()
models = common.Models()

# end import

# setting jager
# provider = TracerProvider()
# processor = BatchSpanProcessor(ConsoleSpanExporter())
# provider.add_span_processor(processor)
# trace.set_tracer_provider(
#     TracerProvider(
#         resource=Resource.create({SERVICE_NAME: "vtpad"})
#     )
# )
# jaeger_exporter = JaegerExporter(
#     agent_host_name=f"{config.jaeger_host}",
#     agent_port=6831,
# )
#
# trace.get_tracer_provider().add_span_processor(
#     BatchSpanProcessor(jaeger_exporter)
# )
#
# tracer = trace.get_tracer(__name__)

# end settings

from .imports import *

# execetion_path for token
execetion_path = [
    ['POST', '/auth'],
    ['POST', '/user']
]

#  register orm
config_orm = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": config.db_name,
                "host": config.db_host,
                "password": config.db_password,
                "port": config.db_port,
                "user": config.db_user,
                "ssl": False
                }
        },

    },
    "apps": {
        'models': {
            'models': models.get_models(),
            # If no default_connection specified, defaults to 'default'
            'default_connection': 'default',
            },

    }
}


from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # server start

    from .migration import migration
    from .migration import init as migration_init
    await migration_init()

    await migration.run_migration()
    yield
    # server stop


mcp_app = get_mcp_app()

from fastmcp.utilities.lifespan import combine_lifespans

app = FastAPI(
    redoc_url='',
    dependencies=[],
    title='vtpad',
    docs_url='/docs',
    lifespan=combine_lifespans(lifespan, mcp_app.lifespan),
)

register_tortoise(app, config=config_orm, generate_schemas=False, add_exception_handlers=True)

# for cors host
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:8008",
    "*"
]

# settings cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### profiler
# app.add_middleware(CProfileMididleware, enable=True, server_app = app, filename='out.pstats', strip_dirs = False, sort_by='cumulative') #
# # app.add_middleware(CProfileMiddleware, enable=True, prnt_each_request = True, strip_dirs = False, sort_by='cumulative')
### profiler







# exception filter
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


# add path to ws.
@app.websocket('/ws')
def ws():
    return ''


app_utils.register_router(
    [
        auth.router,
        users.router,
        users.routerV2,
        space.space_router,
        bug.router,
        bug.router_v2,
        comments_bug.router,
        tag.router,
        file.router,
        notification.router,
        company_router,
        user_company_router,
        router_company_admin,
        qa_report_router,

        # new v2 routers
        test_suite.router,
        section.router,
        test_case.router,
        test_run.router,
        environment.router,
        milestone.router,
        custom_field.router,
        attachment.router,
        api_token.router,
        tech_doc.router,
        test_plan.router,
        analytics.router,

    ], app, global_prefix='/api')


# mount static file for app
app.mount('/uploads', StaticFiles(directory="uploads"), name="uploads")

# Mount MCP server
app.mount('/v1', mcp_app)






# register prom
Instrumentator().instrument(app).expose(app)
