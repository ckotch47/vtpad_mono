from fastapi import APIRouter, Depends, Request

from ..common.crypto import bearer
from .service import (
    create_public_link,
    get_public_link_metadata,
    get_shared_run,
    revoke_public_link,
)

router = APIRouter(prefix='/v2/test-run', tags=['public-run-links'])

@router.post('/{run_id}/public-link', dependencies=[Depends(bearer)])
async def create(run_id: str, request: Request):
    return await create_public_link(run_id, request)


@router.get('/{run_id}/public-link', dependencies=[Depends(bearer)])
async def read(run_id: str, request: Request):
    return await get_public_link_metadata(run_id, request)


@router.delete('/{run_id}/public-link', dependencies=[Depends(bearer)])
async def revoke(run_id: str, request: Request):
    return await revoke_public_link(run_id, request)


@router.get('/public/shared')
async def redeem(request: Request):
    authorization = request.headers.get('authorization', '')
    scheme, separator, token = authorization.partition(' ')
    if not separator or scheme.lower() != 'bearer' or not token or token != token.strip():
        # Still pass unauthenticated attempts through the shared IP rate limit.
        return await get_shared_run('', request)
    return await get_shared_run(token, request)
