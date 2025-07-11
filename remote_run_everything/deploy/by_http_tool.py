from remote_run_everything.tools.common import Common
import os, glob, arrow, requests


class ByHttpTool:

    def push(self, host, f, local, remote):
        b64 = Common().readb64(f)
        push_url = f"{host}/dep_writeb64"
        path = self.loc2remote(f, local, remote)
        pay = {"b64": b64, "path": path}
        res = requests.post(push_url, json=pay).json()
        return res

    def pull(self, host, f, local, remote):
        res = requests.post(f"{host}/readb64", json={"path": f}).json()
        b64 = res['data']
        path = self.remote2loc(f, local, remote)
        Common().writeb64(path, b64)
        return path

    def all_remote_path(self, host, root, disallow_keys=None):
        url = f"{host}/iterdir"
        res = requests.post(url, json={"root": root}).json()
        l = []
        for i in res['data']:
            path = i['path']
            if path == "": continue
            if not self.contain_disallow(path, disallow_keys):
                t = arrow.get(i['time']).format()
                l.append({"path": path, "time": t})
        return l

    def contain_disallow(self, path, disallow_keys):
        if disallow_keys is None or len(disallow_keys) == 0:
            return False
        for k in disallow_keys:
            if k in path:
                return True
        return False

    def all_local_path(self, root, disallow_keys=None):
        '''服务端提供的接口
        '''
        if not os.path.exists(root):
            return []
        files = glob.glob(f'{root}/**/*', recursive=True)
        res = []
        for path in files:
            if os.path.isdir(path):
                continue
            if not self.contain_disallow(path, disallow_keys):
                t = os.path.getmtime(path)
                t = arrow.get(t).format()
                res.append({"path": path, "time": t})
        return res

    def loc2remote(self, f, local, remote):
        rela = os.path.relpath(f, local)
        return f"{remote}/{rela}"

    def remote2loc(self, f, local, remote):
        rela = os.path.relpath(f, remote)
        return f"{local}/{rela}"
