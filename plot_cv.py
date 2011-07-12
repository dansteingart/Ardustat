from pylab import *
import numpy
from glob import glob
from simpardlibnet import ardustat as ard

asa = glob("cv_raw_data*")
print asa
a = ard()
data = open(asa[len(asa)-1]).readlines()

potential = []
current = []
potentiometer = []
dacsetting = []
cycle = 1
pot = []
cur = []
res = []
dac = []
time_start = float(data[0].split(",")[0])
for d in data:
	c = d.split(",")[2:len(d.split(","))]
	this_cycle = int(d.split(",")[1])
	cee = ""
	for i in c:
		cee += i+","
	b = a.parse(cee.strip(","))
	if cycle != this_cycle:
		potential.append(pot)
		current.append(cur)
		potentiometer.append(res)
		dacsetting.append(dac)
		pot = []
		cur = []
		res = []
		dac = []
		cycle = this_cycle
		pot.append(b['cell_ADC'])
		cur.append(b['current'])
		res.append(b['resistance'])
		dac.append(b['DAC0_ADC'])
	else:
		pot.append(b['cell_ADC'])
		cur.append(b['current'])
		res.append(b['resistance'])
		dac.append(b['DAC0_ADC'])


potential.append(pot)
current.append(cur)
potentiometer.append(res)
dacsetting.append(dac)

for i in range(0,len(potential)):
	plot(potential[i])#,numpy.array(current[i])*1000,'.',label="Cycle "+str(i+1))

xlabel("Potential (V)")
ylabel("Current (mA/cm^2)")
legend(loc="best")
savefig("out_cv_3.png")
