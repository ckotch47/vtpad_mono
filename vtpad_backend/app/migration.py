import json
from os.path import dirname, basename, isfile, join
import glob
import re

from tortoise import Tortoise, run_async
from tortoise.transactions import in_transaction

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

    async def find_migration_in_bd(self, migration_name: str, connection=None):
        conn = connection or Tortoise.get_connection('default')
        rows = await conn.execute_query_dict(
            "SELECT id FROM migrationmodel WHERE name = $1",
            [migration_name]
        )
        return rows

    async def save_migration_name_into_bd(self, migration_name: str, connection=None):
        conn = connection or Tortoise.get_connection('default')
        await conn.execute_query(
            "INSERT INTO migrationmodel (id, create_date, name) "
            "VALUES (gen_random_uuid(), current_timestamp, $1)",
            [migration_name]
        )

    async def run_migration(self):
        lock_id_1 = 197938107
        lock_id_2 = 1
        db = Tortoise.get_connection('default')
        try:
            async with db.acquire_connection() as lock_connection:
                await lock_connection.execute(
                    "SELECT pg_advisory_lock($1, $2)", lock_id_1, lock_id_2
                )
                try:
                    await self._run_migrations_locked()
                finally:
                    await lock_connection.execute(
                        "SELECT pg_advisory_unlock($1, $2)", lock_id_1, lock_id_2
                    )
        finally:
            await Tortoise.close_connections()

    async def _run_migrations_locked(self):
        migration_src = f'{dirname(__file__)}/src/migration/data'
        modules = glob.glob(join(migration_src, "*.json"))
        __all__ = sorted([basename(f) for f in modules if isfile(f)])

        for i in __all__:
            temp = self.read_file(f'{migration_src}/{i}')
            sql_all = temp['data']
            if temp.get('transactional', True):
                async with in_transaction() as connection:
                    existing = await self.find_migration_in_bd(i, connection)
                    if not existing:
                        print(f'Running migration: {i}')
                        for sql in sql_all:
                            try:
                                result = await self.run_sql(sql, connection=connection)
                                print(result)
                            except Exception as e:
                                print(f'Error running SQL in {i}: {e}')
                                raise
                        # Mark it applied only after every DDL statement succeeds.
                        await self.save_migration_name_into_bd(i, connection)
            else:
                existing = await self.find_migration_in_bd(i)
                if not existing:
                    print(f'Running non-transactional migration: {i}')
                    await self.drop_invalid_indexes(temp.get('cleanup_invalid_indexes', []))
                    for sql in sql_all:
                        try:
                            result = await self.run_sql(sql)
                            print(result)
                        except Exception as e:
                            print(f'Error running SQL in {i}: {e}')
                            raise
                    # Concurrent DDL cannot be transactional.  Statements must
                    # be idempotent so a failed startup can safely retry them.
                    await self.save_migration_name_into_bd(i)

    async def run_sql(self, sql, params=None, connection=None):
        conn = connection or Tortoise.get_connection('default')
        if params:
            return await conn.execute_query(sql, params)
        return await conn.execute_query(sql)

    async def drop_invalid_indexes(self, index_names: list[str]):
        """Remove only named invalid concurrent indexes before an idempotent retry."""
        conn = Tortoise.get_connection('default')
        for index_name in index_names:
            if not re.fullmatch(r'[a-z0-9_]+', index_name):
                raise ValueError(f'Unsafe index name in migration: {index_name}')
            invalid_indexes = await conn.execute_query_dict(
                'SELECT c.relname FROM pg_index i '
                'JOIN pg_class c ON c.oid = i.indexrelid '
                'JOIN pg_namespace n ON n.oid = c.relnamespace '
                'WHERE n.nspname = $1 AND c.relname = $2 AND NOT i.indisvalid',
                ['public', index_name],
            )
            if invalid_indexes:
                await conn.execute_query(
                    f'DROP INDEX CONCURRENTLY IF EXISTS public.{index_name}'
                )


migration = RunMigration()
