import pysftp, os
from remote_run_everything.conf import Conf

class Remote:
    def __init__(self,conf):
        self.c=conf
        self.shell = pysftp.Connection(self.c.host, username=self.c.user, password=self.c.pwd)
    def __del__(self):
        self.shell.close()

    def upload(self, local_f, remote_f):
        print (local_f,remote_f)
        remote_dir = os.path.dirname(remote_f)
        self.shell.makedirs(remote_dir, mode=777)
        self.shell.put(local_f, remote_f)
    
    def download(self, local_f, remote_f):
        local_dir = os.path.dirname(local_f)
        os.makedirs(local_dir, exist_ok=True, mode=777)
        self.shell.get(remote_f, local_f)
    
    def get_remote(self,dir):
        files=self._get_remote(dir,[])
        return files
    
    def _get_remote(self,root,res):
        data=self.shell.listdir(root)
        for d in data:
            new=os.path.join(root,d).replace("\\","/")
            if self.shell.isfile(new):
                res.append(new)
            else:
                self._get_remote(new,res)
        return res
    def cmd(self,cmds):
        common_cmds = ["/usr/bin/bash -c", f"cd {self.c.remote_root}"]
        all=common_cmds+cmds
        cmd=";".join(all)
        print (cmd)
        res = self.shell.execute(cmd)
        print("***********************")
        for i in res:
            print(i.decode("utf-8"))


if __name__ == '__main__':
    c=Conf()
    r = Remote(c)
    r.cmd(['cargo run'])
    # res=r.get_remote()
