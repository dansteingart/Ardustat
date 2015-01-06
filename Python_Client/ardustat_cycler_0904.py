from pithy import *
from ardustat_class_0820 import Communication as Node
from time import sleep
import time
import numpy
import pickle
import json
print "cycler"

hostsite = 'http://localhost:8002/' #should use portal but internet not stable
file_name = "as_dd_cycles/mdbdb_new_galvstat_4"



n = Node(hostsite)
type_of_test = "cycing - galvanostatic"
ardustat_id = 25
notes = 'These are notes:read_timing = 200ms, firmware - dd_0911, mdbdcell dd3 and dd4 cell, wept lim = 100, galv lim = 1000'
cycles = 4
start_rest_time = 100
read_delay = 1
na = 'na'
DAC2_value = 2.5

def load_resistance_table(ardustat_id):
    res_table = pickle.load(open("/home/dandavies/Data/" + "actual_resistance_tables/resistance_table_" + str(ardustat_id) + ".p"))
    return res_table

if ".csv" in file_name:
    file_name = file_name.replace('.csv', '')
#change this when other people want to use it
setup_file = "/home/dandavies/Data/"+file_name+"_setup.txt"

res_table = load_resistance_table(ardustat_id)
sleep(1)
#___________________________________________________________________
#here is where you specify things


#specifications for constant current portions of cycle
cycler_dict_cc_charge = {"file_name":file_name, 
"res_table":res_table,
#"DAC2_value":DAC2_value, #recommended low
"charge_current":0.0036,
"max_voltage_limit":0.4,
"capacity_limit":na,
"time_limit":na,
"read_delay":read_delay}

cycler_dict_cc_discharge = {"file_name":file_name, 
"res_table":res_table,
#"DAC2_value":DAC2_value, #recommended to be high
"discharge_current":-0.0036,
"min_voltage_limit":-1.0,
"capacity_limit":na,
"time_limit":na,
"read_delay":read_delay}

#specifications for constant voltage portions of cycle
cycler_dict_hold_volt_max = {"file_name":file_name, 
"res_table":res_table,
"cycles":0,
#"DAC2_value":DAC2_value, #recommended to be low
"current_limit_at_max_voltage":na,
"max_voltage_limit":.4,
"time_limit_at_max":600,
"read_delay":read_delay}

cycler_dict_hold_volt_min = {"file_name":file_name, 
"res_table":res_table,
"cycles":0,
#"DAC2_value":DAC2_value, #recommended to be high
"current_limit_at_min_voltage":na,
"min_voltage_limit":0,
"time_limit_at_min":100,
"read_delay":read_delay}
#___________________________________________________________________#
#cycle control calls functions in 'ardustat_class'.
#you can call these in whatever order you want to. its a bit of a pain to change the settings on them for different cycles though - you have to modify the dictionary for different cycles


def cycle_control():
    print "starting control cycle"
    n.ocv()
    sleep(start_rest_time)
    cycle = 0
    sleep(.1) # i hope that this is enough
    while cycle < cycles:
        print 'cycle: ',cycle
        print "resting"
        n.sleeper(600)
        print "charging"
        n.constant_current_charge(cycler_dict_cc_charge,cycle)
        print "holding"
        n.hold_voltage_max(cycler_dict_hold_volt_max,cycle)
        print "resting"
        n.sleeper(600)
        print "discharging"
        n.constant_current_discharge(cycler_dict_cc_discharge,cycle)
        cycle += 1
    n.ocv()
    print "donezo"



"""
"""
cycler_dict_cc_charge = {"file_name":file_name, 
"res_table":res_table,
#"DAC2_value":DAC2_value, #recommended low
"charge_current":0.0036,
"max_voltage_limit":0.4,
"capacity_limit":na,
"time_limit":na,
"read_delay":read_delay}


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

cycler_dict_cc_charge_json = removekey(cycler_dict_cc_charge, "res_table")
cycler_dict_cc_discharge_json = removekey(cycler_dict_cc_discharge, "res_table")
cycler_dict_hold_volt_max_json = removekey(cycler_dict_hold_volt_max, "res_table")
cycler_dict_hold_volt_min_json = removekey(cycler_dict_hold_volt_min, "res_table")

#fix this so that it doesn't send whole resistance table :(
dictionary_of_things = {
    "cycler_dict_cc_charge" :cycler_dict_cc_charge_json,
    "cycler_dict_cc_discharge" : cycler_dict_cc_discharge_json,
    "cycler_dict_hold_volt_max" : cycler_dict_hold_volt_max_json,
    "cycler_dict_hold_volt_min" : cycler_dict_hold_volt_min_json,
    "type_of_test": type_of_test,
    "file_name" : file_name,
    "arudstat_id" :ardustat_id,
    "notes": notes,
    "cycles":cycles,
    "start_rest_time":start_rest_time,
    "read_delay":read_delay,
    "na":na,
    "DAC2_value":DAC2_value,
    }
    
with open(setup_file, 'w') as outfile:
    json.dump(dictionary_of_things, outfile)
    
sleep(.05)
n.set_DAC2(DAC2_value)
sleep(1)
n.ocv()
sleep(1)
print n.startCSV(file_name)
print n.sread()
sleep(.05)
cycle_control()
print n.stopCSV()


