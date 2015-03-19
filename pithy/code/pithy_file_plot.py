import pickle
from pithy import *
import json
cwd = os.getcwd()
base_file = '../../'+cwd.split('/')[-2]+'/'


#select which file you want to view
file_name= base_file +'/Data'+'/pickler/test16'

if ".csv" not in file_name:
    file_name = file_name+".csv"
try:
    setup_file_name = file_name.replace(".csv","_setup.txt")
    setup_file = open(setup_file_name)
    json_data = json.load(setup_file)
except:
    pass

try:
    print json_data
except:
    pass

countto = 1 #amount of averaging you want to do
current_total = 0
voltage_total = 0
counter = 0
cyc_counter = 0
counter_block = 0


#parsing stuff
def load_resistance_table(ardustat_id):
    res_table = pickle.load(open(base_file + "resistance_tables/resistance_table_" + str(ardustat_id) + ".p"))
    return res_table
    
def refbasis(reading,ref):
    return round((float(reading)/float(ref))*2.5,3)
    
time_list = []
voltage_list = []
current_list = []
cycles = 0
try:
    ardustat_id = json_data["ardustat_id"]
except:
    ardustat_id = 1001
res_table = load_resistance_table(ardustat_id)
data = open(file_name).read()
lines = data.split("\n")
print lines[2]
first_time = int(lines[2].split(',')[0][1:-1])
print lines[2].split(',')
print lines[-1].split(',')
print len(lines)
print first_time
for i in range (2,int((len(lines)-1))):
    line = lines[i].split(',')
    ts = int(line[0][1:-1])
    if ts < 2000:
        pass
    else: 
        ref = int(line[-1][1:-1])
        adc = refbasis(int(line[2][1:-1]),ref)
        ref_adc = refbasis(int(line[-2][1:-1]),ref)
        dac = refbasis(int(line[3][1:-1]),ref)
        potstep = int(line[4][1:-1])
        cycle_number = int(line[5][1:-1])
        res = res_table[potstep][0]
        ts = int(line[0][1:-1])
        time = int(ts-first_time)/1000
        voltage_raw = int(line[2][1:-1]) - int(line[-2][1:-1])
        current_raw = int(line[3][1:-1]) - int(line[2][1:-1])
        voltage = adc-ref_adc
        current = (dac-adc)/float(res)
    
        current_total += current
        voltage_total += voltage
        counter += 1
        if counter >= countto:
            current_average = float(current_total)/countto * 1000.0
            voltage_average = float(voltage_total)/countto
            to_raw = str(line) + "," + str(voltage_raw) + "," + str(current_raw) + "," + str(voltage_average) + "," + str(current_average) + str(cycle_number) + "\n"
            time_list.append(time)#timing isn't exact. Sorry for not fixing yet.
            voltage_list.append(voltage_average)
            current_list.append(current_average)
            counter = 0
            current_total = 0
            voltage_total = 0
    
#raw_data_file.close()


plot (voltage_list,current_list)
xlabel("Voltage (V)")
ylabel("Current (mA)")
showme()
clf()

plot (time_list, voltage_list)
xlabel("Time (s)")
ylabel("Voltage (V)")
showme()
clf()

plot (time_list, current_list)
xlabel("Time")
ylabel("Current (mA)")
showme()
clf()





