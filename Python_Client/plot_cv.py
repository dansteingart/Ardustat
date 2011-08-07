from pylab import *
import numpy
import ardustat_library_simple as ard
import time
import sys
from glob import glob
import os


def get_latest():
	data_files = glob("*.dat")
	high_time = 0
	recent_file = "foo"
	for d in data_files:
		if os.path.getmtime(d) > high_time:
			high_time = os.path.getmtime(d)
			recent_file = d
	return recent_file

try:
	file_name = sys.argv[1]
except Exception, err:
	file_name = get_latest()	
	print "defaulting to most recent file:", file_name
	
data = open(file_name).read()

data = data.split("\n")
times = []
potential = []
current = []
cycles = []
this_cycle = 0
for d in data:
	try:
		parts = d.split(",")
		times.append(parts[0])
		potential.append(parts[1])
		current.append(parts[2])
		cycle = int(parts[3])
		if cycle != this_cycle:
			this_cycle = cycle
			cycles.append({'times':times,'potential':potential,'current':current})
			times = []
			potential = []
			current = [] 
	except Exception, err:
		foo = err
cycles.append({'times':times,'potential':potential,'current':current})

counter = 1
for c in cycles:
	plot(c['potential'],c['current'],label='Cycle '+str(counter))
	legend(loc="best")
	ylabel("Current (A)")
	xlabel("Potential (V)")
	counter += 1
show()