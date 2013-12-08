"""
This demo demonstrates how to draw a dynamic mpl (matplotlib) 
plot in a wxPython application.

It allows "live" plotting as well as manual zooming to specific
regions.

Both X and Y axes allow "auto" or "manual" settings. For Y, auto
mode sets the scaling of the graph to see all the data points.
For X, auto mode makes the graph "follow" the data. Set it X min
to manual 0 to always see the whole data from the beginning.

Note: press Enter in the 'manual' text box to make a new value 
affect the plot.

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 31.07.2008
"""
import os
import pprint
import random
import sys
import wx
import pickle
from tests import DataGen
import time

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import matplotlib
#matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab


exited = False


class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value


class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'Demo: dynamic matplotlib graph'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
        self.datagen = DataGen()
        self.datav = [self.datagen.next()[0]]
        self.datac = [self.datagen.next()[1]]
        self.paused = False
        self.ocv = True
        exited = False
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()
        
        #self.redraw_timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        #self.redraw_timer.Start(100)

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
                
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
        
        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.ocv_button = wx.Button(self.panel, -1, "Start")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_BUTTON, self.on_ocv_button, self.ocv_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ocv_button, self.ocv_button)
        
        self.cb_grid = wx.CheckBox(self.panel, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)
        
        self.cb_xlab = wx.CheckBox(self.panel, -1, 
            "Show X labels",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(True)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.ocv_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 5.0), dpi=self.dpi)

        self.axesv = self.fig.add_subplot(211)
        self.axesc = self.fig.add_subplot(212)
        self.axesv.set_axis_bgcolor('black')
        self.axesv.set_title('Voltage (V)', size=12)

        self.axesc.set_axis_bgcolor('black')
        self.axesc.set_title('Current (mA)', size=12)
        
        pylab.setp(self.axesv.get_xticklabels(), fontsize=8)
        pylab.setp(self.axesv.get_yticklabels(), fontsize=8)

        pylab.setp(self.axesc.get_xticklabels(), fontsize=8)
        pylab.setp(self.axesc.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        #
        self.plot_datav = self.axesv.plot(
            self.datav, 
            linewidth=1,
            color=(1, 1, 0),
            )[0]
        
        self.plot_datac = self.axesc.plot(
            self.datac, 
            linewidth=1,
            color=(0, 0, 1),
            )[0]
        

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        if self.xmax_control.is_auto():
            xmaxv = xmaxc = len(self.datav) if len(self.datav) > 50 else 50
        else:
            xmaxv = float(self.xmax_control.manual_value())
            xmaxc = float(self.xmax_control.manual_value())
            
        if self.xmin_control.is_auto():            
            xminv = xminc = xmaxv - 50
        else:
            xminv = float(self.xmin_control.manual_value())
            xminc = float(self.xmin_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        #
        if self.ymin_control.is_auto():
            yminv = min(self.datav[int(xminv):int(xmaxv)])
            yminc = min(self.datac[int(xminc):int(xmaxc)])
        else:
            yminv = float(self.ymin_control.manual_value())
            yminc = float(self.ymin_control.manual_value())
        if self.ymax_control.is_auto():
            ymaxv = max(self.datav[int(xminv):int(xmaxv)])
            ymaxc = max(self.datac[int(xminc):int(xmaxc)])
        else:
            ymaxv = float(self.ymax_control.manual_value())
            ymaxc = float(self.ymax_control.manual_value())

        self.axesv.set_xbound(lower=xminv, upper=xmaxv)
        self.axesv.set_ybound(lower=yminv, upper=ymaxv)

        self.axesc.set_xbound(lower=xminc, upper=xmaxc)
        self.axesc.set_ybound(lower=yminc, upper=ymaxc)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        if self.cb_grid.IsChecked():
            self.axesv.grid(True, color='gray')
            self.axesc.grid(True, color='gray')
        else:
            self.axesv.grid(False)
            self.axesc.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp(self.axesv.get_xticklabels(), 
            visible=self.cb_xlab.IsChecked())

        pylab.setp(self.axesc.get_xticklabels(), 
            visible=self.cb_xlab.IsChecked())
        
        self.plot_datav.set_xdata(np.arange(len(self.datav)))
        self.plot_datav.set_ydata(np.array(self.datav))

        
        self.plot_datac.set_xdata(np.arange(len(self.datac)))
        self.plot_datac.set_ydata(np.array(self.datac))
        
        
        self.canvas.draw()
    
    def on_pause_button(self, event):
        self.paused = not self.paused

    def on_ocv_button(self, event):
        self.ocv = not self.ocv
    
    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)

    def on_update_ocv_button(self, event):
        label = "Start" if self.ocv else "OCV"
        self.ocv_button.SetLabel(label)
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        """
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)

        """
        #file_choices = "PICKLE (*.pickle)|*.pickle"
        dlg = wx.FileDialog(
            self,
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot",
            #wildcard=file_choices,
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath() + "current.pickle"
            outfile = open(path,"w")
            pickle.dump(self.datac, outfile)
            outfile.close()
            path = dlg.GetPath() + "voltage.pickle"
            outfile = open(path,"w")
            pickle.dump(self.datav, outfile)
            outfile.close()
            path = dlg.GetPath()
            outfile = open(path,"w")
            outfile.close()
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            outfile.close()
            path = dlg.GetPath()
            path = path + "log.txt"
            outfile = open(path, "w")
            i = 0
            for voltage, current in zip(self.datav, self.datac):
                outfile.write("Sample: " + str(i) + ", Voltage: " + str(voltage) + ", Current(mA): " + str(current) + "\n")
                i += 1
            outfile.close()

    def on_load_plot(self):
        self.paused = True
        file_choices = "PICKLE (*.pickle)|*.pickle"
        dlg = wx.FileDialog(
            self,
            message="Load plot...",
            defaultDir=os.getcwd(),
            #wildcard=file_choices,
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath() + "current.pickle"
            infile = open(path,"r")
            self.datac = pickle.load(infile)
            infile.close()
            path = dlg.GetPath() + "voltage.pickle"
            infile = open(path,"r")
            self.datav = pickle.load(infile)
            infile.close()
        while True:
            app.frame.on_redraw_timer(False)
            time.sleep(.1)
    
    def on_redraw_timer(self, pause):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        if not self.paused and not pause:
            self.datav.append(self.datagen.next()[0])
            self.datac.append(self.datagen.next()[1])
        
        self.draw_plot()
    
    def on_exit(self, event):
        exited = True
        self.datagen.erase()
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

app = wx.PySimpleApp()

def showRealTime():
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()

def ocv_on():
    return app.frame.ocv
        
def TickTock(pause):
    if exited:
        return False
    else:
        app.frame.on_redraw_timer(pause)
        return True

def loadPlot():
    app.frame.on_load_plot()

def paused():
    return app.frame.paused
