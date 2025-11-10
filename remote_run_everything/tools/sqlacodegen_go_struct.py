import os
from dataclasses import dataclass

'''
sqlacodegen mssql+pyodbc://sa:a@127.0.0.1:1433/pstarback?driver=ODBC+Driver+17+for+SQL+Server > ./test.py
'''


@dataclass
class Tab:
    stname: str
    tbname: str
    fields: list


class Sql2go:
    def __init__(self, path):
        self.path = path

    def read_lines(self):
        with open(self.path, 'r') as f:
            content = f.readlines()
            return content

    def replace(self, s, l):
        for i in l:
            s = s.replace(i, "")
        return s

    def split_cls(self):
        res = []
        content = self.read_lines()
        cur_cls = ""
        t = Tab("", "", [])
        for s in content:
            if s.startswith("class "):
                if cur_cls != "":
                    res.append(t)
                t = Tab("", "", [])
                stname = self.replace(s, [" ", "\n", "class", "(Base)", ":"])
                cur_cls = stname
                t.stname = cur_cls
            elif "__tablename__" in s:
                tbname = self.replace(s, [" ", "__tablename__", "\n", "="])
                t.tbname = tbname
            elif "= Column" in s:
                t.fields.append(s)
        for t in res:
            ll = []
            for s in t.fields:
                ll.append({
                    "field": self.parse_name(s),
                    "tag": self.parse_tag(s),
                    "ty": self.parse_ty(s)
                })
            t.fields = ll
        print(res)
        return res

    def parse_name(self, s):
        name = s.split("=")[0].replace(" ", "")
        return name

    def parse_ty(self, s):
        if "DateTime" in s:
            ty = "time.time"
        elif "String" in s:
            ty = "string"
        elif "BigInteger" in s:
            ty = "int64"
        elif "Integer" in s or "TINYINT" in s:
            ty = "int32"
        elif "CHAR" in s:
            ty = "string"
        elif "Float" in s or "MONEY" in s:
            ty = "float32"
        elif "DECIMAL" in s:
            ty = "float64"
        else:
            ty = "unk"
        return ty

    def parse_tag(self, s):
        name = s.split("=")[0].replace(" ", "").lower()
        tag = ""
        if "primary_key=True" in s:
            tag = f'''`xorm:"pk not null '{name}'" json:"{name}"`'''
        elif "nullable=False" in s:
            tag = f'''`xorm:"not null '{name}'" json:"{name}"`'''
        else:
            tag = f'''`xorm:"'{name}'" json:"{name}"`'''
        return tag

    def write_go(self):
        res = self.split_cls()
        lines = []
        for tab in res:
            header = f"type {tab.stname} struct " + "{"
            st = [header]
            for f in tab.fields:
                ss = f"{f['field']} {f['ty']} {f['tag']}"
                st.append(ss)
            st.append("}" + "\r\n")
            lines.append("\n".join(st))
        ss = "package mod" + "\r\n" + "".join(lines)
        with open("./mod.go", 'w') as f:
            f.write(ss)
        os.system("go fmt mod.go")


if __name__ == '__main__':
    s = Sql2go("./pstarback.py")
    s.write_go()
