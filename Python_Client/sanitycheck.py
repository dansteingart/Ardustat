from pylab import *
import ardustat_library_simple as ard
import time

a = ard.ardustat()
a.connect(7777)


times = []
potential = []
current = []
time_start = time.time()
def appender(reading):
	print reading['cell_ADC'],read['current']
	potential.append(reading['cell_ADC'])
	current.append(reading['current'])
	times.append(time.time()-time_start)



output = 0

print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)

while output < 1:
	output = output + .1
	print a.potentiostat(output)
	for i in range(0,5):
		time.sleep(.1)
		read = a.parsedread()
		appender(read)

print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)


subplot(2,1,1)
plot(times,potential)
subplot(2,1,2)
plot(times,current)
show()