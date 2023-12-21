# -*- coding: utf-8 -*-
import os,signal,sys,re
def kill(port):
    cmd="ss -lp | grep "+port
    out=os.popen(cmd).read()
    for line in out.splitlines():
        print (line)
        match = re.findall('pid=(\d+)', line)
        if len(match)>0:
            for pid_str in match:
                pid = int(pid_str)
                os.kill(pid, signal.SIGKILL)
                print ("kill success")
    return

if __name__ == '__main__':
    port=sys.argv[1]
    kill(port)
