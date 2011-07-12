from pylab import *
import numpy
from glob import glob
from simpardlibnet import ardustat as ard

asa = glob("cv_raw_data*")
a = ard()
data = open(asa[len(asa)-1]).readlines()

potential = []
current = []
cycle = 1
pot = []
cur = []
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
		pot = []
		cur = []
		cycle = this_cycle
		pot.append(b['cell_ADC'])
		cur.append(b['current'])
	else:
		pot.append(b['cell_ADC'])
		cur.append(b['current'])


potential.append(pot)
current.append(cur)


for i in range(0,len(potential)):
	plot(potential[i],numpy.array(current[i])*1000,'.-',label="Cycle "+str(i+1))

xlabel("Potential (V)")
ylabel("Current (mA/cm^2)")
legend(loc="best")
savefig("out_cv.png")
