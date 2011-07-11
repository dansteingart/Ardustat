from simpardlibnet import ardustat as ard
from time import sleep,time

filename = "raw_data_"+str(int(time()))+".dat"
def write_log(data):
	if(data['valid']):open(filename,"a").write(str(data['time'])+","+data['raw']+"\n")

a = ard()
a.connect(7777)


a.ocv()
time_limit = time()+30
while time() < time_limit:
	sleep(.5)
	write_log(a.parseReading(a.rawread()))

a.potentiostat(0.5)
time_limit = time()+40
while time() < time_limit:
	sleep(1)
	write_log(a.parseReading(a.rawread()))

a.potentiostat(1.5)
time_limit = time()+3600*8
while time() < time_limit:
	sleep(.5)
	write_log(a.parseReading(a.rawread()))
	
a.ocv()
time_limit = time()+30
while time() < time_limit:
	sleep(.5)
	write_log(a.parseReading(a.rawread()))

