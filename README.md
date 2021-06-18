# remote_run_everthing统一解决各种语言远程调试

jet家的什么python，java，clion的c/c++都带remote debug，但是第一要缴费版本，第二rust这种语言，缴费也没有。

一种方法是使用gdbserver，这个具体可以google

## 方法原理

使用python脚本，在远程环境调用cmd，把结果打印到目前的ide，调用的时候运行python脚本就可以，如果配合虚拟机共享文件夹使用，那么就不需要上传下载文件。可能有人会问，为什么下载文件，这个主要是为了ide代码智能补全。

## 以运行rust代码为例
pip install remote_run_everything

[remote_run_everythin github 地址](https://github.com/wangmarkqi/remote_run_everything.git)

```python
from remote_run_everything import Conf, Local, Remote
def test():
    c = Conf(
        host="192.168.177.130",
        user="root",
        pwd="a",
        remote_root="/mnt/myrust/ssl",
        local_root="D://myrust/ssl",
    )
    l = Local(c)
    
    # step1:代码文件同步：这个命令会把local_root下的子文件夹递归复制到remote_root对应的子文件夹,虚拟机共享文件夹不需要本步骤
    l.upload(c.local_root+"/src",exclude="node_modules")
    #or
    l.upload(c.local_root+"/src",exclude=["node_modules"])
    #or
    l.upload(c.local_root+"/src")

    # step2: 命令行：这个命令会在远程环境remot_root文件夹中执行cargo run，并把输出结果打印在屏幕。多个命令以列表形式传递
    # r.cmd(['cargo run'])
    
    # step3：代码智能补全文件下载： 这个命令会把remote_root的子文件夹复制到local_root对应子文件夹,虚拟机共享文件夹不需要本步骤，这一步的意义在于ide智能补全（编译代码在虚拟机，本地没有）。实际中，执行此步骤需要根据语言变更子文件夹,以rust为例，复制target即可
    
    l.download(c.remote_root+"/target")


test()

```

##  运维功能

此外，__scripts__文件夹下含有python运维管理脚本，运行就会把__scripts__下所有运维脚本上传到远程根目录，然后运行相应的cmd命令即可。目前的脚本主要是杀进程的，根据关键字杀进程，根据端口号杀进程，未来会不断拓展。详细参见__scripts__目录脚本写法.

```
c = Conf(
    host="192.168.177.130",
    user="root",
    pwd="a",
    remote_root="/mnt/myrust/ssl",
    local_root="D://myrust/ssl",
)
l = Local(c)
r = Remote(c)
#把__scripts__下所有运维脚本上传到远程根目录
l.upload_scripts()
```
- 杀进程
```
# 杀掉端口号8088的所有进程（gunicorn针对一个端口多个进程，全杀）
r.cmd(['cd __scripts__', 'python kill_ss.py 8088'])

# 杀掉包含关键词的所有进程（gunicorn多个进程，全杀）
r.cmd(['cd __scripts__','python kill_ps.py keyword1 keyword2'])
```

- 芒果db备份恢复
```
# 将mongodb数据库1,2下所有数据备份到远程根目录mongoback目录下，数据库名称是子目录名称
r.cmd(['source /home/anaconda3/bin/activate server',
      'python ./__scripts__/mongo_dump_restore.py dump mongodb://localhost:27017 mpy ruihe'
      ])

# 将备份文件拉回本地
l.download(c.remote_root+"/mongo_backup")

# 将mongodb数据库1,2下所有数据恢复
r.cmd(['source /home/anaconda3/bin/activate server','python ./__scripts__/mongo_dump_restore.py restore mongodb://localhost:27017 db1 db2'])

```

- gunicorn 重启server
```
start=['source /home/anaconda3/bin/activate server',"gunicorn riskMis:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8887 --daemon"]
r.cmd(start)
```
