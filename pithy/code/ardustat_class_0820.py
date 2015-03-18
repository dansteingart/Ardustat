from pithy import *
 
import urllib2
import time
from time import sleep
import pickle

class Communication():
    def __init__(self,base):
        self.base = base
        self.bwrite = self.base+"write/"
        self.bread = self.base+"read/"
        self.bchangefile = self.base+"setName/"
        self.bstartCSV = self.base+"startCSV/"
        self.bstopCSV = self.base+"stopCSV/"
        self.bunkill = self.base+"unkill/"
        self.debug = False

    def changefile(self,file_name):
        foo = urllib2.urlopen(self.bchangefile+file_name)
        sleep(.05)
        return foo.read() # if nothing this shouldn't break
    def startCSV(self,file_name):
        urllib2.urlopen(self.bunkill)
        urllib2.urlopen(self.bchangefile+file_name)
        sleep(.05)
        foo = urllib2.urlopen(self.bstartCSV+file_name)
        sleep(.05)
        return foo.read()
    
    def stopCSV(self):
        foo = urllib2.urlopen(self.bstopCSV)
        
    def sread(self):
        foo = urllib2.urlopen(self.bread)
        buff = foo.read()
        out = buff[buff.rfind("GO"):buff.rfind("ST")+2]
        return out
      
    def swrite(self,stringer):
        foo = urllib2.urlopen(self.bwrite+stringer)
        sleep(.05)
        return foo.read()
      

    def parseline(self,reading,res_table):
        outdict = {}
        #print "reading: ",reading
        outdict['valid'] = True
        parts = reading.split(",")
        if parts[0] != "GO":
	        print "reading messed up"
	        return "reading error"
        outdict['outvolt']=int(parts[2])
        outdict['setout'] = int(parts[6])
        outdict['ref'] =float(parts[-2])
        outdict['dac1'] = self.refbasis(parts[4],outdict['ref'])
        outdict['adc'] = self.refbasis(parts[3],outdict['ref'])
        outdict['pot_step'] = parts[5]
        outdict['dac2'] = self.refbasis(parts[-4],outdict['ref'])
        outdict['ref_adc'] = self.refbasis(parts[-3],outdict['ref'])
        outdict['res'] = res_table[int(outdict['pot_step'])][0]
        outdict['current'] = (float(outdict['dac1'])-float(outdict['adc']))/outdict['res']
        outdict['adc-ref_adc'] = (float(outdict['adc'])-float(outdict['ref_adc']))
        if self.debug:
            print outdict
        return outdict

