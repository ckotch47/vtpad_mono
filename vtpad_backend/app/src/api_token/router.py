from fastapi import APIRouter, Depends

from .service import ApiTokenService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/api-token',
    tags=['api-token'],
    responses={404: {"description": "Not found"}},
)


@router.get('/', dependencies=[Depends(bearer)])
async def get_by_user(token: str = Depends(bearer)):
    return await ApiTokenService.get_by_user(token)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: ApiTokenCreateDto, token: str = Depends(bearer)):
    raw_token, api_token = await ApiTokenService.create(dto, token)
    return {
        'token': raw_token,
        'id': str(api_token.id),
        'name': api_token.name,
        'scopes': api_token.scopes,
        'expires_at': api_token.expires_at.isoformat() if api_token.expires_at else None,
        'created_at': api_token.created_at.isoformat(),
    }


@router.delete('/{token_id}', dependencies=[Depends(bearer)])
async def revoke(token_id: str, token: str = Depends(bearer)):
    return await ApiTokenService.revoke(token_id, token)
