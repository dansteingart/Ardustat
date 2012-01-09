import ardustat_library_simple as ard
from time import sleep
a = ard.ardustat()
a.connect()
a.debug = False
a.load_resistance_table(16)
print "got table"
#move ground up
a.groundvalue = 2.5
a.moveground()
a.ser.timeout = .1
a.ser.writeTimeout = .1

for i in range(0,10):
	print a.parsedread()
	sleep(1)