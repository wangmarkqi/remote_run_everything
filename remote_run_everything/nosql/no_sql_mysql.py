import json

from remote_run_everything.nosql.no_sql_tool import NosqlTool
from remote_run_everything.tools.common import Common

from remote_run_everything.db.crude_duck import CrudeDuck


class NosqlMysql:
    def __init__(self, user, pwd, host, port, dbname):
        self.t = NosqlTool()
        self.cd = CrudeDuck()
        self.conn = self.cd.install_mysql_ext(user, pwd, host, port, dbname)
        self.conn.create_function("my_q", self.t.query)
        self.table = None

    def drop_table(self):
        assert self.table is not None
        self.cd.drop_table(self.conn, self.table)
        self.table = None

    def __getitem__(self, table):
        self.table = table
        sql = f'''CREATE TABLE IF NOT EXISTS {table} (
        id bigint NOT NULL  primary key ,
        data text
        )'''
        self.conn.execute(sql)
        self.conn.commit()
        return self

    def insert_one(self, dic):
        assert self.table is not None
        mid = self.cd.max_id(self.conn, self.table)
        value = json.dumps(dic)
        sql = f"insert INTO {self.table} (id,data) VALUES ({mid},'{value}')"
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
    conf = Common().read_conf()['mysql']['test']
    dbname = Common().read_conf()['mysql']['price']['test']
    t = 'nosql'
    no = NosqlMysql(**{**conf, "dbname": dbname})
    col = no[t]
    col.insert_one({"a": 1})
    print(col.find({}))
