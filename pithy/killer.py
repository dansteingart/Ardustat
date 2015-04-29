#! /usr/bin/python
import psutil
import sys
from commands import getoutput as go
for p in psutil.get_pid_list():
    i = psutil.Process(p)
    try:
        if i.cmdline[0].find("python") > -1:
            print i.cmdline
            print sys.argv[1]
            if i.cmdline[2].find(sys.argv[1]+".py") > -1:
                print p
                print go("kill "+str(p))
    except Exception as err:
        a = "foo"
