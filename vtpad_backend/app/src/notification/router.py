import asyncio
import json
import logging

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request

from .dto import GetNotificationDto
from .service import NotificationService

from ..common.crypto import bearer, user_payload

logger = logging.getLogger()

MESSAGE_STREAM_DELAY = 15  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # milisecond

router = APIRouter(
    prefix="/v1/notification",
    tags=["notification"],
    responses={404: {"message": "Not found"}},
)

COUNTER = 0


async def get_message(user_id: str):
    # todo rework to redis
    return await NotificationService.get_notification(GetNotificationDto(
        user_id=user_id,
        send=False
    ))


async def event_generator(request: Request, user_id: str):
    while True:
        if await request.is_disconnected():
            logger.debug("Request disconnected")
            break

        # Checks for new messages and return them to client if any
        counter = await get_message(user_id)
        if counter:
            for i in counter:
                # todo rework to redis
                await NotificationService.send_notification(i.id)
                yield {
                    "id": i.id,
                    "event": i.event,
                    "data": json.dumps(i.data),
                }

        await asyncio.sleep(MESSAGE_STREAM_DELAY)


@router.get("/stream", dependencies=[Depends(bearer)])
async def message_stream(request: Request, token: str = Depends(bearer)):
    user = user_payload(token)
    return EventSourceResponse(event_generator(request, user.get('id')))


@router.get('/unread-count', dependencies=[Depends(bearer)])
async def notification_unread_count(token: str = Depends(bearer)):
    return await NotificationService.get_count_unread_notification(user_payload(token))


@router.get('', dependencies=[Depends(bearer)])
async def get_notification(token: str = Depends(bearer), skip: int = 0, limit: int = 20):
    user = user_payload(token)

    return await NotificationService.get_notification(GetNotificationDto(user_id=str(user.get('id'))), limit, skip)


@router.put('/{notification_id}/read', dependencies=[Depends(bearer)])
async def read_notification(notification_id: str):
    return await NotificationService.read_notification(notification_id)


# read_all_notification
@router.put('/read-all', dependencies=[Depends(bearer)])
async def get_notification(token: str = Depends(bearer)):
    return await NotificationService.read_all_notification(user_payload(token))
