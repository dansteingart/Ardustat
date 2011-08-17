import numpy
import ardustat_library_simple as ard
import time
import atexit

#set parameters
cycles = 4
min_potential = -.5 #V
max_potential = .5 #V
rate = 5 #mV/s
read_delay = .2 #second
ardustat_id = 16
file_name = "two_coin_test"
ardustat_socket = 7777
debug = False

#Below here no touchy
#connect to to ardustat and setup resistance table
a = ard.ardustat()

a.connect(ardustat_socket)
a.debug = debug
a.load_resistance_table(ardustat_id)
a.ocv()
time.sleep(.1)
a.groundvalue = 2.5
a.moveground()
time.sleep(.2)
a.ocv()

#create arrays + a function for logging data
times = []
potential = []
current = []
time_start = time.time()
cycle = 0
file_name = file_name+"_"+str(int(time_start))+".dat"
def appender(reading):
	print reading['work_v_ref'],reading['current']
	tdiff = str(time.time()-time_start)
	out = tdiff+","+str(reading['work_v_ref'])+","+str(reading['current'])+","+str(cycle)+"\n"
	open(file_name,"a").write(out)
	


#Allows cell to settle and picks starting potential based on OCV
output = 0
print "cycles:",cycle
a.ocv()
for i in range(0,5):
	time.sleep(1)
	read = a.parsedread()
	appender(read)
	output = float(read['work_v_ref'])

min_potential = min_potential + output #V
max_potential = max_potential + output #V

while cycle < cycles:
	#Scan Up
	while output < max_potential:	
		step_time = time.time()
		output = output + .005
		a.potentiostat(output)
		while (time.time()-step_time) < (5/rate):
			time.sleep(read_delay)
			read = a.parsedread()
			appender(read)
	#Scan Down
	while output > min_potential:
		step_time = time.time()
		output = output - .005
		a.potentiostat(output)
		while (time.time()-step_time) < (5/rate):
			time.sleep(read_delay)
			read = a.parsedread()
			appender(read)
	#Tick the Cycle
	cycle = cycle +1 
		
#Set to OCV
a.ocv()
