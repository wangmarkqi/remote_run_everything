import jinja2, requests, os
import pandas as pd
import socket, os, tomllib
import base64
import os, signal
import subprocess, sys
from remote_run_everything.tools.common1 import Common1


class Common(Common1):
    @property
    def local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def read_conf(self, path=None):
        if path is None:
            d = "D://mypy/conf" if os.name == 'nt' else "/data/mypy/conf"
            n = "win" if os.name == "nt" else self.local_ip
            path = f"{d}/{n}.toml"
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return data


    def supervise(self, workdir, pidfile, app):
        if os.path.exists(pidfile):
            with open(pidfile, "rb") as f:
                pid = f.read().decode()
            print("exist pid===", pid)
        try:
            os.kill(int(pid), signal.SIGTERM)
        except Exception as e:
            print("kill err==", e)

        print("chdir====", workdir)
        os.chdir(workdir)
        process = subprocess.Popen(app, creationflags=subprocess.CREATE_NEW_CONSOLE)
        print("new pid====", process.pid)
        with open(pidfile, "wb") as f:
            s = str(process.pid).encode()
            f.write(s)
        sys.exit()


if __name__ == '__main__':
    g = Common()
    a = g.prefix_zero(5, 111)
