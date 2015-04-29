import numpy
import numbers
import scipy
from scipy import ndimage
from scipy import integrate
from scipy import special
import matplotlib
matplotlib.use('agg')
from pylab import *
from PIL import Image
from PIL import ImageOps
from glob import glob
import time
import os
import sys
from commands import getoutput as go
import inspect
import StringIO
import urllib, base64


#hack to make things worth from PIL
def showimg(im,tip=".png"):
    tim = str(int(time.time()))    
    #imname = imname.replace("/","-")
    image = 'images/pithy_img_'+str(int(time.time()*1000))+tip
    print '##_holder_##:',"/"+image
    im.save(image)

    
#Hack to get thigns to work from matplotlib
def showmeold(tip=".png",kind="static"):
    tim = str(int(time.time()))	
    rcParams['figure.dpi'] = 40
    #imname = imname.replace("/","-")
    image = 'images/pithy_img_'+str(int(time.time()*1000))+tip
    if kind == "static": print '##_holder_##:',"/"+image
    else: print '##_dynamic_##:',kind,':',tim,':',"/"+image
    savefig(image)


def showme(tip=".png",kind="static"):
    tim = str(int(time.time()))	
    rcParams['figure.dpi'] = 40
    #imname = imname.replace("/","-")
    image = 'images/pithy_img_'+str(int(time.time()*1000))+tip
    if kind == "static": print '<img src=/'+image+'>'
    else: print '##_dynamic_##:',kind,':',tim,':',"/"+image
    savefig(image)

def showme64(tip="png"):
    imgdata = StringIO.StringIO()
    savefig(imgdata, format=tip)
    imgdata.seek(0)  # rewind the data
    preload = 'data:image;base64,' 
    if tip == ".svg":
        preload = 'data:image/svg+xml,' 
    uri =  preload+ urllib.quote(base64.b64encode(imgdata.buf))
    stylekey = 'style="width:100%;"'
    print '<img %s src = "%s"/>' % (stylekey,uri)


#A smoothing function I use
def smooth(x,window_len=11,window='flat'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    
    y = list(y)
    #account for windowing shift 2012-08-02
    for j in range(0,int(window_len)):
        y.pop(0)

    
    return array(y)



#makes links to quick go between 
def navigator():
    me  = ""
    mess = sys.argv
    mess[0] = mess[0].split("/")[-1].replace(".py","")
    for m in mess:
        me += m+"/"
    base = "http://steingart.princeton.edu"
    code = ":8001/"
    view = ":8003/"
    cl = base+code+me
    vl = base+view+me
    print "<a href='%s'>view</a> <a href='%s'>code</a>" % (vl,cl)


#line # hack from http://code.activestate.com/recipes/145297-grabbing-the-current-line-number-easily/
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno
