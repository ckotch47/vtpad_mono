import aioredis
from aioredis import Redis
from ..common.config import EnvConfig

env_config = EnvConfig()


class RedisService:
    redis: Redis

    def __init__(self, db=0):
        if env_config.redis_user and env_config.redis_password:
            self.redis = aioredis.from_url(
                f"redis://{env_config.redis_host}:{env_config.redis_port}",
                db=db,
                username=env_config.redis_user,
                password=env_config.redis_password,
                decode_responses=True
            )
        else:
            self.redis = aioredis.from_url(f"redis://{env_config.redis_host}:{env_config.redis_port}")

    async def set_string(self, key: str, value: str, seconds: int = 259200):
        try:
            await self.redis.set(
                name=key,
                value=value,
                ex=seconds,
                xx=False,
                keepttl=False
            )
            return True
        except Exception as e:
            print('set string into redis', e)
            return False

    async def get_string(self, key) -> str | None:
        try:
            temp = await self.redis.get(key)
            return temp.decode("utf-8")
        except Exception as e:
            print('get string from redis', e)
            return None

    async def del_by_key(self, key):
        try:
            await self.redis.delete(key)
        except:
            pass
