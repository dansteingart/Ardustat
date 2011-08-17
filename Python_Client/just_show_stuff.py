import numpy
import ardustat_library_simple as ard
import time
import atexit

ardustat_id = 16
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
def appender(reading):
	print reading['work_v_ref'],reading['current']
	tdiff = str(time.time()-time_start)
	out = tdiff+","+str(reading['work_v_ref'])+","+str(reading['current'])+","+str(cycle)+"\n"
	open(file_name,"a").write(out)
	


#Allows cell to settle and picks starting potential based on OCV
while True:
	time.sleep(1)
	read = a.parsedread()
	#appender(read)
	print read

