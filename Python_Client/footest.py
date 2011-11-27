import ardustat_library_simple as ard

from time import sleep,time
a = ard.ardustat()
a.auto_connect(7777)

while True:
	a.blink()
	print a.parsedread()
	sleep(2)
