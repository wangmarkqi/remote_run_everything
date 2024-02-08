from remote_run_everything.pg.sql_tool import SqlTool


class Sql:
    def __init__(self):
        self.tool = SqlTool()
        self.table=None

    def create_database(self,name,owner):
        return f'CREATE DATABASE "{name}" OWNER "{owner}"'
    # 此处table必须是mod,不可以表名称
    def create_table(self,  ty_ins):
        dic = self.tool.convert_type(ty_ins)
        l = [f"{k} {v}" for k, v in dic.items()]
        s = ",".join(l)
        return f"CREATE TABLE  IF NOT EXISTS {self.table} ( id serial PRIMARY KEY,{s});"

    def drop_table(self):
        return f"DROP TABLE IF EXISTS {self.table}"

    def insert_one(self,  dic):
        dic = self.tool.k2sqlv(dic)
        ks = ",".join(dic.keys())
        vs = ",".join(dic.values())
        return f"INSERT INTO {self.table} ( {ks} ) VALUES ( {vs} );"

    def delete(self,  where):
        s = f"DELETE  FROM {self.table} WHERE {self.tool.where(where)}"
        return s

    def find(self,  where):
        s = f"SELECT * FROM {self.table}"
        if where is None or len(where) == 0:
            return s
        s = f"{s} WHERE {self.tool.where(where)} "
        return s

    def update(self,  where, d):
        if where is None or len(where) == 0: raise "update where is None"
        for k in where.keys():
            d.pop(k, None)
        if len(d) == 0: raise "data is same with where"
        d = self.tool.k2sqlv(d)
        vs = [f" {k} = {v}" for k, v in d.items()]
        vs = ",".join(vs)
        return f"UPDATE {self.table} SET {vs} WHERE {self.tool.where(where)}"


if __name__ == '__main__':
    s = Sql()
    a = s.update("test", {"a": "name", "b": 3}, {"c": "xx", "d": 34})
    print(a)
