import web
import time
import os
import sys
import subprocess, signal
import ardustatlibrary
import socket
import json
import pickle
import matplotlib.pyplot
import webdotpyparselib

#The port used for communication between the python functions and socketserver.py is always 50000 + (the id # of the ardustat)
#We don't use templates because web.py's templating language conflicts with jquery
#We communicate with the HTML/Javascript page using JSON objects, which are like python dictionaries; conversion is as simple as using json.dumps(<dictionary>)

urls = ('/',			'index',
	'/startardustat',	'startardustat',
	'/galvanostat',		'galvanostat',
	'/potentiostat',	'potentiostat',
	'/calibrate',		'calibrate',
	'/rawcmd',			'rawcmd',
	'/begindatalog',	'begindatalog',
	'/enddatalog',		'enddatalog',
	'/datatable',		'datatable',
	'/generateimage',	'generateimage',
	'/ask',				'ask',
	'/blink',			'blink',
	'/raiseground',		'raiseground',
	'/makenewimage',	'makenewimage',
	'/listcsvfiles',	'listcsvfiles',
	'/cyclinginputparse','cyclinginputparse',
	'/killself',		'killself',
	'/shutdown',		'shutdown',
	'/favicon.ico',		'favicon',
	'/jquery-tools-full.min.js','jqueryfile')


app = web.application(urls, globals())

class index:
	def GET(self):
		return open("index.html","r").read()
		
class startardustat: #Open serialforwarder.py as a subprocess so we can use it communicate with the ardustat over sockets. Save a dictionary containing its process ID and the ardustat ID # in a pickle so we can find and kill it later.
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		if data["input"] == "": #If input is left blank, use the guessUSB function to autoconnect to the first ardustat it finds
			result = ardustatlibrary.guessUSB()
			if result["success"] == True:
				port = result["port"]
			else:
				print result
				return json.dumps({"success":False,"message":"Couldn't find serial port to autoconnect to. guessUSB() returned:"+result["message"]})
		else:
			port = data["input"]
		result = ardustatlibrary.connecttoardustat(port,data["id"])
		return json.dumps(result)
			
class galvanostat:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No id number was passed to this function."})
		try:
			result = ardustatlibrary.galvanostat(float(data["input"]),50000+int(data["id"]),int(data["id"]))
		except:
			return json.dumps({"success":False,"message":"Unexpected error setting galvanostat"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Set galvanostat"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Setting galvanostat failed: "+result["message"]})

class potentiostat:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		try:
			result = ardustatlibrary.potentiostat(float(data["input"]),50000+int(data["id"]))
		except:
			return json.dumps({"success":False,"message":"Unexpected error setting potentiostat"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Set potentiostat: "+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Setting potentiostat failed: "+result["message"]})

class raiseground:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No id number was passed to this function."})
		try:
			result = ardustatlibrary.raiseGround(float(data["input"]),50000+int(data["id"]))
		except:
			return json.dumps({"success":False,"message":"Unexpected error raising ground"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Raised ground: "+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Raising ground failed:\n"+result["message"]})

