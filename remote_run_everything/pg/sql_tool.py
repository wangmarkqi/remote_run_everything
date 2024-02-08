from datetime import datetime
import json


class SqlTool:
    def convert_type(self, dic):
        res = {}
        for k, v in dic.items():
            if isinstance(v, int):
                res[k] = "INTEGER"
            elif isinstance(v, float):
                res[k] = "DECIMAL"
            elif isinstance(v, bool):
                res[k] = "BOOLEAN"
            elif isinstance(v, list) or isinstance(v, dict):
                res[k] = "JSON"
            else:
                res[k] = "TEXT"

        return res

    def k2sqlv(self, dic):
        res = {}
        for k, v in dic.items():
            if isinstance(v, float) or isinstance(v, int):
                res[k] = f"{v}"
            elif isinstance(v, list) or isinstance(v, dict):
                res[k] = f"'{json.dumps(v)}'"
            elif isinstance(v, bool):
                res[k] = f"'true'" if v else f"'false'"
            else:
                res[k] = f"'{v}'"
        return res

    def where(self, dic):
        l = []
        for k, v in dic.items():
            if isinstance(v, str):
                l.append(f"{k} = '{v}'")
            else:
                l.append(f"{k} = {v}")
        return " AND ".join(l)


if __name__ == '__main__':
    s = SqlTool()
    a = datetime.today()
    print(a, type(a), isinstance(a, datetime))
