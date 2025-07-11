import os, pymysql
from urllib.parse import quote_plus

from sqlalchemy import create_engine, select, update, and_, insert, delete


class Crud:
    def sqlite_engine(self, dbpath):
        dir = os.path.dirname(dbpath)
        os.makedirs(dir, exist_ok=True)
        url = f"sqlite:///{dbpath}"
        engine = create_engine(url, future=True, connect_args={'timeout': 30, 'check_same_thread': False})
        return engine

    def pg_url(self, user, pwd, host, port, db):
        f = lambda x: quote_plus(x)
        return f"postgresql://{f(user)}:{f(pwd)}@{f(host)}:{port}/{db}"

    def pg_engine(self, user, pwd, host, port, db):
        return create_engine(self.pg_url(user, pwd, host, port, db), pool_recycle=3600, pool_size=80, max_overflow=-1,
                             echo=False,
                             future=True)

    def mysql_url(self, user, pwd, host, port, db):
        f = lambda x: quote_plus(x)
        return f"mysql+pymysql://{f(user)}:{f(pwd)}@{f(host)}:{port}/{db}"

    def mysql_engine(self, user, pwd, host, port, db):
        # print(f"sqlacodegen {url} >> {db}.py")
        return create_engine(self.mysql_url(user, pwd, host, port, db), pool_recycle=3600, pool_size=80,
                             max_overflow=-1, echo=False,
                             future=True)

    def drop_table(self, engine, mod):
        mod.__table__.drop(engine)

    def create_table(self, engine, mod):
        mod.__table__.create(engine, checkfirst=True)

    def exist_id(self, engine, mod, cond):
        with engine.connect() as conn:
            stmt = select(mod).where(cond).limit(1)
            id = conn.scalar(stmt)
            if id is not None:
                return id
            return None

    def table_columns(self, mod):
        if "__annotations__" in mod.__dict__:
            cols = mod.__dict__['__annotations__'].keys()
        else:
            cols = [i for i in mod.__dict__.keys() if not i.startswith("__")]
        return cols

    def insert_many(self, engine, mod, l):
        if len(l)==0:return
        cols = self.table_columns(mod)
        with engine.connect() as conn:
            for dic in l:
                dic = {k: v for k, v in dic.items() if k in cols}
                stmt = insert(mod).values(dic)
                conn.execute(stmt)
            conn.commit()

    def insert_one(self, engine, mod, dic):
        cols = self.table_columns(mod)
        dic = {k: v for k, v in dic.items() if k in cols}
        with engine.connect() as conn:
            stmt = insert(mod).values(dic)
            conn.execute(stmt)
            conn.commit()

    def update_by_id(self, engine, mod, id, dic):
        cols = self.table_columns(mod)
        dic = {k: v for k, v in dic.items() if k in cols}
        with engine.connect() as conn:
            stmt = update(mod).where(mod.id == id).values(dic)
            conn.execute(stmt)
            conn.commit()

    def upsert(self, engine, mod, cond, dic):
        id = self.exist_id(engine, mod, cond)
        if id is not None:
            self.update_by_id(engine, mod, id, dic)
            return
        self.insert_one(engine, mod, dic)

    def delete_by_id(self, engine, mod, id):
        with engine.connect() as conn:
            stmt = delete(mod).where(mod.id == id)
            conn.execute(stmt)
            conn.commit()

    def delete(self, engine, mod, cond):
        id = self.exist_id(engine, mod, cond)
        if id is not None:
            self.delete_by_id(engine, mod, id)
