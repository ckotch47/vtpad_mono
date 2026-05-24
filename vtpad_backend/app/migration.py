import json
from os.path import dirname, basename, isfile, join
import glob

from tortoise import Tortoise, run_async

from .src import common

config = common.EnvConfig()


async def init():
    print('migration start \n\n ')
    await Tortoise.init(
        db_url=f'postgres://'
               f'{config.db_user}:{config.db_password}'
               f'@{config.db_host}:{config.db_port}/{config.db_name}',
        modules={'models': []})


class RunMigration:

    def read_file(self, file_name):
        with open(file_name) as file:
            return json.load(file)

    def save_file(self, file_name, data):
        with open(file_name, 'w') as file:
            file.write(data)
        return True

    async def find_migration_in_bd(self, migration_name: str):
        conn = Tortoise.get_connection('default')
        rows = await conn.execute_query_dict(
            "SELECT id FROM migrationmodel WHERE name = $1",
            [migration_name]
        )
        return rows

    async def save_migration_name_into_bd(self, migration_name: str):
        conn = Tortoise.get_connection('default')
        await conn.execute_query(
            "INSERT INTO migrationmodel (id, create_date, name) "
            "VALUES (gen_random_uuid(), current_timestamp, $1)",
            [migration_name]
        )

    async def run_migration(self):
        migration_src = f'{dirname(__file__)}/src/migration/data'
        modules = glob.glob(join(migration_src, "*.json"))
        __all__ = sorted([basename(f) for f in modules if isfile(f)])

        for i in __all__:
            temp = self.read_file(f'{migration_src}/{i}')
            sql_all = temp['data']
            existing = await self.find_migration_in_bd(i)
            if not existing:
                print(f'Running migration: {i}')
                await self.save_migration_name_into_bd(i)
                for sql in sql_all:
                    try:
                        result = await self.run_sql(sql)
                        print(result)
                    except Exception as e:
                        print(f'Error running SQL in {i}: {e}')
                        raise

        await Tortoise.close_connections()

    async def run_sql(self, sql, params=None):
        conn = Tortoise.get_connection('default')
        if params:
            return await conn.execute_query(sql, params)
        return await conn.execute_query(sql)


migration = RunMigration()
