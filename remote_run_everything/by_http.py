import base64
import glob
import os

from remote_run_everything.hist_pickle import Hist


class ByHttp:
    def __init__(self, record_k, record_dir, local_root, remote_root):
        self.record_k = record_k
        self.record_dir = record_dir
        self.local = local_root
        self.remote = remote_root

    def will_push(self, lpath):
        h = Hist(self.record_dir)
        return h.upload_record_or_not(self.record_k, lpath)

    def push_list(self):
        for f in glob.glob(f"{self.local}/**/*", recursive=True):
            if os.path.isdir(f): continue
            # 记录本地文件修改时间(k,lpath):mtime
            path = self.loc2remote(f)

            dic = {
                "rpath": path,  # remote path
                "lpath": f,
                "b64": self.readb64(f),
            }
            yield dic

    def pull_list(self, l):  # [{rpath,mtime}]
        res = []
        for i in l:
            if i['path'] == "": continue
            res.append({
                "rpath": i['path'],
                "lpath": self.remote2loc(i['path']),
                "time": i['time'],
            })
        return res

    def will_pull(self, lpath, rtime):
        h = Hist(self.record_dir)
        return h.download_record_or_not(self.record_k, lpath, rtime)

    def writeb64(self, path, b64):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        content = base64.b64decode(b64)
        with open(path, "wb") as f:
            f.write(content)
            os.chmod(path, 0o777)

    def readb64(self, f):
        with open(f, "rb") as file:
            encoded_string = base64.b64encode(file.read())
            return encoded_string.decode()

    def loc2remote(self, f):
        rela = os.path.relpath(f, self.local)
        return f"{self.remote}/{rela}"

    def remote2loc(self, f):
        rela = os.path.relpath(f, self.remote)
        return f"{self.local}/{rela}"
