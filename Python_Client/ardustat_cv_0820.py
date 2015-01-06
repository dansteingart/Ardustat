from pithy import *
from ardustat_class_0813 import Communication as Node
from time import sleep
import time
import numpy

print "you are in cyclic voltammetry land now"
hostsite = 'http://steingart.princeton.edu/ardustat_01/'
n = Node(hostsite)
ardustat_id = 25
file_name = "dan/test5"

if ".csv" in file_name:
    file_name = file_name.replace('.csv', '')

#change this so if directory not there - create it, also if user adds a .csv then make sure that it doesn't matter
print n.sread()
res_table = n.load_resistance_table(ardustat_id)

def cyclic_voltammetry():
    start_rest_time = 1
    rate = 5 #mv/s
    cycles = 2
    min_potential = -.5
    max_potential = .5
    read_delay = 0
    DAC2_value = 2.5
    relative_to_ocv = False
    
    cycle = 0
    n.set_DAC2(DAC2_value)
    sleep(2)
    n.ocv()
    time.sleep(start_rest_time)
    print n.startCSV(file_name)
    time_start = time.time()
    
#--------------------------------#    
    read = n.parsedread(res_table) 
    ocv = read['adc-ref_adc']
    output = ocv
    print "adc-ref_adc",output
    print "dac2: %r" %read['dac2']
    if relative_to_ocv:
        min_potential = min_potential + output #V
        max_potential = max_potential + output #V
    print "max_potential ", max_potential
    print "min_potential ", min_potential
    
    while cycle < cycles:
        output = discharge(output, rate, min_potential)
        output = charge(output, rate, max_potential)
        cycle += 1
    output = discharge(output, rate, ocv)
    n.ocv()
   	        
def charge(output, rate, high_v):
    while output < high_v:
        print "attempt potential: %r" %output
        step_time = time.time()
        voltage = n.potentiostat(output)
        output = output + .005
        while ((time.time()-step_time) < (5/rate)):
            pass
    output = high_v
    return output

def discharge(output, rate, low_v):
    while output > low_v:
        print "attempt potential: %r" %output
        step_time = time.time()
        voltage = n.potentiostat(output)
        output = output - .005
        while (time.time()-step_time) < (5/(rate)):
            pass
    output = low_v
    return output
   	
print n.changefile(file_name)
sleep(.05)
n.swrite('-0000')
sleep(.05)
sleep(1)

cyclic_voltammetry()
print n.stopCSV()
