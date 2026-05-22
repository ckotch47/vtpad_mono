from fastapi import APIRouter, Depends

from .service import NewsService
from ..common.crypto import bearer, user_payload

router = APIRouter(
    prefix='/v1/news',
    tags=['news'],
    responses={404: {"message": "Not found"}},
    deprecated=True
)

news_service = NewsService()


@router.get('', dependencies=[Depends(bearer)])
async def get_news_for_user(token: str = Depends(bearer)):
    return await news_service.get_news_for_user(user_payload(token))


@router.patch('read', dependencies=[Depends(bearer)])
async def read_news_by_id(news_id: str, token: str = Depends(bearer)):
    return await news_service.read_news(news_id, user_payload(token))


@router.get('unread', dependencies=[Depends(bearer)])
async def get_news_count_unread(token: str = Depends(bearer)):
    return await news_service.get_unread_count(user_payload(token))
