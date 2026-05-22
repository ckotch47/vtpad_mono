# import tortoise
# from opentelemetry.instrumentation.tortoiseorm import TortoiseORMInstrumentor


from prometheus_fastapi_instrumentator import Instrumentator  # prom client
from starlette.middleware.cors import CORSMiddleware  # midelware

from fastapi import FastAPI  # fatapi requeriments

from starlette.responses import PlainTextResponse, Response  # response for try
from starlette.staticfiles import StaticFiles  # static file for picture
from tortoise.contrib.fastapi import register_tortoise  # tortoise ORM

# cprofiler import
# from fastapi_cprofile.profiler import CProfileMiddleware

# imporn modules
import app.src.common as common
import app.src.items as items

import app.src.pad as pad
import app.src.space as space
import app.src.run as run
import app.src.runitems as runitems
import app.src.users as users
import app.src.auth as auth
import app.src.file as file
import app.src.notes as note
import app.src.bug as bug
import app.src.comments as comments_bug
import app.src.tag as tag
import app.src.notification as notification
import app.src.padfolder as padfolder
import app.src.news as news
import app.src.report as report
import app.src.testcases as testcases
import app.src.testcases_runitem as testcases_runitem
import app.src.testcases_paditem as testcases_paditem
import app.utils.register_router as app_utils

import app.src.checklist as checklist
import app.src.qa_report.router as qa_report

from app.src.admin import company_router, user_company_router, router_company_admin
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
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry import trace
#
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.sdk.trace.export import ConsoleSpanExporter
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
# from opentelemetry.sdk.resources import SERVICE_NAME, Resource
#
# from opentelemetry.instrumentation.requests import RequestsInstrumentor

# init config module and models
config = common.EnvConfig()
models = common.Models()

# end import