#hack
    def parseline_calibrate(self,reading):
        outdict = {}
        outdict['valid'] = True
        parts = reading.split(",")
        if parts[0] != "GO":
	        print "reading messed up"
	        return "reading error"
        outdict['ref'] =float(parts[-2])
        outdict['dac1'] = self.refbasis(parts[4],outdict['ref'])
        outdict['adc'] = self.refbasis(parts[3],outdict['ref'])
        outdict['pot_step'] = parts[5]
        outdict['other_DAC'] = self.refbasis(parts[-3],outdict['ref'])
        outdict['ref_electrode'] = self.refbasis(parts[-2],outdict['ref'])
        if self.debug:
            print outdict
        return outdict
 
    def load_resistance_table(self,ardustat_id):
        if (ardustat_id == 'test'):
            self.res_table = pickle.load(open(drop_pre + "actual_resistance_tables/res_table_full.p"))
            return self.res_table
            print "the resistance table should work now"
        else:
            try:
                self.res_table = pickle.load(open(drop_pre + "actual_resistance_tables/resistance_table_" + str(ardustat_id) + ".p"))
                return self.res_table
                print "returned res_table"
            except:
                print "first use 8001/ardustat_calibration to create a resistance table for this ardustat"
          
    def refbasis(self,reading,ref):
        return round((float(reading)/float(ref))*2.5,3)
          
    def ocv(self):
        self.swrite("-0000")
        
    def sleeper(self, time):
        self.ocv()
        sleep(time)
        
    def parsedread(self,res_table):
        read = self.parseline(self.sread(),res_table)
        while read == "reading error":
		    print read
		    read = self.parseline(self.sread(),res_table)
        return read
  
    def parsedread_calibrate(self):
        read = self.parseline_calibrate(self.sread())
        while read == "reading error":
		    print read
		    read = self.parseline_calibrate(self.sread())
        return read
  
    def get_r(self,known_res,DAC,ADC):
        return float(known_res)*((float(DAC)/float(ADC))-1)
          
    def potentiostat(self,potential):
        voltage = str(int(1023*(abs(potential)/5.0))).rjust(4,"0")
        if potential < 0:
            voltage = int(voltage) + 2000
        if voltage == 2000:
            voltage = '0000'
        if self.debug:
            print 'sending arduino: ',("p"+voltage)
        voltage = str(voltage)
        self.swrite("p"+voltage)
        return voltage
       
    def sleep(self,time):
        self.ocv()
        for i in range(0,time):
            time.sleep(1)
          
    def set_DAC2(self,potential):
        potential = str(int(1023*(potential/5.0))).rjust(4,"0")
        self.swrite("d"+potential)
          
    def galvanostat(self,current,res_table):
        if current > 1.0:
            current = current * 1000
        debug = True
        if current < 0:
            current = abs(current)
            sign = -1
        else: 
            sign = 1
            
        if current == 0:
            current = 0.001
        R_goal = 1/current
        R_real = 10000
        R_set = 0
        err = 1000
        for d in res_table:
            this_err = abs(res_table[d][0] - R_goal)
            if this_err < err:
                err = this_err
                R_set = d
                R_real = res_table[d][0]
        delta_V = abs(current*R_real)
        if debug:
            print "voltage diff ", delta_V
            print "R_set ", R_set
            print "R_real ", R_real
        potential = str(int(1023 * (delta_V / 5.0))).rjust(4, "0")
        if sign < 0:
            potential = str(int(potential)+2000)
        if debug:
            print "r_set setting ", R_set
            print "gstat setting ", potential
        self.swrite("r" + str(R_set).rjust(4,"0"))
        sleep(.1)
        self.swrite("g"+str(potential))
        return potential
        
#cycling stuff
#----------------------------------------------------------------------------#
#constant ramp of current until a certain voltage is achieved
    def gradual_cycle(self, cycler_dict_gradual_cycle, cycle, res_table):
        d = cycler_dict_gradual_cycle
        time_start = time.time()
        time_diff = 0
        capacity = 0
        read = self.parsedread(res_table)
        current = d['start_current']
        print "this is the gradual charger",read
        
        if d['capacity_limit'] != 'na':
            capacity_limit = d['capacity_limt']
        else:
            capacity_limit = 10000
            print "no capacity limit"
        if d['max_voltage_limit'] != 'na':
            voltage_limit = d['max_voltage_limit']
        else:
            voltage_limit = 5
            print "no voltage limit"
        if d['time_limit'] != 'na':
            time_limit = d['time_limit']
        else:
            time_limit = 360000 #thousand hours
            print "time limit 100 hours"
        voltage = voltage_limit - 1 #hack
        rate = d['rate']
        #TODO: check that this is right
        while (time_diff < time_limit and abs(voltage) < abs(voltage_limit)):
            print "attempt current: %r" %current
            step_time = time.time()
            self.galvanostat(current)
            #TODO: work out what is best increment
            current = current + 0.0005
            while ((time.time() - step_time) < (.5/rate)):
                pass
        return

    def hold_voltage_min(self,cycler_dict_hold_volt_min,cycle,res_table):
        d = cycler_dict_hold_volt_min
        time_start = time.time()
        time_diff = 0
        #self.set_DAC2(d['DAC2_value'])
        read = self.parsedread(res_table)
        capacity = 0
        current = read['current']
        if d['time_limit_at_min'] != 'na':
            time_limit = d['time_limit_at_min']
        else:
            time_limit = 360000 #hundred hours 
            print "time limit 100 hours"
        if d['current_limit_at_min_voltage'] != 'na':
            current_limit = d['current_limit_at_min_voltage']
        else:
            current_limit = 0
            print "no current limit"
        self.potentiostat(d["min_voltage_limit"])
        while (time_diff < time_limit and abs(current) > abs(current_limit)):
            sleep(d['read_delay'])
            read = self.parsedread(res_table)
            current = read['current']
            #error check
            voltage = read['adc-ref_adc']
            time_diff = time.time() - time_start
            if self.debug:
                print time_diff
        return
    
    def hold_voltage_max(self,cycler_dict_hold_volt_max,cycle,res_table):
        d = cycler_dict_hold_volt_max
        time_start = time.time()
        time_diff = 0
        #self.set_DAC2(d['DAC2_value'])
        read = self.parsedread(res_table)
        capacity = 0
        current = read['current']
        if d['time_limit_at_max'] != 'na':
            time_limit = d['time_limit_at_max']
        else:
            time_limit = 360000 #hundred hours
            print "time limit 100 hours"
        if d['current_limit_at_max_voltage'] != 'na':
            current_limit = d['current_limit_at_max_voltage']
        else:
            current_limit = 0
            print "no current limit"
        self.potentiostat(d["max_voltage_limit"])
        while (time_diff < time_limit and (abs(current) > abs(current_limit))):
            sleep(d['read_delay'])
            read = self.parsedread(res_table)
            current = read['current']
            #error check
            voltage = read['adc-ref_adc']
            time_diff = time.time() - time_start
            if self.debug:
                print time_diff
        return
    
