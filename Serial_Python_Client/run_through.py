import ardustat_library_simple as ard
from time import sleep
a = ard.ardustat()

a.connect()

while True:
	sleep(.5)
	a.blink()
	a.ser.flush()
	a.rawwrite("s0000")
	print a.rawread()
