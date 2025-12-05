import duckdb, os, arrow


class CrudeDuck:

    def install_sql_ext(self, dbpath):
        dir = os.path.dirname(dbpath)
        os.makedirs(dir, exist_ok=True)
        sql = f"ATTACH '{dbpath}' AS db (TYPE sqlite,journal_mode wal);use db;"
        con = duckdb.connect()
        con.install_extension("sqlite")
        con.load_extension("sqlite")
        con.sql(sql)
        return con

    def install_pg_ext(self, user, pwd, host, port, dbname):
        sql = f'''ATTACH 'dbname={dbname} user={user} 
            host={host} port={port} connect_timeout=10 password={pwd}'
             AS {dbname} (TYPE postgres);use {dbname};'''
        con = duckdb.connect()
        con.install_extension("postgres")
        con.load_extension("postgres")
        con.sql(sql)
        return con

    def install_mysql_ext(self, user, pwd, host, port, dbname):
        con = duckdb.connect()
        con.install_extension("mysql")
        con.load_extension("mysql")
        sql = f"ATTACH 'host={host} user={user} password={pwd} port={port} database={dbname}' AS msqldb (TYPE MYSQL);"
        con.sql(sql)
        con.sql(f"USE msqldb;")
        return con

    def scheme(self, con, db, table, dbtype):
        # for mysql db== dbname ; for pg db==public for sqlite db=main
        if dbtype == "mysql":
            db = db
        elif dbtype == "sqlite3":
            db = "main"
        elif dbtype == "pg":
            db = "public"
        else:
            db = db
        sql = f'''  SELECT column_name, data_type FROM information_schema.columns
    WHERE table_schema = '{db}' AND table_name   = '{table}';
            '''
        scheme = {i[0]: i[1] for i in con.sql(sql).fetchall()}
        return scheme

    def quot_comma(self, l):
        return ','.join([f"'{i}'" for i in l])

    def max_id(self, con, table):
        sql = f'select max(id) from {table}'
        a = con.sql(sql).fetchone()
        if a is None or a[0] is None: return 0
        return a[0] + 1

    def sql_from_ty(self, ty, v):
        if v is None: return None
        ty = ty.upper()
        if ty in ['BIGINT', "TINYINT", "INTEGER", "BOOLEAN"]:
            return str(int(v))
        if ty in ["VARCHAR"]:
            return f"'{str(v)}'"
        if "TIMESTAMP" in ty:
            return f"'{arrow.get(v).format()[:19]}'"
        return None

    def dic2sql(self, data, scheme):
        dic = {}
        for k, v in data.items():
            if k not in scheme.keys(): continue
            tyv = self.sql_from_ty(scheme[k], v)
            if tyv is not None:            dic[k] = tyv
        if len(dic) == 0:
            return "", ""
        cols = ", ".join(dic.keys())
        values = ", ".join(dic.values())
        return f"({cols})", f"({values})"

    def list2sql(self, l, scheme):
        cols = ""
        values = ""
        for data in l:
            dic = {}
            for k, v in data.items():
                if k not in scheme.keys(): continue
                tyv = self.sql_from_ty(scheme[k], v)
                if tyv is not None:   dic[k] = tyv
            if len(dic) == 0:
                continue
            cols = ", ".join(dic.keys())
            s = ", ".join(dic.values())
            values = values + f"({s}),"
        return f"({cols})", values

    def insert_many(self, con, db, table, data, dbtype=""):
        sche = self.scheme(con, db, table, dbtype)
        cols, values = self.list2sql(data, sche)
        if values == "": return
        sql = f'insert into {table} {cols} values {values}'
        con.execute(sql)

    def insert_one(self, con, db, table, data, dbtype=""):
        sche = self.scheme(con, db, table, dbtype)
        cols, values = self.dic2sql(data, sche)
        if values == "": return
        sql = f'insert into {table} {cols} values {values}'
        con.execute(sql)

    def drop_table(self, con, table):
        sql = f"drop table if exists {table}"
        con.execute(sql)

    def delete_by_ids(self, con, table, ids):
        ids = [str(i) for i in ids]
        ids = ','.join(ids)
        sql = f"delete from  {table} where id in ({ids})"
        con.execute(sql)

    def delete_by_id(self, con, table, id):
        sql = f"delete from  {table} where id = {id}"
        con.execute(sql)
