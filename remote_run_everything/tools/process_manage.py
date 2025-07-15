import psutil, os
from signal import SIGTERM  # or SIGKILL


class ProcessManage:
    # nosql is instance of Nosql or Nosqlmysql or Nqsqlpg
    def __init__(self, nosql):
        self.db = nosql
        self.col = self.db['pid']

    # 只需要在程序中引入这个函数,启动后会把pid存入数据库,然后有了pid,什么都有了
    def save_pid(self, name, cmd):
        dic = {"name": name, "cmd": cmd, "pid": os.getpid()}
        print("save pid", dic)
        self.col.insert_one(dic)

    def list_all(self):
        l = self.col.find({})
        pids = [i['pid'] for i in l]
        for proc in psutil.process_iter():
            if proc.pid in pids:
                print("list by pid==", proc)

    def kill_by_name(self, name):
        l = self.col.find({"name": name})
        for i in l:
            self.kiil_by_pid(i['pid'])

    def kiil_by_pid(self, pid):
        for proc in psutil.process_iter():
            if proc.pid == pid:
                print("kill by pid==", proc)
                proc.send_signal(SIGTERM)

    def kill_by_port(self, port):
        for proc in psutil.process_iter():
            for conns in proc.net_connections(kind='inet'):
                if conns.laddr.port == port:
                    print("kill by port==", port)
                    proc.send_signal(SIGTERM)

    def query_by_port(self, port):
        for proc in psutil.process_iter():
            for conns in proc.net_connections(kind='inet'):
                if conns.laddr.port == port:
                    print("list port==", conns)
                    return proc
