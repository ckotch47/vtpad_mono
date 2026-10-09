import asyncio
import logging
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tortoise import Tortoise

from app.src.redis import redis_service


router = APIRouter(tags=["Health"])
DEPENDENCY_TIMEOUT_SECONDS = 2
logger = logging.getLogger(__name__)


class ReadinessUnavailable(BaseModel):
    status: Literal["not_ready"]


@router.get("/health", summary="Check whether the backend process is alive")
async def health_check():
    return {"status": "ok"}


async def _check_database():
    connection = Tortoise.get_connection("default")
    await connection.execute_query("SELECT 1")


async def _check_redis():
    await redis_service.redis.ping()


@router.get(
    "/ready",
    summary="Check whether required backend dependencies are available",
    responses={
        503: {
            "model": ReadinessUnavailable,
            "description": "A required dependency is unavailable",
        }
    },
)
async def readiness_check():
    for dependency, check in (("postgresql", _check_database), ("redis", _check_redis)):
        try:
            await asyncio.wait_for(check(), timeout=DEPENDENCY_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.warning("Readiness check failed: dependency=%s reason=timeout", dependency)
            return JSONResponse(status_code=503, content={"status": "not_ready"})
        except Exception:
            logger.warning("Readiness check failed: dependency=%s reason=unavailable", dependency)
            return JSONResponse(status_code=503, content={"status": "not_ready"})

    return {"status": "ready"}
