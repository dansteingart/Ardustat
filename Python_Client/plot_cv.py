from pylab import *
import numpy
import ardustat_library_simple as ard
import time

data = open("outfile.dat").read()

data = data.split("\n")
times = []
potential = []
current = []
for d in data:
	try:
		parts = d.split(",")
		times.append(parts[0])
		potential.append(parts[1])
		current.append(parts[2])
	except Exception, err:
		print err
	

plot(potential,current)
show()