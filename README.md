# remote_run_everthing 各类实用代码集合封装

## 安装
```shell
 pip install -U --index-url https://test.pypi.org/simple/ remote_run_everything
```

## 运维功能
```python
# 服务端代码
from remote_run_everything import cherrypy_in_daemon,ByHttpServer
cherrypy_in_daemon(ByHttpServer,8888,"/deploy")

# 上推代码
from remote_run_everything import ByHttp 
def test_up():
    host = "http://x.x.x.x:8888/deploy"
    local = "D://project/demand/shop"
    remote = "/data/mypy/shop"
    db = "D://wq/temp/shop.db"
    bh = ByHttp(host, local, remote, db)
    bh.up(['node_modules', ".pyc", ".idea"])

# 下拉代码
def test_down():
    host = "http://x.x.x.x:8888/deploy"
    local = "D://project/demand/shop"
    remote = "/data/mypy/shop"
    db = "D://wq/temp/shop.db"
    bh = ByHttp(host, local, remote, db)
    bh.down(['node_modules', ".pyc", ".idea"])
```

## 缓存功能
```python
from remote_run_everything import cache_by_1starg,cache_by_name,cache_by_rkey 
@cache_by_name("asdf", 1)
def test1():
    print("运行了函数!!!!!!!!!!!!!!!!")
    return {"a": "adaf"}
@cache_by_1starg("asdf", 1)
def test2(arg1):
    print("运行了函数!!!!!!!!!!!!!!!!")
    return {"a": "adaf"}
@cache_by_rkey(1)
def test2(rkey="xx"):
    print("运行了函数!!!!!!!!!!!!!!!!")
    return {"a": "adaf"}
```
## KV数据库
```python
from remote_run_everything import KvStore
kv = KvStore('test.db') 
print(len(kv))         
kv['hello1'] = 'you1'
del kv['hello1']
print(len(kv))        
print('hello1' in kv) 
kv['hello3'] = 'newvalue'
print(kv.keys())        
print(kv.values())     
print(kv.items())     
for k in kv:
    print(k, kv[k])
```
## Mongodb like 数据库
```python
from remote_run_everything import Nosql,NosqlPg,NosqlMysql
db = Nosql()
t = "test"
col = db['test']
dic = {"a": 2, "b": 456, 'c': "adf", "d": "2020-02-02"}
col.insert_one(dic)
dic = {"a": 56, "b": 456, 'c': "adf", "d": "2020-07-02"}
col.insert_one(dic)
q = {"a": 2,"b":{"$gt":1}}
print(col.find(q))
db.drop_db()
```
## 进程管理
```python
class ProcessManage:
    # nosql is instance of Nosql or Nosqlmysql or Nqsqlpg
    def __init__(self, nosql):
        self.db = nosql
        self.col = self.db['pid']

    # 只需要在程序中引入这个函数,启动后会把pid存入数据库,然后有了pid,结合psutil,什么都有了
    def save_pid(self, name, cmd):
        dic = {"name": name, "cmd": cmd, "pid": os.getpid()}
        print("save pid", dic)
        self.col.insert_one(dic)

```
