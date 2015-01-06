import pickle
from pithy import *
import json

#file name stuff
#--------------------------------------------------------------------------------
file_name="/home/dandavies/Data/pickler/test16"

if ".csv" not in file_name:
    file_name = file_name+".csv"
raw_data_file_name = file_name.replace(".csv","raw_basic_average.csv")
raw_data_file = open(raw_data_file_name, "w")
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
countto = 1
current_total = 0
voltage_total = 0
counter = 0




#parsing functions

def load_resistance_table(ardustat_id):
    res_table = pickle.load(open("/home/dandavies/Data/" + "actual_resistance_tables/resistance_table_" + str(ardustat_id) + ".p"))
    return res_table
    
def refbasis(reading,ref):
    return round((float(reading)/float(ref))*2.5,3)
    
time_list = []
voltage_list = []
current_list = []
try:
    ardustat_id = json_data["ardustat_id"]
except:
    ardustat_id = 1001
res_table = load_resistance_table(ardustat_id)
data = open(file_name).read()
lines = data.split("\n")
first_time = int(lines[2].split(',')[0][1:-1])
print len(lines)
print first_time
for i in range (2,(len(lines)-1)):
    line = lines[i].split(',')
    ts = int(line[0][1:-1])
    if ts < 2000:
        pass
    else: 
        #print line
        ref = int(line[-1][1:-1])
        #print ref
        adc = refbasis(int(line[2][1:-1]),ref)
        ref_adc = refbasis(int(line[-2][1:-1]),ref)
        dac = refbasis(int(line[3][1:-1]),ref)
        #print line[2],adc,line[3],dac
        potstep = int(line[4][1:-1])
        res = res_table[potstep][0]
        ts = int(line[0][1:-1])
        time = int(ts-first_time)
        voltage_raw = int(line[2][1:-1]) - int(line[-2][1:-1])
        current_raw = int(line[3][1:-1]) - int(line[2][1:-1])
        voltage = adc-ref_adc
        current = (dac-adc)/res
#-----------------------------------------------------------------#    
        current_total += current
        voltage_total += voltage
        counter += 1
        if counter >= countto:
            current_average = current_total/countto
            voltage_average = voltage_total/countto
            to_raw = str(line) + "," + str(voltage_raw) + "," + str(current_raw) + "," + str(voltage_average) + "," + str(current_average) + "\n"
            raw_data_file.write(to_raw)
            time_list.append(time) #timing isnt exact but fuck it
            voltage_list.append(voltage_average)
            current_list.append(current_average)
            counter = 0
            current_total = 0
            voltage_total = 0
    
raw_data_file.close()


plot (voltage_list,current_list)
#xlim(.65,.8)
xlabel("voltage (V)")
ylabel("current (A)")
showme()
clf()

plot (time_list, voltage_list)
xlabel("time")
ylabel("voltage (V)")
showme()
clf()

plot (time_list, current_list)
xlabel("time")
ylabel("current A")
showme()
clf()






