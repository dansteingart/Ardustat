import ardustatlibrary as ard
import time
the_socket = 7777

connresult = ard.connecttosocket(the_socket)

print connresult

socketinstance = connresult["socket"]

for a in range(0,5):
	ard.blink(the_socket)
	time.sleep(.2)

print ard.calibrate(9999,7777,7)

for a in range(0,5):
	ard.blink(the_socket)
	time.sleep(.2)
