from pithy import *
import pickle
from ardustat_class_0820 import Communication as Node
from time import sleep
import time
 
#the last four digits of host site is where the forwarder is forwarding to. Ardustat id the the number written on the ardustat
drop_pre = "https://drops.steingart.princeton.edu/"
hostsite = 'http://localhost:8010/'
n = Node(hostsite)
ardustat_id = 21
known_resistor = 10000 #ohms
print "this better print"
print n.sread()
sleep(1)

 
 
def calibrate(known_res,ardustat_id):
    n.swrite("R0000")
    n.swrite("r0001")
    ressers = []
    values = n.parsedread_calibrate()
    print ' here we go '
    for i in range(0,10):
        print i
        for y in range(0,256):
            n.swrite("r"+str(y).rjust(4,"0"))
            sleep(.5)
            values = n.parsedread_calibrate()
            built_in_res = n.get_r(known_res,values['dac1'],values['adc'])
            print values['pot_step'],built_in_res,values['dac1'],values['adc']
            open(drop_pre + 'actual_resistance_tables/resistance_table_'+str(ardustat_id)+'.txt','a').write(str(values['pot_step'])+',' + str(built_in_res) + '\n')
            ressers.append([int(values['pot_step']), built_in_res])
             
    #Make a Big List of Correlations
       
    big_dict = {}
    for r in ressers:
        try:
           big_dict[r[0]].append(r[1])
        except:
           big_dict[r[0]] = []
           big_dict[r[0]].append(r[1])
        
    print big_dict
                 
    #Find Values
    final_dict = {}
    print len(big_dict.keys())
    print big_dict.keys()
    for b in big_dict.keys():
        print b
        final_dict[b] = [sum(big_dict[b])/len(big_dict[b]),(max(big_dict[b])-min(big_dict[b]))/2.0]
    pickle.dump(final_dict,open(drop_pre + 'actual_resistance_tables/resistance_table_'+str(ardustat_id)+'.p',"wb"))
    return final_dict


calibrate(known_resistor, ardustat_id)
