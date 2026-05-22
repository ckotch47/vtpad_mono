

from fastapi import APIRouter, Request

from .dto import *
from .rto import RefreshTokenRto
from .service import AuthService


router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"],
    responses={404: {"message": "Not found"}},
)

authService = AuthService()


@router.post('', response_model=RefreshTokenRto)
async def auth(user: AuthUserDto, request: Request):
    return await authService.authenticate_user(user, request.client.host)


@router.post('/refresh', response_model=RefreshTokenRto)
async def refresh_token(dto: RefreshTokenDto, request: Request):
    return await authService.refresh_token(dto.refresh_token, request.client.host)
