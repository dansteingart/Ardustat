from simpardlibnet import ardustat as ard
from time import sleep,time

filename = "raw_data_"+str(int(time()))+".dat"
def write_log(data):
	if(data['valid']):open(filename,"a").write(str(data['time'])+","+data['raw']+"\n")

def write_log_cv(cyc,data):
	if(data['valid']):open("cv_"+filename,"a").write(str(data['time'])+","+str(cyc)+","+data['raw']+"\n")


def calc_step_time(rate):
	return (5/float(rate))

	
a = ard()
a.connect(7777)

#parameters
scan_rate = 1 #mV/s
initial_potential = 0.3
end_potential = 2.5
cycles = 5
this_potential = initial_potential
step_size = 0.005

#record 30 seconds of OCV
a.ocv()
time_limit = time()+10
print "OCV Portion"
while time() < time_limit:
	sleep(.5)
	write_log(a.parse(a.rawread()))
	

#CV portion
print "CV Portion"
for cycle in range(1,cycles+1):
	print "Cycle:",str(cycle)
	while this_potential < end_potential:
		time_limit = time() + calc_step_time(scan_rate)
		this_potential += step_size
		a.potentiostat(this_potential)
		while time() < time_limit:
			sleep(.2)
			write_log_cv(cycle,a.parse(a.rawread()))
	while this_potential > initial_potential:
		time_limit = time() + calc_step_time(scan_rate)
		this_potential += -1*step_size
		a.potentiostat(this_potential)
		while time() < time_limit:
			sleep(.2)
			write_log_cv(cycle,a.parse(a.rawread()))
		
#OCV			
a.ocv()
time_limit = time()+10
print "OCV Portion"
while time() < time_limit:
	sleep(.5)
	write_log(a.parse(a.rawread()))
