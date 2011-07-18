from pylab import *
import numpy
from glob import glob
from simpardlibnet import ardustat as ard
import json

asa = glob("raw_data*")
a = ard()
data = open(asa[len(asa)-1]).readlines()

time = []
potential = []
current = []

for i in data:
	thedict = json.loads(i.replace("\n",""))
	time.append(thedict["time"])
	potential.append(thedict['cell_ADC'])
	current.append(thedict['current'])


subplot(2,1,1)
plot(time,potential)
subplot(2,1,2)
plot(time,current)
savefig("out_file.png")
