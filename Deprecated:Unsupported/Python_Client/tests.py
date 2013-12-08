import RealTime
from pylab import *
import numpy
import ardustat_library_simple as ard
import time
import subprocess
import math


#start a serial forwarder
#p = subprocess.Popen(("python tcp_serial_redirect.py /dev/tty.usbmodemfa131 57600").split())

                
times = [0]
potential = [0]
current = [0]
time_start = time.time()


class DataGen(object):
        """ A silly class that generates pseudo-random data for
                display in the plot.
        """
        def __init__(self,init=50):
                self.data = (0,0)
                
        def next(self):
                self._recalc_data()
                return self.data
            
        def _recalc_data(self):
                self.data = (potential[-1],current[-1]*1000)

        def erase(self):
                times = [0]
                potential = [0]
                current = [0]
                time_start = time.time()
                
def appender(reading):
        print reading['cell_ADC'],reading['current']
        potential.append(reading['cell_ADC'])
        current.append(reading['current'])
        times.append(time.time()-time_start)

        
def runGalvo(curr1=0.002, curr2=-0.002, vmax=1.6, vmin=0.9, cycles=4):
        #connecto to ardustat and setup resistance table
        #for i in range (0,3):
        a = ard.ardustat()
        a.connect(7777)
        a.debug = False
        #a.calibrate(15000,16)
        a.load_resistance_table(16)
        read = a.parsedread()
        print "Resistance table loaded"
        time.sleep(1)
        #create arrays + a function for logging data

                    
        """
        subplot(3,1,1)
        potLine, = plot(times,potential,'.')
        title("Potential vs. Time")
        ylabel("Potential (V)")

        subplot(3,1,2)
        curLine, = plot(times,current,'.')
        title("Current vs. Time")
        ylabel("Current (A)")
        subplot(3,1,3)
        resLine, = plot(times,numpy.array(potential)/numpy.array(current))
        title("Resistance vs. Time")
        ylabel("Resistance (Ohms)")
        xlabel("Time (s)")
        

        #ion()                           # interaction mode needs to be turned off
 
        x = arange(0,2*pi,0.01)         # we'll create an x-axis from 0 to 2 pi
        line, = plot(x,x)               # this is our initial plot, and does nothing
        line.axes.set_ylim(-3,3)        # set the range for our plot
         
        starttime = time.time()         # this is our start time
        t = 0                           # this is our relative start time

        """
        
        """
        #Step through values
        output = 0
        print a.ocv()
        print -1
        for i in range(0,10):
                time.sleep(.1)
                read = a.parsedread()
                appender(read)
                print i


        #output = 0
        #while output < 2:
        output = 1.24
                #output = output + .01
        print a.potentiostat(output)
        for i in range(0,300):
        #for i in range(0,100):
                time.sleep(.1)
                read = a.parsedread()
                appender(read)
                       
        if str(a.ocv()) == "None":
                print "None"
                #connecto to ardustat and setup resistance table
                a = ard.ardustat()
                a.connect(7777)
                a.debug = False
                #a.calibrate(15000,16)
                a.load_resistance_table(16)
                time.sleep(.1)
              
        print a.ocv()
        for i in range(0,10):
                time.sleep(.1)
                read = a.parsedread()
                print "Appending initial values!"
                appender(read)
                if not RealTime.TickTock(False):
                        return
        
          """
        
        #output = 0
        #while output < .001:
        #output = -curr # new line
        #print  curr
        #print  output
        numCycles = int (cycles)
        for i in range (0,numCycles): # new line
                #output = output + .00001
                #output = -output # new line
                #print output
                if not RealTime.ocv_on():
                        if (i%2) == 0:
                                a.galvanostat(curr1)
                        else:
                                a.galvanostat(curr2)
                #for i in range(0,3):
                if (i%2) == 0:
                        voltage = vmin
                        while voltage < vmax:#for i in range (0,100): # new line
                                if RealTime.paused():
                                        handle_paused()
                                if RealTime.ocv_on():
                                        handle_ocv(a,"galvo",curr1)
                                time.sleep(.01)
                                read = a.parsedread()
                                appender(read)
                                voltage = read['cell_ADC']
                                if not RealTime.TickTock(False):
                                        return
                                        
                else:
                        voltage = vmax
                        while voltage > vmin:
                                if RealTime.paused():
                                        handle_paused()
                                if RealTime.ocv_on():
                                        handle_ocv(a,"galvo",curr2)
                                time.sleep(.01)
                                read = a.parsedread()
                                appender(read)
                                voltage = read['cell_ADC']
                                if not RealTime.TickTock(False):
                                        return
                        

        
        """
        print a.ocv()
        for i in range(0,10):
                time.sleep(.1)
                read = a.parsedread()
                appender(read)
        """
        
        while True:
                if RealTime.ocv_on():
                        handle_ocv(a)
                elif not RealTime.TickTock(True):
                        return
        
        """
        #p.kill()

        #Make sure everything plots out realistically 
        subplot(3,1,1)
        potLine = plot(times,potential,'.')
        title("Potential vs. Time")
        ylabel("Potential (V)")

        subplot(3,1,2)
        plot(times,current,'.')
        title("Current vs. Time")
        ylabel("Current (A)")
        subplot(3,1,3)
        plot(times,numpy.array(potential)/numpy.array(current))
        title("Resistance vs. Time")
        ylabel("Resistance (Ohms)")
        xlabel("Time (s)")
        show()

        """
