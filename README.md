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
from remote_run_everything import ByHttp ,BySftp
def test_up():
    host = "http://x.x.x.x:8888/deploy"
    local = "D://project/demand/shop"
    remote = "/data/mypy/shop"
    db = "D://wq/temp/shop.db"
    bh = ByHttp(host, local, remote, db)
    bh.up(['node_modules', ".pyc", ".idea"])
def test_up2():
    host = "http://x.x.x.x:8888/deploy"
    local = "D://project/demand/shop"
    remote = "/data/mypy/shop"
    db = "D://wq/temp/shop.db"
    by=BySftp(host,22,'root','pwd',local,remote,db)
    by.up(['node_modules', ".pyc", ".idea", ".pdf", ".docx", ".pickle", ".png", ".jpg",".venv","target","dist","build"])

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
import os
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
##  缓存装饰器
```python
from remote_run_everything import cache_by_1starg,cache_by_name,cache_by_rkey,cache_by_nth_arg
@cache_by_name("asdf", 1)
def test_dec():
    print("运行了函数!!!!!!!!!!!!!!!!")
    return {"a": "adaf"}


```

## 关系型 数据库
```python
from remote_run_everything import Crud,CrudeDuck
# 详情参见类方法
```

##  双目测距
```python
from remote_run_everything.binocular.relative_pos import RelativePos,CamTool
import numpy as np
unit=0.006240084611316764
l=[[3838.36767578125, 50.56350326538086], [2636.24072265625, 88.38832092285156], [511.72705078125, 95.95327758789062], [2303.57666015625, 107.30072784423828], [2159.92626953125, 111.08320617675781], [2001.15478515625, 114.86569213867188], ]
r=[[3743.86083984375, 31.651092529296875], [2424.54541015625, 65.69342803955078], [231.98681640625, 69.47590637207031], [2076.76025390625, 84.6058349609375], [1921.76904296875, 88.38832092285156], [1759.21728515625, 92.1707992553711]]
l=np.array(l)
r=np.array(r)
path="./nik_insinc.txt"
dic = RelativePos(path,path,unit,unit).rel_one(l, r)
print (dic)
```
