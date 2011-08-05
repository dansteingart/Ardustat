from pylab import *
import ardustatlibrary as ard
import time
the_socket = 7777

connresult = ard.connecttosocket(the_socket)


times = []
potential = []
current = []
time_start = time.time()
def appender(reading):
	potential.append(reading['cell_ADC'])
	current.append(reading['current'])
	times.append(time.time()-time_start)

print connresult

socketinstance = connresult["socket"]

print ard.ocv(the_socket)
for i in range(0,10):
	time.sleep(.1)
	read = ard.parse(ard.socketread(socketinstance)['reading'])
	print read
	appender(read)
	
print ard.potentiostat(2,the_socket)
for i in range(0,10):
	time.sleep(.1)
	read = ard.parse(ard.socketread(socketinstance)['reading'])
	print read
	appender(read)

print ard.potentiostat(1,the_socket)
for i in range(0,10):
	time.sleep(.1)
	read = ard.parse(ard.socketread(socketinstance)['reading'])
	print read
	appender(read)


subplot(2,1,1)
plot(times,potential)
subplot(2,1,2)
plot(times,current)
show()