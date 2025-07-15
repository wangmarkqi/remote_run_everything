import jinja2, requests,os
import pandas as pd
import socket, os, tomllib
import base64
from psutil import process_iter
from signal import SIGTERM  # or SIGKILL


class Common:
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

    def table_search(self, data, search):
        res = []
        for i in data:
            if search == "":
                res.append(i)
            elif search != "" and search in str(i):
                res.append(i)
        return res

    def split_page(self, numPerPage, cur, search, data):
        data = self.table_search(data, search)
        if data is None or len(data) == 0:
            return {"total": 0, "data": []}
        cur = int(cur)
        res = {"total": len(data)}
        n = int(numPerPage)
        total = len(data)
        start = (cur - 1) * n
        end = cur * n
        if start > total - 1:
            res['data'] = []
        elif end > total - 1:
            remainder = total % numPerPage
            if remainder == 0:
                res['data'] = data[-numPerPage:]
            else:
                res['data'] = data[-remainder:]
        else:
            res['data'] = data[start:end]
        return res

    def render(self, dir, html, data):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(f'{dir}/templates'))
        template = env.get_template(html)
        outputText = template.render(data=data)  # this is where to put args
        return outputText

    def inven_everyday(self, df, begin, end):
        df1 = df.groupby(by=['id', 'date']).sum()
        # 可以把复合index重新拆分成columns
        trades = df1.reset_index()
        trades['id'] = trades['id']
        trades['date'] = trades['date']
        # create a range of dates for the merged dataframe pd.datetime.today()
        if not begin:
            begin = df['date'].min()
        if not end:
            end = df['date'].max()
        index_of_dates = pd.date_range(begin, end).to_frame().reset_index(drop=True).rename(columns={0: 'date'}).astype(
            str)
        # create a merged dataframe with columns date / stock / stock_Tr.
        merged = pd.merge(index_of_dates, trades, how='left', on='date')
        # create a pivottable showing the shares_TR of each stock for each date
        shares_tr = merged.pivot(index='date', columns='id', values='q')
        shares_tr = shares_tr.dropna(axis=1, how='all').fillna(0)
        cumShares = shares_tr.cumsum()
        cumShares.index = cumShares.index.astype(str)
        return cumShares

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

    def prefix_zero(self, n, d):
        if len(str(d)) >= n: return str(d)[-n:]
        l = ["0"] * (n - len(str(d)))
        zeros = "".join(l)
        return f"{zeros}{d}"

    def kill_by_port(self, port):
        for proc in process_iter():
            for conns in proc.net_connections(kind='inet'):
                if conns.laddr.port == port:
                    print("kill by port==", port)
                    proc.send_signal(SIGTERM)

    def list_by_port(self, port):
        for proc in process_iter():
            for conns in proc.net_connections(kind='inet'):
                if conns.laddr.port == port:
                    print("list port==",conns)


if __name__ == '__main__':
    g = Common()
    a = g.prefix_zero(5, 111)
