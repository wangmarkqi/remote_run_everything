import os.path

from remote_run_everything.db.crud_sqlalchemy import Crud
from remote_run_everything.deploy.record_mod import Up, Down
from remote_run_everything.db.crude_duck import CrudeDuck
from remote_run_everything.deploy.by_http_tool import ByHttpTool


class ByHttp:
    def __init__(self, host, local, remote, dbpath):
        self.host = host
        self.local = local
        self.remote = remote
        self.dbpath = dbpath
        self.t = ByHttpTool()

    def down(self, disallow_keys=None):
        assert self.dbpath.endswith(".db"), "dbpath should be xxx.db"
        c = Crud()
        eg = c.sqlite_engine(self.dbpath)
        c.create_table(eg, Down)
        con = CrudeDuck().install_sql_ext(self.dbpath)
        remote_files = self.t.all_remote_path(self.host, self.remote, disallow_keys)
        mod = Down
        add_l = []
        for dic in remote_files:
            path = dic['path']
            t = dic['time']
            sql = f"select * from down where path='{path}' and time='{t}' "
            res = con.sql(sql).fetchone()
            if res is not None: continue
            print("down", dic)
            con.execute(f"delete from down where path='{path}' ")
            self.t.pull(self.host, path, self.local, self.remote)
            add_l.append(dic)
        con.commit()
        c.insert_many(eg, mod, add_l)

    def up(self, disallow_keys=None):
        if os.name == "nt":
            return self.up_win(disallow_keys)
        assert self.dbpath.endswith(".db"), "dbpath should be xxx.db"
        c = Crud()
        eg = c.sqlite_engine(self.dbpath)
        c.create_table(eg, Up)
        con = CrudeDuck().install_sql_ext(self.dbpath)
        mod = Up
        loc_files = self.t.all_local_path(self.local, disallow_keys)
        add_l = []
        for dic in loc_files:
            path = dic['path']
            t = dic['time']
            sql = f"select * from up where path='{path}' and time='{t}' and host='{self.host}' "
            res = con.sql(sql).fetchone()
            if res is not None: continue
            print("up==", dic)
            sql = f"delete from  up where path='{path}' and  host='{self.host}'"
            con.execute(sql).commit()
            self.t.push(self.host, path, self.local, self.remote)
            dic['host'] = self.host
            add_l.append(dic)
        con.commit()
        c.insert_many(eg, mod, add_l)

    def up_win(self, disallow_keys=None):
        from mongo_emb import PyMongoEmb
        if not os.path.exists(self.dbpath):
            os.makedirs(self.dbpath)
        assert os.path.isdir(self.dbpath), "dbpath should be dir"
        path = os.path.normpath(self.dbpath)
        db = PyMongoEmb(path)
        col = db['up']
        loc_files = self.t.all_local_path(self.local, disallow_keys)
        for dic in loc_files:
            dic['host'] = self.host
            # time path host
            if col.find_one(dic) is not None:
                continue
            if os.path.normpath(os.path.dirname(dic['path'])) == path: continue
            self.t.push(self.host, dic['path'], self.local, self.remote)
            print("up==", dic)
            col.update_one({"host": self.host, "path": dic['path']}, {"$set": {"time": dic['time']}}, upsert=True)
