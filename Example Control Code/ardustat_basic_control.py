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


lin_pot = [99.0 for x in range(256)] #linspace(100,10000,255)

lin_pot = [float(x) for x in open("resistance").readlines()]

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
    bval = int(round(val/ref))
    if bval < 0: bval = abs(bval)+2000
    bval = "p"+str(bval).rjust(4,"0")
    write(bval)
    return bval

def setCur(pot,res):
    #bval = int(pot/5.0*1023)
    write("r"+str(res).rjust(4,"0"))
    bval = int(round(pot/ref))
    if bval < 0: bval = abs(bval)+2000
    bval = "g"+str(bval).rjust(4,"0")
    write(bval)
    return bval


def setOCV():
    write("-0000")

#some basic control code
write("r0026")  #set resistance to 26th value out of 255
write("d0512")  #set the ardustat to work at +/- 2.5 V
setPot(.1)
setOCV()