#put in a negative capacity limit
    def constant_current_discharge(self,cycler_dict_cc_discharge,cycle,res_table):
        d = cycler_dict_cc_discharge
        time_start = time.time()
        time_diff = 0
        #self.set_DAC2(d['DAC2_value'])
        read = self.parsedread(res_table)
        capacity = 0
        #hack so that cycle won't hit targets unless the user specifies them
        if d['capacity_limit'] != 'na':
            capacity_limit = d['capacity_limit']
        else:
            capacity_limit = 10000
            print "no capacity limit"
        if d['min_voltage_limit'] != 'na':
            voltage_limit = d['min_voltage_limit']
        else:
            voltage_limit = -5
            print "no voltage limit"
        if d['time_limit'] != 'na':
            time_limit = d['time_limit']
        else:
            time_limit = 360000 #thousand hours
            print "time limit 100 hours"
        if d['discharge_current'] > 0:
            discharge_current = -1*d['discharge_current']
        else:
            discharge_current = d['discharge_current']
        voltage = voltage_limit + 1 #dumb little hack to make sure loop starts
        self.galvanostat(discharge_current,res_table)
        while (time_diff < time_limit and (voltage > voltage_limit) and (capacity < capacity_limit)):
                sleep(d['read_delay'])
                read = self.parsedread(res_table)
                voltage = read['adc-ref_adc']
                current = read['current']
                time_diff = time.time()-time_start
                print "time diff ",time_diff
                capacity = abs(current * time_diff)
        return

    def constant_current_charge(self,cycler_dict_cc_charge,cycle,res_table):
        d = cycler_dict_cc_charge
        time_start = time.time()
        time_diff = 0
        capacity = 0
        read = self.parsedread(res_table)
        print "this is the charger ",read
        #self.set_DAC2(d['DAC2_value'])
        if d['capacity_limit'] != 'na':
            capacity_limit = d['capacity_limit']
        else:
            capacity_limit = 10000
            print "no capacity limit"
        if d['max_voltage_limit'] != 'na':
            voltage_limit = d['max_voltage_limit']
        else:
            voltage_limit = 5
            print "no voltage limit"
        if d['time_limit'] != 'na':
            time_limit = d['time_limit']
        else:
            time_limit = 360000 #thousand hours
            print "time limit 100 hours"
        voltage = voltage_limit - 1          #dumb little hack to make sure loop starts
        self.galvanostat(d["charge_current"],res_table)
        while (time_diff < time_limit and (voltage < voltage_limit) and (capacity < capacity_limit)):
                sleep(d['read_delay'])
                read = self.parsedread(res_table)
                voltage = read['adc-ref_adc']
                current = read['current']
                time_diff = time.time()-time_start
                print "time_diff ", time_diff
                capacity = current * time_diff
        return
