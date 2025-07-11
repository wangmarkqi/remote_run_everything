import sqlite3, os, json

from remote_run_everything.nosql.no_sql_tool import NosqlTool

from remote_run_everything.db.crude_duck import CrudeDuck


class Nosql:
    def __init__(self, dbpath=None):
        self.t = NosqlTool()
        self.cd = CrudeDuck()
        self.db_path = self.t.default_db_path(dbpath)
        self.conn = self.cd.install_sql_ext(self.db_path)
        self.conn.create_function("my_q", self.t.query)
        self.table = None

    def drop_db(self):
        os.remove(self.db_path)

    def drop_table(self):
        assert self.table is not None
        self.cd.drop_table(self.conn, self.table)
        self.table=None

    def __getitem__(self, table):
        self.table = table
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        conn.execute('pragma journal_mode=wal')
        sql = f'''CREATE TABLE IF NOT EXISTS {table} (id  INTEGER PRIMARY KEY AUTOINCREMENT, data text)'''
        conn.execute(sql)
        return self

    def insert_one(self, dic):
        assert self.table is not None
        value = json.dumps(dic)
        sql=f"insert INTO {self.table} (data) VALUES ('{value}')"
        self.conn.execute(sql)
        self.conn.commit()

    def find(self, query={}):
        return self.t.find(self.conn, self.table, query)

    def delete(self, query={}):
        return self.t.delete(self.conn, self.table, query)

    # 保证queery唯一,最后会隐含删除
    def upsert_one(self, query, dic):
        assert self.table is not None
        l = self.find(query)
        if len(l) == 0:
            return self.insert_one(dic)
        retain = l[0]
        self.t.revise_one(self.conn, self.table, retain, dic)
        rest_ids = [i['id'] for i in l if i['id'] != retain["id"]]
        if len(rest_ids) > 0:
            self.cd.delete_by_ids(self.conn, self.table, rest_ids)
            self.conn.commit()


if __name__ == '__main__':
    db = Nosql()
    db.drop_db()
    t = "test"
    col = db['test']
    dic = {"a": 2, "b": 456, 'c': "adf", "d": "2020-02-02"}
    col.insert_one(dic)
    dic = {"a": 56, "b": 456, 'c': "adf", "d": "2020-07-02"}
    col.insert_one(dic)
    q = {"a": 2}
    print(111, col.find(q))
    db.upsert_one(q, {"b": 999})
    q = {"a": 2}
    print(222, col.find(q))
