import sqlite3, os, json, arrow

'''
kv = KeyValueStore('test.db')  # uses SQLite

print(len(kv))                 # 0 item
kv['hello1'] = 'you1'

del kv['hello1']
print(len(kv))                 # 2 items remaining
print('hello1' in kv)          # False, it has just been deleted!

kv['hello3'] = 'newvalue'      # redefine an already present key/value

print(kv.keys())               # ['hello2', 'hello3']
print(kv.values())             # ['you2', 'newvalue']
print(kv.items())              # [('hello2', 'you2'), ('hello3', 'newvalue')]

for k in kv:
    print(k, kv[k])

kv.close()  
'''


class KvStore(dict):
    def __init__(self, filename=None):
        self.db_path = self.default_db_path(filename)
        self.conn = sqlite3.connect(self.db_path, isolation_level=None)
        self.conn.execute('pragma journal_mode=wal')
        self.conn.execute("CREATE TABLE IF NOT EXISTS kv (key text unique, value text)")

    def default_db_path(self, db_path):
        if db_path is None:
            db_path = "D://wq/temp/decor.db" if os.name == 'nt' else "/data/temp/decor.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return db_path

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def __len__(self):
        rows = self.conn.execute('SELECT COUNT(*) FROM kv').fetchone()[0]
        return rows if rows is not None else 0

    def iterkeys(self):
        c = self.conn.cursor()
        for row in c.execute('SELECT key FROM kv'):
            yield row[0]

    def itervalues(self):
        c = self.conn.cursor()
        for row in c.execute('SELECT value FROM kv'):
            yield row[0]

    def iteritems(self):
        c = self.conn.cursor()
        for row in c.execute('SELECT key, value FROM kv'):
            yield row[0], row[1]

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def __contains__(self, key):
        key = str(key)
        return self.conn.execute('SELECT 1 FROM kv WHERE key = ?', (key,)).fetchone() is not None

    def __getitem__(self, key):
        key = str(key)
        item = self.conn.execute('SELECT value FROM kv WHERE key = ?', (key,)).fetchone()
        if item is None:
            return None
        v = json.loads(item[0])
        return v

    def __setitem__(self, key, value):
        key = str(key)
        value = json.dumps(value)
        self.conn.execute('REPLACE INTO kv (key, value) VALUES (?,?)', (key, value))

    def __delitem__(self, key):
        key = str(key)
        if key in self:
            self.conn.execute('DELETE FROM kv WHERE key = ?', (key,))

    def __iter__(self):
        return self.iterkeys()

    def read_with_ex(self, key, ex):
        res = self.__getitem__(key)
        if res is None: return None
        if not (isinstance(res, dict) and "time" in res.keys()): return None
        dif = arrow.now() - arrow.get(res['time'])
        if dif.seconds >= ex:
            self.__delitem__(key)
            return None
        return res['v']

    def write_with_ex(self, k, v):
        self.__setitem__(k, {"v": v, "time": arrow.now().format()})
