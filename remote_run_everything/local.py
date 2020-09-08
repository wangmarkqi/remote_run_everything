import os
from remote_run_everything.conf import Conf
from remote_run_everything.remote import Remote


class Local:
    def __init__(self, conf):
        self.c = conf
        self.r = Remote(conf)
    
    def get_local(self,dir):
        res = []
        for root, dir, files in os.walk(dir):
            for f in files:
                e = os.path.join(root, f)
                res.append(e.replace("\\", "/"))
        return res
    
    
    
    def upload(self,dir):
        files = self.get_local(dir)
        local_len = len(self.c.local_root)
        for lf in files:
            relativ_loc = lf[local_len:]
            if not relativ_loc.startswith('/'):
                relativ_loc = "/" + relativ_loc
            rf = self.c.remote_root + relativ_loc
            self.r.upload(lf, rf)
        return "success"
    
    def download(self,dir):
        files = self.r.get_remote(dir)
        remote_len = len(self.c.remote_root)
        for rf in files:
            relative_loc = rf[remote_len:]
            if not relative_loc.startswith("/"):
                relative_loc= "/" + relative_loc
            lf = self.c.local_root + relative_loc
            self.r.download(lf,rf)
        return "success"


