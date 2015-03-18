#! /usr/bin/python
from pithy import *
import psutil
import sys

#this is just used as a hack to kill python processes that won't die.
listing = psutil.get_pid_list()
for p in listing:
    process = psutil.Process(p)
    if process.name() == 'python' or process.name() == 'Python':
        if "ardustat" in process.cmdline()[2]: #this is the important line where you 'select' what process you want to kill.
            print 'process ', process
            print process.cmdline()[2]
            #print process.cmdline[2]
            process.terminate()
            print "terminated ", process
        