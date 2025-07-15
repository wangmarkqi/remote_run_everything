from remote_run_everything.db.crud_sqlalchemy import Crud
from remote_run_everything.deploy.record_mod import Up, Down
from remote_run_everything.db.crude_duck import CrudeDuck
from remote_run_everything.deploy.by_http_tool import ByHttpTool


class ByHttp:
    def __init__(self, host, local, remote, dbpath):
        self.host = host
        self.local = local
        self.remote = remote
        self.engine = Crud().sqlite_engine(dbpath)
        self.con = CrudeDuck().install_sql_ext(dbpath)
        self.crud = Crud()
        self.crud.create_table(self.engine, Up)
        self.crud.create_table(self.engine, Down)
        self.t = ByHttpTool()

    def down(self, disallow_keys=None):
        remote_files = self.t.all_remote_path(self.host, self.remote, disallow_keys)
        mod = Down
        add_l = []
        for dic in remote_files:
            path = dic['path']
            t = dic['time']
            sql = f"select * from down where path='{path}' and time='{t}' "
            res = self.con.sql(sql).fetchone()
            if res is not None: continue
            print("down", dic)
            self.con.execute(f"delete from down where path='{path}' ")
            self.t.pull(self.host, path, self.local, self.remote)
            add_l.append(dic)
        self.con.commit()
        self.crud.insert_many(self.engine, mod, add_l)

    def up(self, disallow_keys=None):
        mod = Up
        loc_files = self.t.all_local_path(self.local, disallow_keys)
        add_l = []
        for dic in loc_files:
            path = dic['path']
            t = dic['time']
            sql = f"select * from up where path='{path}' and time='{t}' and host='{self.host}' "
            res = self.con.sql(sql).fetchone()
            if res is not None: continue
            print("up==", dic)
            sql = f"delete from  up where path='{path}' and  host='{self.host}'"
            self.con.execute(sql).commit()
            self.t.push(self.host, path, self.local, self.remote)
            dic['host'] = self.host
            add_l.append(dic)
        self.con.commit()
        self.crud.insert_many(self.engine, mod, add_l)
