# -*- coding: utf-8 -*-
import os,signal,sys

def contain_every_key(keyws,line):
    for k in keyws:
        if k not in line:
            return False
    # 自己不能在里面
    if sys.argv[0] in line:
        return False
    print ("line==",line)
    return True
def kill(keyws):
    k0=keyws[0]
    cmd="ps -aux | grep "+k0
    out=os.popen(cmd).read()
    for line in out.splitlines():
        if contain_every_key(keyws,line):
            pid = int(line.split()[1])
            os.kill(pid, signal.SIGKILL)
            print ("kill success")
    return

if __name__ == '__main__':
    keyws=sys.argv[1:]
    kill(keyws)
