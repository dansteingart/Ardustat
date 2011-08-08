from pylab import *
import numpy
import ardustat_library_simple as ard
import time

#set parameters
read_delay = .5 #second
ardustat_id = 16
file_name = "AAA_Test"
ardustat_socket = 7777
debug = False
pulse_time = 600

#Below here no touchy
#connect to to ardustat and setup resistance table
a = ard.ardustat()
a.connect(ardustat_socket)
a.debug = debug
a.load_resistance_table(ardustat_id)

#create arrays + a function for logging data
times = []
potential = []
current = []
time_start = time.time()
cycle = 0
file_name = file_name+"_"+str(int(time_start))+".dat"
def appender(reading):
	print reading['cell_ADC'],read['current']
	tdiff = str(time.time()-time_start)
	out = tdiff+","+str(reading['cell_ADC'])+","+str(read['current'])+","+str(cycle)+"\n"
	open(file_name,"a").write(out)


#Step through values
output = 0
a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)


while True:
	start_pulse = time.time()
	a.galvanostat(-.01)
	while (time.time()- start_pulse) < pulse_time:
		time.sleep(read_delay)
		read = a.parsedread()
		appender(read)
	
	start_pulse = time.time()
	a.ocv()
	while (time.time()- start_pulse) < 60:
		time.sleep(read_delay)
		read = a.parsedread()
		appender(read)

	start_pulse = time.time()
	a.galvanostat(0.01)
	while (time.time()- start_pulse) < pulse_time:
		time.sleep(read_delay)
		read = a.parsedread()
		appender(read)
			
	start_pulse = time.time()
	a.ocv()
	while (time.time()- start_pulse) < 60:
		time.sleep(read_delay)
		read = a.parsedread()
		appender(read)
	


	


print a.ocv()
