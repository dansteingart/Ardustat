from simpardlibnet import ardustat as ard
from time import sleep,time
import json

filename = "raw_data_"+str(int(time()))+".dat"
def write_log(data):
	if(data['success']):
		print data
		open(filename,"a").write(json.dumps(data)+"\n")


def calc_step_time(rate):
	return (5/float(rate))

	
a = ard()
a.connect(7777)

a.ocv()
print "OCV Portion"
time_limit = time() + 10
while time() < time_limit:
	sleep(.5)
	write_log(a.parse(a.rawread()))
	

a.potentiostat(1)
time_limit = time() + 10
while time() < time_limit:
	sleep(.5)
	write_log(a.parse(a.rawread()))
	
a.potentiostat(1.5)
time_limit = time() + 3600
while time() < time_limit:
	sleep(.5)
	write_log(a.parse(a.rawread()))

		
#OCV			
a.ocv()
time_limit = time()+10
print "OCV Portion"
while time() < time_limit:
	sleep(.5)
	write_log(a.parse(a.rawread()))
