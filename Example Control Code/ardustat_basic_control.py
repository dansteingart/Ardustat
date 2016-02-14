from urllib import urlopen as uo
from time import *
url = "http://localhost:8888" #replace with whatever your port is

def read():
    uo(url+"/write/s0000").read()
    sleep(.1)
    incoming = uo(url+"/read/").read()
    return incoming.split("GO,")[-1].split(",ST")[0]

def write(ss):
    uo(url+"/write/"+ss).read()
    #sleep(.1)

#lin_pot = [99.0 for x in range(256)] #

#If we have a resistance table great, otherwise, make a linear map from 100 to 10000 kohm
try: lin_pot = [float(x) for x in open("resistance").readlines()]
except:  lin_pot = linspace(100,10000,255)

def parse(reading):
    res = lin_pot
    p = reading.split(",")
    #print p
    out ={}
    out['ref'] = 2.5/float(p[-2])
    ref = out['ref']
    out['ADC'] = float(p[1])*ref
    out['DAC'] = float(p[2])*ref
    out['RES'] = float(p[3])
    out['REF'] = float(p[-3])*ref
    out['GND'] = float(p[-4])*ref
    out['RR'] = res[int(out['RES'])]
    return out
    
ref = parse(read())['ref']

def setPot(val):
    #set potential in volts
    bval = int(round(val/ref))
    if bval < 0: bval = abs(bval)+2000
    bval = "p"+str(bval).rjust(4,"0")
    write(bval)
    return bval

def setCur(current,fix_res=None):
    """Set current in amps"""
    #if variable pot
    if fix_res == None:
        #V = IR
        #target 100 mV difference (10 ticks)
        tV = .1
        R =  tV/abs(current)  #V/I
        maxdiff = 10000
        res = 0
        for i in range(len(x)):
            if abs(R-x[i]) < maxdiff: 
                maxdiff = abs(R-x[i])
                res = i
        outr = "r"+str(res).rjust(4,"0")
        write(outr)
        r = x[res]
    #If fixed resistor
    else: r = fix_res

    #now calculate real potential difference
    outv = r*current
    outv = int(round(outv/ref))
    if outv < 0: outv = abs(outv)+2000
    gset = "g"+str(outv).rjust(4,"0")
    delay(.1)
    write(gset)

def setOCV():
    write("-0000")

t0 = time()
fn = "datafile_%i.csv" % t0
header = 'time_s,potential_V,current_A\n'
open(fn,'w').write(header)

def writereading():
    p = parse(read())
    current = (out['ADC']-out['DAC'])/out['RR']
    potential = out['ADC']-out['REF']
    ts = time.time()-t0
    out = "%f,%f,%f\n"
    open(fn,'a').write(out)


#some basic control code
write("d0512")  #set the ardustat to work at +/- 2.5 V
setCur(.0001) #set to 100uA

#take readings for 100 seconds
while time.time() < (t0+100):
    sleep(1)
    writereading()    
setOCV()

