import json
from os.path import dirname, basename, isfile, join
import glob

from tortoise import Tortoise, run_async

from .src import common

config = common.EnvConfig()


#  register orm


async def init():
    # create connection with psql
    print('migration start \n\n ')
    await Tortoise.init(
        db_url=f'postgres://'
               f'{config.db_user}:{config.db_password}'
               f'@{config.db_host}:{config.db_port}/{config.db_name}',
        modules={'models': []})





class RunMigration:

    def read_file(self, file_name):
        file = open(file_name)
        temp_data: str = file.read()
        file.close()
        return json.loads(temp_data)

    def save_file(self, file_name, data):
        file = open(file_name, 'w')
        file.write(data)
        file.close()
        return True

    async def find_migration_in_bd(self, migration_name: str):
        # find into bd migration by name
        sql = f"SELECT id FROM migrationmodel WHERE name = '{migration_name}'"
        return (await self.run_sql(sql))[0]

    async def save_migration_name_into_bd(self, migration_name: str):
        # create new migration into bd
        sql = f"INSERT INTO migrationmodel (id, create_date, name) " \
              f"VALUES (gen_random_uuid(), current_timestamp, '{migration_name}')"
        return (await self.run_sql(sql))[0]

    async def run_sql(self, sql):
        conn = Tortoise.get_connection('default')
        try:
            return await conn.execute_query(sql)
        except Exception as e:
            print(e)
            return [0, []]

    async def run_migration(self):

        # init folder where saved migration files
        migration_src = f'{dirname(__file__)}/src/migration/data'

        # get migration all file with json extension
        modules = glob.glob(join(migration_src, "*.json"))
        __all__ = [basename(f) for f in modules if isfile(f)]

        # every *.json file
        for i in __all__:
            # get file data
            temp = self.read_file(f'{migration_src}/{i}')
            # get sql array from file
            sql_all = temp['data']
            # if not migration name into bd
            tmp = await self.find_migration_in_bd(i)
            if not tmp or tmp == 0:
                # save into bd
                await self.save_migration_name_into_bd(i)
                # run all sql into json [data]
                for sql in sql_all:
                    print(await self.run_sql(sql))

        await Tortoise.close_connections()
migration = RunMigration()
# run_async(migration.run_migration())