class calibrate:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.calibrate(float(data["input"]),50000+data["id"],data["id"])
		except:
			return json.dumps({"success":False,"message":"Unexpected error starting calibration"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Started calibration:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Starting calibration failed:\n"+result["message"]})

class rawcmd: #Sends a command directly over socket interface to the ardustat. No sanity checking. Fix this later
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			connsocket = ardustatlibrary.connecttosocket(50000+data["id"])
			result = ardustatlibrary.socketwrite(connsocket["socket"],data["input"])
		except:
			raise
			return json.dumps({"success":False,"message":"Unexpected error sending raw command"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Sent command "+data["input"]+"."})
			else:
				return json.dumps({"success":False,"message":"Error sending command:\n"+result["message"]})

class begindatalog:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		result = ardustatlibrary.begindatalog(data["input"],50000+data["id"],data["id"])
		return json.dumps(result)
				
class enddatalog:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		result = ardustatlibrary.enddatalog(data["id"])
		return json.dumps(result)

class datatable: #Generate a data table for the filename the user inputs. No HTTP parsing; chokes on non-alphanumeric characters besides '-'
	def POST(self):
		filename = web.data()[6:]
		contents = open(filename, "r").read()	#VERY VERY VERY VERY INSECURE
		contents = str(contents)
		contents = "<table border=1><tr><td>"+contents+"</td></tr></table></p>"
		contents = contents.replace("\n","</td></tr><tr><td>")
		contents = contents.replace(",","</td><td>")
		return "<p>"+contents+"</p>"

class generateimage: #Generate a graph for input in the parsed data csv file
	def GET(self): #If it's a "get", just return the image
		web.header("Content-Type", "images/png")
		return open("image.png","rb").read()
	
	def POST(self): #If it's a "post", generate the image and return a string saying what the function plotted
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["xpoints"]) > 0:
			data["xpoints"] = int(data["xpoints"])
		else:
			data["xpoints"] = False
		if len(data["ypoints"]) > 0:
			data["ypoints"] = int(data["ypoints"])
		else:
			data["ypoints"] = False
		f = open(data["filename"], "r") #ALSO VERY INSECURE
		csvfile = f.read()
		f.close()
		csvfile = csvfile.split("\n")
		for i in range(len(csvfile)):
			csvfile[i] = csvfile[i].split(",")
		timelist = []
		DAC0_setting = []
		DAC0_ADC = []
		cell_ADC = []
		resistance = []
		current = []
		cell_resistance = []
		GND = []
		reference_electrode = []
		for row in csvfile:
			try:
				for i in range(8):
					float(row[i])
				float(row[9])
			except:
				
				pass
			else:
				timelist.append(float(row[0]))
				DAC0_setting.append(float(row[1]))
				DAC0_ADC.append(float(row[2]))
				cell_ADC.append(float(row[3]))
				resistance.append(float(row[5]))
				GND.append(float(row[6]))
				current.append(float(row[7]))
				try:
					cell_resistance.append(float(row[8]))
				except:
					pass #Couldn't calculate cell resistance at that point, so move on
				reference_electrode.append(float(row[9]))
		#We need to do this so that only certain values can be passed to pylab.plot, otherwise there is arbitrary code execution
		if data["xaxis"] == "time":
			data["xaxis"] = timelist
			xlabel = "Unix Time"
		elif data["xaxis"] == "DAC0_setting":
			data["xaxis"] = DAC0_setting
			xlabel = "DAC Setting (V)"
		elif data["xaxis"] == "DAC0_ADC":
			data["xaxis"] = DAC0_ADC
			xlabel = "DAC Measurement (V)"
		elif data["xaxis"] == "cell_ADC":
			data["xaxis"] = cell_ADC
			xlabel = "Cell Voltage Measurement (V)"
		elif data["xaxis"] == "resistance":
			data["xaxis"] = resistance
			xlabel = "Resistor Setting (Ohm)"
		elif data["xaxis"] == "current":
			data["xaxis"] = current
			xlabel = "Current Calculation (A)"
		elif data["xaxis"] == "cell_resistance":
			data["xaxis"] = cell_resistance
			xlabel = "Cell Resistance Calculation (Ohm)"
		elif data["xaxis"] == "GND":
			data["xaxis"] = GND
			xlabel = "Ground Measurement (V)"
		elif data["xaxis"] == "reference_electrode":
			data["xaxis"] = reference_electrode
			xlabel = "Reference Electrode"
		else:
			data["xaxis"] = [0]
			xlabel = "Unexpected error!"
		if data["yaxis"] == "time":
			data["yaxis"] = timelist
			ylabel = "Unix Time"
		elif data["yaxis"] == "DAC0_setting":
			data["yaxis"] = DAC0_setting
			ylabel = "DAC Setting (V)"
		elif data["yaxis"] == "DAC0_ADC":
			data["yaxis"] = DAC0_ADC
			ylabel = "DAC Measurement (V)"
		elif data["yaxis"] == "cell_ADC":
			data["yaxis"] = cell_ADC
			ylabel = "Cell Voltage Measurement (V)"
		elif data["yaxis"] == "resistance":
			data["yaxis"] = resistance
			ylabel = "Resistor Setting (Ohm)"
		elif data["yaxis"] == "current":
			data["yaxis"] = current
			ylabel = "Current Calculation (A)"
		elif data["yaxis"] == "cell_resistance":
			data["yaxis"] = cell_resistance
			ylabel = "Cell Resistance Calculation (Ohm)"
		elif data["yaxis"] == "GND":
			data["yaxis"] = GND
			ylabel = "Ground Measurement (V)"
		elif data["yaxis"] == "reference_electrode":
			data["yaxis"] = reference_electrode
			ylabel = "Reference Electrode"
		else:
			data["yaxis"] = [0]
			ylabel = "Unexpected error!"
		matplotlib.pyplot.clf()
		if data["xpoints"] != False:
			xaxis = xaxis[(data["xpoints"] * -1):] #The last (data["xpoints"]) number of points
		if data["ypoints"] != False:
			yaxis = yaxis[(data["ypoints"] * -1):] #Ditto
		matplotlib.pyplot.plot(data["xaxis"],data["yaxis"],data["plotstyle"])
		matplotlib.pyplot.xlabel(xlabel)
		matplotlib.pyplot.ylabel(ylabel)
		matplotlib.pyplot.savefig("image.png")
		matplotlib.pyplot.draw()
		return json.dumps({"success":True,"message":"Plotted "+xlabel+" on the x axis and "+ylabel+" on the y axis."})
	
class ask:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		result = ardustatlibrary.ask(50000+data["id"],data["id"])
		return json.dumps({"success":True,"message":result["message"]})

class blink:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		result = ardustatlibrary.blink(50000+data["id"])
		return json.dumps({"success":True,"message":result["message"]})
		
class listcsvfiles:
	def POST(self):
		list = os.listdir(os.getcwd())
		filestr = ""
		for file in list:
			if file[len(file)-4:] == ".csv":
				filestr = filestr + str(file) + "\n"
		if filestr == "":
			return json.dumps({"success":False,"message":"No CSV files found!"})
		else:
			return json.dumps({"success":True,"message":filestr})
			
class cyclinginputparse:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		result = ardustatlibrary.cyclinginputparse(data["input"])
		return json.dumps({"success":True,"message":result})

class jqueryfile:
	def GET(self):
		return open("jquery-tools-full.min.js","r").read()

class favicon:
	def GET(self):
		web.header("Content-Type","image/x-icon")
		return open("favicon.ico", "rb").read()
		
class killself: #Run shutdown() and then quit using sys.exit()
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		ardustatlibrary.shutdown(data["id"])
		sys.exit()
		
class shutdown:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		result = ardustatlibrary.shutdown(data["id"])
		return json.dumps({"success":True,"message":result["message"]})
					
if __name__ == "__main__":
	print "Starting up Ardustat web server. In your browser, go to http://localhost:8080/"
	print "Note: You must keep this terminal window open for the program to work."
	app.run()
