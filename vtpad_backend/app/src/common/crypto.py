from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from .config import EnvConfig

env_config = EnvConfig()

bearer = OAuth2PasswordBearer(tokenUrl="auth", auto_error=True, scheme_name='bearer')

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = env_config.secret_key #"09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = env_config.algorithm #"HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = env_config.access_token_expire #30000
REFRESH_TOKEN_EXPIRE_MINUTES = env_config.refresh_token_expire #60000
##

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def decode_refresh(refresh: str):
    return jwt.decode(refresh, SECRET_KEY, ALGORITHM)


def user_payload(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="not auth")


async def get_user_id_by_token(token: str) -> str:
    payload = user_payload(token)
    return payload.get("id", "")
