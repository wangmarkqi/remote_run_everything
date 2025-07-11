import sqlite3, os, json, arrow
from remote_run_everything.db.crude_duck import CrudeDuck


class NosqlTool:
    def __init__(self):
        self.cd = CrudeDuck()

    def default_db_path(self, db_path):
        if db_path is None:
            db_path = "D://wq/temp/emongo.db" if os.name == 'nt' else "/data/temp/emongo.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return db_path

    def op_match(self, opdic, dvalue):
        for op, qv in opdic.items():
            if op == "$gt":
                return dvalue > qv
            elif op == "$gte":
                return dvalue >= qv
            elif op == "$lt":
                return dvalue < qv
            elif op == "$lte":
                return dvalue < qv
            elif op == "$ne":
                return dvalue != qv
            elif op == "$in":
                return dvalue in qv
            elif op == "$between":
                return (dvalue >= qv[0]) and (dvalue <= qv[1])
        return False

    def query(self, data: str, query: str) -> int:
        d = json.loads(data)
        q = json.loads(query)
        if len(q) == 0: return 1
        for qk, qv in q.items():
            # 查询的key在数据不存在
            if qk not in d.keys(): return 0
            if isinstance(qv, dict):
                if not self.op_match(qv, d[qk]):
                    return 0
            elif d[qk] != qv:
                return 0
        return 1

    def add_id(self, l):
        res = []
        for i in l:
            dic = json.loads(i['data'])
            dic['id'] = i['id']
            res.append(dic)
        return res

    def find(self, conn, table, query={}):
        assert table is not None
        qs = json.dumps(query)
        sql = f"select * from {table} where my_q(data,'{qs}') = 1 "
        df = conn.sql(sql).df()
        if len(df) == 0: return []
        return self.add_id(df.to_dict("records"))

    def delete(self, conn, table, query={}):
        assert table is not None
        l = self.find(conn, table, query)
        if len(l) == 0: return
        ids = [i['id'] for i in l]
        self.cd.delete_by_ids(conn, table, ids)
        conn.commit()

        # 保证queery唯一,最后会隐含删除

    def revise_one(self, conn, table, ex, dic):
        assert table is not None
        id = ex["id"]
        v = {**ex, **dic}
        s = json.dumps(v)
        sql = f'''update {table} set data='{s}' where id={id}
    '''
        conn.execute(sql)
        conn.commit()
