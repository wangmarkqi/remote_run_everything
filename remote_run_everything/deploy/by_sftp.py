import os.path
from remote_run_everything.db.crud_sqlalchemy import Crud
from remote_run_everything.deploy.record_mod import Up, Down
from remote_run_everything.db.crude_duck import CrudeDuck
from remote_run_everything.deploy.by_http_tool import ByHttpTool
import paramiko
from pathlib import Path

class BySftp:
    def __init__(self, host,port,user,pwd, local, remote, dbpath):
        self.host=host
        self.cli=self.sftp_cli(host,port,user,pwd)
        self.local = local
        self.remote = remote
        self.dbpath = dbpath
        self.t = ByHttpTool()
    def sftp_cli(self,host,port,user,pwd):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        transport = paramiko.Transport(host, port)
        transport.connect(None, user, pwd)
        cli= paramiko.SFTPClient.from_transport(transport)
        return cli

    def up(self, disallow_keys=None):
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

            rpath = self.t.loc2remote(path, self.local, self.remote)
            rpath=rpath.replace("\\","/")
            lpath=path.replace("\\","/")
            res=self.upload_file(rpath, lpath)
            print("up==", path,res)
            if res=="ok":
                sql = f"delete from  up where path='{path}' and  host='{self.host}'"
                con.execute(sql).commit()
                dic['host'] = self.host
                add_l.append(dic)
        con.commit()
        c.insert_many(eg, mod, add_l)

    def mkdirs(self,fpath):
        dpath = os.path.dirname(fpath)
        l=dpath.split('/')
        if len(l)==0:return
        if l[0]=="":l[0]="/"
        for i in range(len(l)+1):
            if i<=1:continue
            ll=l[:i]
            path=os.path.join(*ll)
            try:
                # default mod 777
                path=path.replace('\\','/')
                self.cli.mkdir(path)
            except Exception as e:
                pass

    def upload_file(self, rpath, lpath):
        self.mkdirs(rpath)
        try:
            self.cli.put(lpath, rpath)
            return "ok"
        except:
            return "fail"
