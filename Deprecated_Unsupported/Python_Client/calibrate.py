from pylab import *
import numpy
import ardustat_library_simple as ard
import time
import subprocess
import os
import glob
import sys

##Guess a serial port
port = ""
if os.name == "posix":
	#try os x
	if len(glob.glob("/dev/tty.u*")) > 0:
		port = glob.glob("/dev/tty.u*")[0]
	elif len(glob.glob("/dev/ttyUSB*")) > 0:
		port = glob.glob("/dev/ttyUSB*")[0]
	else:
		print "can't see any ardustats.  PEACE."
		sys.exit()
	print port
	

#start a serial forwarder
p = subprocess.Popen(("python tcp_serial_redirect.py "+port+" 57600").split())
print "waiting"
time.sleep(5)
print "going"
a = ard.ardustat()
a.connect(7777)
foo = a.calibrate(9974,16)

for f in foo:
	print f,foo[f]
	
a.s.close()
p.kill()