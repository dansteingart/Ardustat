import pickle
from pithy import *
import sys
import os

ardustat_id = ''
countto = 1
current_total = 0
voltage_total = 0
counter = 0

start_fresh_flag = False
finish_flag = False

cwd = os.getcwd()

res_dir = "../../"+ cwd.split('/')[-2]+"/"
base_dir = '../../'+cwd.split('/')[-2]+'/Data/'

#have a script that automagically copies 
def load_resistance_table(ardustat_id):
    res_table = pickle.load(open(res_dir + "resistance_tables/resistance_table_" + str(ardustat_id) + ".p"))
    return res_table
    
def refbasis(reading,ref):
    if ref == 0:
        ref = 0.01 #comment this out
    return round((float(reading)/float(ref))*2.5,3)
    
def finisher():
    to_clean = str(time_list) + '\n' + str(voltage_list) + '\n' + str(current_list) + '\n' + str(cycle_list) 
    clean_file = open(clean_file_name, "w")
    clean_file.write(to_clean)
    #put in cycle
    #print 'finisher called'
    #delete pickle files (set to '')
    pickle.dump('', open(pickle_file_name, 'wb'))
    #delete bigCSV (set to '')
    #open(file_name, 'w').write('')
    to_read_from = 1
    
        
s = 2
eol = -1
y = 'v'
x = 't'
if len(sys.argv) > 1:
    file_name = base_dir + sys.argv[1] + "/"
if len(sys.argv) > 2:
    file_name = file_name + sys.argv[2]
if len(sys.argv) >3:
    if long(sys.argv[3]) > 2:
        s = long(sys.argv[3])
if len(sys.argv) >4:
    end = long(sys.argv[4])
    if(end > 0):
        eol = end
if len(sys.argv) >5:
    x = sys.argv[5]
if len(sys.argv) >6:
    y = sys.argv[6]
if len(sys.argv) > 7:
    ardustat_id = int(sys.argv[7])
if len(sys.argv) > 8:
    countto = int(sys.argv[8])
if len(sys.argv) > 9:
    if sys.argv[9] == 'start':
        start_fresh_flag = True
    elif sys.argv[9] == 'end':
        finish_flag = True

#print sys.argv
try:
    if ".csv" not in file_name:
        file_name = file_name+".csv"
    clean_file_name = file_name.replace(".csv","_clean.csv")
    try:
        #pass
        #setup_file_name = file_name.replace(".csv","_setup.txt")
        #setup_file = open(setup_file_name)
        pickle_file_name = file_name.replace(".csv", "_pickle.p")
    except:
        pass
        #print 'pickle file could not be loaded'  
    
    if ( not start_fresh_flag):
        try:
            things = pickle.load(open(pickle_file_name))
            to_read_from = things['to_read_from']
            time_list = things['time_list']
            voltage_list = things['voltage_list']
            current_list = things['current_list']
            cycle_list = things['cycle_list']
        except Exception, e:
            #print 'pickle loading problem ', e
            to_read_from = 1
            time_list = []
            voltage_list = []
            current_list = []
            cycle_list = []
            
    else:
        to_read_from = 1
        time_list = []
        voltage_list = []
        current_list = []
        cycle_list = []
    
            
    
    #print 'to_read_from ', to_read_from
    
    
    
    
    if ardustat_id == '':
        ardustat_id = 1001
    res_table = load_resistance_table(ardustat_id)
    
    data = open(file_name).read()
    #print data
    lines = data.split("\n")
    
    #print len(lines) 
    first_time = int(lines[1].split(',')[0])
    if (eol < 0):
        eol = len(lines)-1
    #print len(lines) 
    try:
        if type(to_read_from) == int:
            check_exists = to_read_from
        else: to_read_from = 1
    except:
        to_read_from = 1
    
    #print to_read_from
    #print eol
    for i in range (to_read_from,eol):
        line = lines[i].split(',')
        ts = int(line[0])
        if ts < 2000:
            pass
        else: 
            #print 'some stuff being worked out '
            ref = int(line[-1][1:-1])
            adc = refbasis(int(line[2][1:-1]),ref)
            ref_adc = refbasis(int(line[-2][1:-1]),ref)
            dac = refbasis(int(line[3][1:-1]),ref)
            potstep = int(line[4][1:-1])
            res = res_table[potstep][0]
            ts = int(line[0])
            timer = int(ts-first_time)/1000.0
            cycle_number = int(line[5][1:-1])
            voltage_raw = int(line[2][1:-1]) - int(line[-2][1:-1])
            current_raw = int(line[3][1:-1]) - int(line[2][1:-1])
            voltage = adc-ref_adc

            
            #REMOVE: this is only in here for running when I have a fake resistance table. this ... resistance should never be 0.
            if res == 0:
                res = 100
            current = (dac-adc)/res 
            
            current_total += current
            voltage_total += voltage
            counter += 1
            #print 'counter ', counter
            #print 'countto ', countto
            if counter >= countto:
                #print 'stuff being appended'
                current_average = current_total/countto
                voltage_average = voltage_total/countto
                voltage_total = 0
                current_total = 0
                counter = 0
                time_list.append(timer)
                voltage_list.append(voltage_average)
                current_list.append(current_average)
                cycle_list.append(cycle_number)
    
    #update pickle file etc..
    to_pickle = {}
    to_read_from = int(len(lines)-1) 
    to_pickle['to_read_from'] = to_read_from
    to_pickle['time_list'] = time_list
    to_pickle['voltage_list'] = voltage_list
    to_pickle['current_list'] = current_list
    to_pickle['cycle_list'] = cycle_list
    
    pickle.dump(to_pickle, open(pickle_file_name, 'wb'))
    
    if (x == 'v'):
        xaxis = voltage_list
        xlegend = "voltage (V)"
    elif (x == 'c'):
        xaxis = current_list
        xlegend = "current (A)"
    else:
        xaxis = time_list
        xlegend = "time (s)"
    if (y == 'c'):
        yaxis = current_list
        ylegend = "current (A)"
    else:
        yaxis = voltage_list
        ylegend = "voltage (V)"
    plot(xaxis,yaxis,'.')
    dpi = 80
    xlabel(xlegend)
    ylabel(ylegend)
    tip = ".png"
    imagesource = 'images/pithy_img_'+str(int(time.time()*1000))+tip
    w = ""
    h = ""
    s = "style='%s%s'" %(w,h)
    savefig(imagesource,dpi=dpi)
    image = '<img '+s+' src=/'+imagesource+'>'
    print imagesource
    
    if finish_flag :
        finisher()
    #print image

    #save things to pickle files...
    #voltage_list
    #current_list

        
except Exception as e:
    print 'something is wrong'
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(e, exc_tb.tb_lineno)




    #print 'starting fresh'
    

        








