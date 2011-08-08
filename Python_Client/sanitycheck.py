from pylab import *
import numpy
import ardustat_library_simple as ard
import time

#connecto to ardustat and setup resistance table
a = ard.ardustat()
a.connect(7777)
a.debug = False
a.load_resistance_table(16)

#create arrays + a function for logging data
times = []
potential = []
current = []
time_start = time.time()
def appender(reading):
	print reading['cell_ADC'],read['current']
	potential.append(reading['cell_ADC'])
	current.append(reading['current'])
	times.append(time.time()-time_start)


#Step through values
output = 0
print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)

while output < 2:
	output = output + .1
	print a.potentiostat(output)
	for i in range(0,3):
		time.sleep(.1)
		read = a.parsedread()
		appender(read)
print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)
	
output = 0
while output < .001:
	output = output + .0001
	a.galvanostat(output)
	for i in range(0,3):
		time.sleep(.1)
		read = a.parsedread()
		appender(read)

print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)



#Make sure everything plots out realistically 
subplot(3,1,1)
plot(times,potential,'.')
title("Potential vs. Time")
ylabel("Potential (V)")

subplot(3,1,2)
plot(times,current,'.')
title("Current vs. Time")
ylabel("Current (A)")
subplot(3,1,3)
plot(times,numpy.array(potential)/numpy.array(current))
title("Resistance vs. Time")
ylabel("Resistance (Ohms)")
xlabel("Time (s)")
show()