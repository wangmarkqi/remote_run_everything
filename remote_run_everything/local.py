import os
from remote_run_everything.remote import Remote


class Local:
    def __init__(self, conf):
        self.c = conf
    
    def get_local(self,dir):
        res = []
        for root, dir, files in os.walk(dir):
            for f in files:
                e = os.path.join(root, f)
                res.append(e.replace("\\", "/"))
        return res
    
    def upload(self,dir):
        r = Remote(self.c)
        files = self.get_local(dir)
        local_len = len(self.c.local_root)
        data=[]
        for lf in files:
            relativ_loc = lf[local_len:]
            if not relativ_loc.startswith('/'):
                relativ_loc = "/" + relativ_loc
            rf = self.c.remote_root + relativ_loc
            data.append((lf,rf))
        r.upload(data)
        return "success"
    
    def download(self,dir):
        r = Remote(self.c)
        files = r.get_remote(dir)
        remote_len = len(self.c.remote_root)
        data=[]
        for rf in files:
            relative_loc = rf[remote_len:]
            if not relative_loc.startswith("/"):
                relative_loc= "/" + relative_loc
            lf = self.c.local_root + relative_loc
            data.append((lf,rf))
        r.download(data)
        return "success"


