from pylab import *
import numpy
import ardustat_library_simple as ard
import time

#connecto to ardustat and setup resistance table
a = ard.ardustat()
a.connect(7777)
a.debug = False
a.load_resistance_table(16)
a.ocv()
time.sleep(100)
a.groundvalue = 0
a.moveground()


#create arrays + a function for logging data
times = []
potential = []
current = []
time_start = time.time()
def appender(reading):
	print reading['cell_ADC'],read['current']
	tdiff = str(time.time()-time_start)
	out = tdiff+","+str(reading['cell_ADC'])+","+str(read['current'])+"\n"
	open("outfile.dat","a").write(out)
	


#Step through values
output = 0
print a.ocv()
for i in range(0,10):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)

while output < 1:
	output = output + .005
	print a.potentiostat(output)
	for i in range(0,5):
		time.sleep(1)
		read = a.parsedread()
		appender(read)
		
while output > -1 :
	output = output + .005
	print a.potentiostat(output)
	for i in range(0,5):
		time.sleep(1)
		read = a.parsedread()
		appender(read)

print a.ocv()
