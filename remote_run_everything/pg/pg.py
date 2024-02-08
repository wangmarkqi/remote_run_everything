import asyncio

import asyncpg

from remote_run_everything.pg.sql import Sql

DB = {}


class PG:
    def __init__(self, host, port, user, pwd, dbName):
        self.sql = Sql()
        self.user = user
        self.pwd = pwd
        self.host = host
        self.port = port
        self.dbName = dbName
        self.db = None
        self.table = None

    def __getitem__(self, tb):
        self.table = tb
        self.sql.table = tb
        return self

    async def db_pool(self):
        global DB
        if DB.get(self.dbName, None) is None:
            DB[self.dbName] = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.pwd,
                database=self.dbName,
            )

        self.db = DB[self.dbName]
        print("DB", self.dbName, self.db)
        return self

    # 如果测算程序不调用,切数据库会出现pgadmin看不到表格的问题.
    def terminate_pool(self):
        print("will terminate", self.db)
        if self.db is not None:
            self.db.terminate()
        DB.pop(self.dbName, None)

    async def check(self):
        if self.dbName is None:
            raise "no db name"
        if self.table is None:
            raise "no table name"
        if self.db is None:
            await self.db_pool()

    async def execute(self, sql):
        print("sql===", sql)
        await self.check()
        async with self.db.acquire() as conn:
            await conn.execute(sql)

    async def trans(self, sqls):
        await self.check()
        async with self.db.acquire() as conn:
            async with conn.transaction():
                for sql in sqls:
                    print("sql===", sql)
                    await conn.execute(sql)

    async def create_db(self, name):
        await self.execute(self.sql.create_database(name, self.user))

    async def create_table(self, ins):
        await self.execute(self.sql.create_table(ins))

    async def drop_table(self):
        await self.execute(self.sql.drop_table())

    async def insert_one(self, dic):
        await self.execute(self.sql.insert_one(dic))

    async def delete(self, where):
        await self.execute(self.sql.delete(where))

    async def find(self, where=None):
        await self.check()
        sql = self.sql.find(where)
        print("sql==", sql)
        async with self.db.acquire() as conn:
            q = await conn.fetch(sql)
            return [dict(i) for i in q]

    async def update(self, where, dic):

        await self.execute(self.sql.update(where, dic))

    async def upsert(self, where, dic):
        res = await self.find(where)
        if len(res) == 0:
            await self.insert_one({**where, **dic})
        elif len(res) == 1:
            await self.update(where, dic)
        else:
            sqls = [self.sql.delete(where), self.sql.insert_one({**where, **dic})]
            await self.trans(sqls)

    def run(self, f):
        print(self.dbName, self.table)
        asyncio.get_event_loop().run_until_complete(f())
        self.terminate_pool()
