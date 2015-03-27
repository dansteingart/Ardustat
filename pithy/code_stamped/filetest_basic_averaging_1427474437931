#cool - gonna do a little experimenting here...
#deciding if this the best way to do things...

#the problem is with overwriting files
#it is the slowest and yuckiest step - so if can speed it up - probably should. 
#if need to overwrite a file - something should be sent to make sure that happens.
#if overwrite going to happen - io_emit to 

#actually wait - the overwriting happens in node - don't need to worry about it in python. All that needs to happen - the first time plotting is called after an experiment is sent - then you start from the start. this is very easy to do. Awesome - so I just get this working..

#what happens when test is stopped half way through... Analysis page can deal with that fine. Too lazy to make analysis page use only the clean csv... Maybe I should - but that's 2.0
first_time = True

import pickle
from pithy import *
import json

cwd = os.getcwd()

#base_file = '../../Ardustat_Private/'
base_file = '../../'+cwd.split('/')[-2]+'/'
#file name stuff
#--------------------------------------------------------------------------------
#automagically change  to the directory of where  node files are.
file_name= base_file +'/Data/' + 'greg/limno2'

if ".csv" not in file_name:
    file_name = file_name+".csv"
#raw_data_file_name = file_name.replace(".csv","raw_basic_average.csv")
#raw_data_file = open(raw_data_file_name, "w")
try:
    setup_file_name = file_name.replace(".csv","_setup.txt")
    #setup_file = open(setup_file_name)
    pickle_file_name = file_name.replace(".csv", "_pickle.p")
    #pickle_file = open(pickle_file_name)
except:
    print 'pickle didnt load :(' 

#try load pickle data
if not first_time:
    print 'not first time'
    try:
        print 'loading pickle data'
        things = pickle.load(open(pickle_file_name))
        #print things
        to_read_from = things['to_read_from']
        time_list = things['time_list']
        voltage_list = things['voltage_list']
        current_list = things['current_list']
        print 'to read from is ', to_read_from
        #print 'time list is ', time_list
    except Exception, e:
        print e
        to_read_from = 5
        time_list = []
        voltage_list = []
        current_list = []
        print 'to read from is ', to_read_from
        print 'time list is ', time_list
else:
    print 'first time'
    to_read_from = 2
    time_list = []
    voltage_list = []
    current_list = []


countto = 1
current_total = 0
voltage_total = 0
counter = 0
cyc_counter = 0
counter_block = 0




#parsing functions

#TODO: this needs to be included when worrying about directory stuff.
def load_resistance_table(ardustat_id):
    res_table = pickle.load(open(base_file + "resistance_tables/resistance_table_" + str(ardustat_id) + ".p"))
    return res_table
    
def refbasis(reading,ref):
    if float(ref) == 0:
       ref = 0.1
    return round((float(reading)/float(ref))*2.5,3)
    
try:
    ardustat_id = json_data["ardustat_id"]
except:
    ardustat_id = 1001
res_table = load_resistance_table(ardustat_id)
data = open(file_name).read()
lines = data.split("\n")
#print lines
first_time = int(lines[2].split(',')[0])
print lines[0:7]
#print int(lines[2].split(',')[3])
print len(lines)
print first_time
for i in range (to_read_from,int((len(lines)-1))):
    line = lines[i].split(',')
    ts = int(line[0])
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
        cycle_number = int(line[5][1:-1])
        res = res_table[potstep][0]
        ts = int(line[0])
        time = float(ts-first_time)/1000.0
        #print time
        
        
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
            to_raw = str(line) + "," + str(voltage_raw) + "," + str(current_raw) + "," + str(voltage_average) + "," + str(current_average) + str(cycle_number) + "\n"
            #raw_data_file.write(to_raw)
            time_list.append(time) #timing isnt exact but fuck it
            voltage_list.append(voltage_average)
            current_list.append(current_average)
            counter = 0
            current_total = 0
            voltage_total = 0
    
#update pickle file etc..
to_pickle = {}
to_read_from = int(len(lines)-1) 
to_pickle['to_read_from'] = to_read_from
to_pickle['time_list'] = time_list
to_pickle['voltage_list'] = voltage_list
to_pickle['current_list'] = current_list

#print 'time_list is now ', time_list
pickle.dump(to_pickle, open(pickle_file_name, 'wb'))



plot (voltage_list,current_list)
#xlim(.65,.8)
xlabel("voltage (V)")
ylabel("current (A)")
showme()
clf()

plot (time_list, voltage_list)
xlabel("time (s)")
ylabel("voltage (V)")
showme()
clf()

plot (time_list, current_list)
xlabel("time")
ylabel("current A")
showme()
clf()

#print cyc_counter





