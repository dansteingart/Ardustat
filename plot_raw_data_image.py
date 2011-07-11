from pylab import *
import numpy
from glob import glob
from simpardlib import ardustat as ard

asa = glob("raw_data*")
a = ard()
data = open(asa[len(asa)-1]).readlines()

time = []
potential = []
current = []

time_start = float(data[0].split(",")[0])
for d in data:
	c = d.split(",")[1:len(d.split(","))]
	cee = ""
	for i in c:
		cee += i+","
	b = a.parseReading(cee.strip(","))
	time.append(float(d.split(",")[0])-time_start)
	potential.append(b['cell_ADC'])
	current.append(b['current'])


subplot(2,1,1)
plot(time,potential)
subplot(2,1,2)
plot(time,current)
savefig("out_file.png")