def runPot(vol=1.4, cur=.001, slope=.01):
        #connecto to ardustat and setup resistance table
        #for i in range (0,3):
        a = ard.ardustat()
        a.connect(7777)
        a.debug = False
        #a.calibrate(15000,16)
        a.load_resistance_table(16)
        time.sleep(1)

        #create arrays + a function for logging data

                    
        """
        subplot(3,1,1)
        potLine, = plot(times,potential,'.')
        title("Potential vs. Time")
        ylabel("Potential (V)")

        subplot(3,1,2)
        curLine, = plot(times,current,'.')
        title("Current vs. Time")
        ylabel("Current (A)")
        subplot(3,1,3)
        resLine, = plot(times,numpy.array(potential)/numpy.array(current))
        title("Resistance vs. Time")
        ylabel("Resistance (Ohms)")
        xlabel("Time (s)")
        

        #ion()                           # interaction mode needs to be turned off
 
        x = arange(0,2*pi,0.01)         # we'll create an x-axis from 0 to 2 pi
        line, = plot(x,x)               # this is our initial plot, and does nothing
        line.axes.set_ylim(-3,3)        # set the range for our plot
         
        starttime = time.time()         # this is our start time
        t = 0                           # this is our relative start time

        """
        """
        #Step through values
        output = 0
        print a.ocv()
        print -1
        for i in range(0,10):
                time.sleep(.1)
                read = a.parsedread()
                appender(read)
                print i


        #output = 0
        #while output < 2:
        output = 1.24
                #output = output + .01
        print a.potentiostat(output)
        for i in range(0,300):
        #for i in range(0,100):
                time.sleep(.1)
                read = a.parsedread()
                appender(read)
                       
        if str(a.ocv()) == "None":
                #connecto to ardustat and setup resistance table
                a = ard.ardustat()
                a.connect(7777)
                a.debug = False
                #a.calibrate(15000,16)
                a.load_resistance_table(16)
                
        a.ocv()
        for i in range(0,10):
                time.sleep(.1)
                read = a.parsedread()
                appender(read)

        

        
        read = a.parsedread()
        appender(read)
        voltage = volmeasured = read['cell_ADC']
        while volmeasured < vol:
                voltage += slope
                a.potentiostat(voltage)
                read = a.parsedread()
                appender(read)
                volmeasured = read['cell_ADC']
                if not RealTime.TickTock(False):
                        return
                time.sleep(.01)
        """
        if not RealTime.ocv_on():
                potentiostat(a,vol)
        read = a.parsedread()
        appender(read)
        currmeasured = read['current']
        #volmeasured = read['cell_ADC']
        #vol = vol - volmeasured
        while True:#while currmeasured > cur:
                if RealTime.paused():
                        handle_paused()
                if RealTime.ocv_on():
                        handle_ocv(a,"pot",vol)
                read = a.parsedread()
                appender(read)
                currmeasured = read['current']
                if not RealTime.TickTock(False):
                        return
                time.sleep(.01)

        while True:
                if RealTime.ocv_on():
                        handle_ocv(a)
                elif not RealTime.TickTock(True):
                        return

def handle_ocv(handle,string,value):
        handle.ocv()
        while RealTime.ocv_on():
                read = handle.parsedread()
                appender(read)
                if not RealTime.TickTock(False):
                        return
                time.sleep(.01)
        if string == "galvo":
                print "equal"
                handle.galvanostat(value)
        elif string == "pot":
                potentiostat(handle,value)

def potentiostat(handle,value):
        handle.potentiostat(value)
        """
        volset = value
        read = handle.parsedread()
        appender(read)
        volmeasured = read['cell_ADC']
        while math.fabs(volmeasured-value) > 0.01:
                volset += value - volmeasured
                handle.potentiostat(volset)
                time.sleep(.1)
                read = handle.parsedread()
                appender(read)
                volmeasured = read['cell_ADC']
        """

def handle_paused():
        while RealTime.paused():
                if not RealTime.TickTock(False):
                        return
                time.sleep(.1)
        
def my_split(s, seps):
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res

def runCustom(commandString):
                #connecto to ardustat and setup resistance table
        a = ard.ardustat()
        a.connect(7777)
        a.debug = False
        #a.calibrate(15000,16)
        a.load_resistance_table(16)

        #create arrays + a function for logging data
        

        """
        commandList = commandString.split("\n")
        parsedList = []
        for command in commandList:
                parsedList.append(my_split(command,[",", ":"]))
        for element in parsedList:
                if element[0] == "V":
                        #run potentiostat test with gradient based on element[1] until trigger hits
                else if element[0] == "C":
                        #run galvanostat test with gradient based on element[1] until trigger hits
        """
        
                    

