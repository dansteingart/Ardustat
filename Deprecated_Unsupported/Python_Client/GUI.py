from Tkinter import *
from RealTime import showRealTime
from RealTime import loadPlot
from tests import runGalvo
from tests import runPot
from tests import runCustom
from string import *
import time, random
import thread
import Pmw
import numpy
import subprocess
import ardustat_library_simple as ard

root = Tk()
root.title('Imprint Battery Tester')
Pmw.initialise()

nb = Pmw.NoteBook(root)
p1 = nb.add('Galvanostat test')
p2 = nb.add('Potentiostat test')
p3 = nb.add('Custom test')
p4 = nb.add('Load result')
#p5 = nb.add('Open-circuit potential')

nb.pack(padx=5, pady=5, fill=BOTH, expand=1)

entryLabelCur1 = Label(p1)
entryLabelCur1["text"] = "Start Current(mA):"
entryLabelCur1.pack(anchor="w")

entryWidgetCur1 = Entry(p1)
entryWidgetCur1["width"] = 10
entryWidgetCur1.pack(anchor="w")
entryWidgetCur1.insert(0,"2")

entryLabelCur2 = Label(p1)
entryLabelCur2["text"] = "End Current(mA):"
entryLabelCur2.pack(anchor="w")

entryWidgetCur2 = Entry(p1)
entryWidgetCur2["width"] = 10
entryWidgetCur2.pack(anchor="w")
entryWidgetCur2.insert(0,"-2")

entryLabelVMax = Label(p1)
entryLabelVMax["text"] = "Vmax(V):"
entryLabelVMax.pack(anchor="w")

entryWidgetVMax = Entry(p1)
entryWidgetVMax["width"] = 10
entryWidgetVMax.pack(anchor="w")
entryWidgetVMax.insert(0,"1.4")

entryLabelVMin = Label(p1)
entryLabelVMin["text"] = "Vmin(V):"
entryLabelVMin.pack(anchor="w")


entryWidgetVMin = Entry(p1)
entryWidgetVMin["width"] = 10
entryWidgetVMin.pack(anchor="w")
entryWidgetVMin.insert(0,"0.9")

entryLabelCycle = Label(p1)
entryLabelCycle["text"] = "Cycles:"
entryLabelCycle.pack(anchor="w")

entryWidgetCycle = Entry(p1)
entryWidgetCycle["width"] = 10
entryWidgetCycle.pack(anchor="w")
entryWidgetCycle.insert(0,"4")

entryLabelPotV = Label(p2)
entryLabelPotV["text"] = "Voltage:"
entryLabelPotV.pack(anchor="w")

entryWidgetPotV = Entry(p2)
entryWidgetPotV["width"] = 10
entryWidgetPotV.pack(anchor="w")
entryWidgetPotV.insert(0,"1.4")

entryLabelPotC = Label(p2)
entryLabelPotC["text"] = "Threshold Current(mA):"
entryLabelPotC.pack(anchor="w")

entryWidgetPotC = Entry(p2)
entryWidgetPotC["width"] = 10
entryWidgetPotC.pack(anchor="w")
entryWidgetPotC.insert(0,"1")

entryLabelPotS = Label(p2)
entryLabelPotS["text"] = "Ramp up slope(Volts/sample):"
entryLabelPotS.pack(anchor="w")

entryWidgetPotS = Entry(p2)
entryWidgetPotS["width"] = 10
entryWidgetPotS.pack(anchor="w")
entryWidgetPotS.insert(0,"0.01")

textboxLabel = Label(p3)
textboxLabel["text"] = "Write Custom Test then Select Run"
textboxLabel.pack(anchor="w")

textbox = Text(p3)
textbox["width"] = 20
textbox.pack(anchor="w",side=LEFT)

#textboxVol = Text(p5)
#textboxVol["width"] = 10
#textboxVol.pack(anchor="w",side=LEFT)

def runGTest():
    thread.start_new_thread(showRealTime, ())
    thread.start_new_thread(runGalvo,(atof(entryWidgetCur1.get())/1000,atof(entryWidgetCur2.get())/1000,atof(entryWidgetVMax.get()),atof(entryWidgetVMin.get()),atof(entryWidgetCycle.get())))
    #print "Hello!"
#pady=40

def runPTest():
    thread.start_new_thread(showRealTime, ())
    thread.start_new_thread(runPot,(atof(entryWidgetPotV.get()),atof(entryWidgetPotC.get())/1000,atof(entryWidgetPotS.get())))

def runCTest():
    thread.start_new_thread(showRealTime, ())
    thread.start_new_thread(runCustom, (textbox.get(1.0,END),))

def loadResult():
    thread.start_new_thread(showRealTime, ())
    time.sleep(1)
    thread.start_new_thread(loadPlot, ())


Button(p1, text='Run!', fg='blue', command=runGTest).pack(anchor="w")
Button(p2, text='Run!', fg='blue', command=runPTest).pack(anchor="w")
Button(p3, text='Run!', fg='blue', command=runCTest).pack(anchor="w")
Button(p4, text='Load', fg='blue', command=loadResult).pack(anchor="w")
#Button(p5, text='Refresh', fg='blue', command=lookupPotential).pack(anchor="w")


#textbox.insert(END, "Data being logged")

"""
c = Canvas(p2, bg='gray30')

w = c.winfo_reqwidth()
h = c.winfo_reqheight()
c.create_oval(10,10,w-10,h-10,fill='DeepSkyBlue1')
c.create_text(w/2,h/2,text='This is text on a canvas', fill='white',
      font=('Verdana', 14, 'bold'))
c.pack(fill=BOTH, expand=1) 
"""

#subprocess.Popen(("python tcp_serial_redirect.py COM3 57600").split())

root.mainloop()
