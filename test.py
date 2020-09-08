from remote_run_everything import Conf, Local, Remote
def test():
    c = Conf(
        host="192.168.177.130",
        user="root",
        pwd="a",
        remote_root="/mnt/myrust/ssl",
        local_root="D://myrust/ssl",
    )
    r = Remote(c)
    l = Local(c)
    
    # step1:代码文件同步：这个命令会把local_root下的子文件夹递归复制到remote_root对应的子文件夹,虚拟机共享文件夹不需要本步骤
    l.upload(c.local_root+"/src")
    
    # step2: 命令行：这个命令会在远程环境remot_root文件夹中执行cargo run，并把输出结果打印在屏幕。多个命令以列表形式传递
    # r.cmd(['cargo run'])
    
    # step3：代码智能补全文件下载： 这个命令会把remote_root的子文件夹复制到local_root对应子文件夹,虚拟机共享文件夹不需要本步骤，这一步的意义在于ide智能补全（编译代码在虚拟机，本地没有）。实际中，执行此步骤需要根据语言变更子文件夹,以rust为例，复制target即可
    
    l.download(c.remote_root+"/target")


test()
