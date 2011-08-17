from pylab import *
import numpy
import ardustat_library_simple as ard
import time
import subprocess
import os
import glob
import sys

#connecto to ardustat and setup resistance table
a = ard.ardustat()
a.trial_connect(7777)
a.debug = False
a.load_resistance_table(16)


#create arrays + a function for logging data
times = []
potential = []
current = []
time_start = time.time()

def blink():
	a.rawwrite(" ")
	time.sleep(.1)
	aaaaa = 3

def appender(reading):
	print reading['cell_ADC'],read['current']
	potential.append(reading['cell_ADC'])
	current.append(reading['current'])
	times.append(time.time()-time_start)


#Step through values
output = 0
blink()
print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)

while output < 2:
	output = output + .1
	blink()
	print a.potentiostat(output)
	for i in range(0,3):
		time.sleep(.1)
		read = a.parsedread()
		appender(read)

blink()
print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)
	
output = 0
while output < .001:
	output = output + .0001
	blink()
	a.galvanostat(output)
	for i in range(0,3):
		time.sleep(.1)
		read = a.parsedread()
		appender(read)

blink()
print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)


#Clost socket and kill socket server
a.s.close()
a.p.kill()
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

