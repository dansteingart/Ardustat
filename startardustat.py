import web
import sys
import ardustatlibrary
import json
import matplotlib.pyplot
import webdotpyparselib
import glob
import ConfigParser

#The port used for communication between the python functions and socketserver.py is always <portconstant variable> + (the id # of the ardustat). Ideally, the portconstant variable should be the same in both ardustatlibrary and startardustat and greater than 50000.
#We don't use templates because web.py's templating language conflicts with jquery
#We communicate with the HTML/Javascript page using JSON objects, which are like python dictionaries except in string form; conversion to/from json format is as simple as using json.dumps(<dictionary>)/json.loads(<dictionary>).

urls = ('/galvanostat',	'galvanostat',
	'/potentiostat',	'potentiostat',
	'/raiseground',		'raiseground',
	'/calibrate',		'calibrate',
	'/begindatalog',	'begindatalog',
	'/enddatalog',		'enddatalog',
	'/ask',				'ask',
	'/blink',			'blink',
	#Slightly nonstandard functions:
	'/shutdown',		'shutdown',
	'/startardustat',	'startardustat',
	'/rawcmd',			'rawcmd',
	'/cyclinginputparse','cyclinginputparse',
	'/killself',		'killself',
	#Functions dealing with CSV files:
	'/generateimage',	'generateimage',
	'/listcsvfiles',	'listcsvfiles',
	'/datatable',		'datatable',
	#Files:
	'/',				'index',
	'/jquery-tools-full.min.js','jqueryfile',
	'/favicon.ico',		'favicon')
	
app = web.application(urls, globals())

config = ConfigParser.ConfigParser()
config.read("ardustatrc.txt")

portconstant = int(config.get("values","portconstant"))
enabledebugging = bool(config.get("values","enabledebugging"))

#Note: Ideally, every class should have the following form:
#
#class example:
#	def POST(self):
#		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
#		if len(data["id"]) < 1:
#			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
#		data["id"] = int(data["id"])
#		try:
#			result = ardustatlibrary.example(data["input"],portconstant+int(data["id"]))
#		except:
#			if enabledebugging == True: raise
#			return json.dumps({"success":False,"message":"Example function failed unexpectedly."})
#		else:
#			if result["success"] == True:
#				return json.dumps({"success":True,"message":"Did example function:\n"+result["message"]})
#			else:
#				return json.dumps({"success":False,"message":"Example function failed with message:\n"+result["message"]})
#
#If classes are made this way, then all you need to do to change the program is change the code in ardustatlibrary. You can debug using the console by setting the enabledebugging variable to True; if this is set to False, web.py should just tell the user that it failed unexpectedly.
#
#Begin "standardized" functions

class galvanostat:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No id number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.galvanostat(float(data["input"]),portconstant+data["id"],data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Setting galvanostat failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Set galvanostat:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Setting galvanostat failed with message:\n"+result["message"]})

class potentiostat:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.potentiostat(float(data["input"]),portconstant+data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Setting potentiostat failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Set potentiostat: "+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Setting potentiostat failed with message:\n"+result["message"]})

class raiseground:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No id number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.raiseGround(float(data["input"]),portconstant+data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Raising ground failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Raised ground:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Raising ground failed with message:\n"+result["message"]})

class calibrate:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.calibrate(float(data["input"]),portconstant+data["id"],data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Starting calibration failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Started calibration:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Starting calibration failed with message:\n"+result["message"]})

class begindatalog:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.begindatalog(data["input"],portconstant+data["id"],data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Starting data log failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Started data log:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Starting data log failed with message:\n"+result["message"]})

class enddatalog:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.enddatalog(data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Ending data log failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Ended data log:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Ending data log failed with message:\n"+result["message"]})

class ask:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.ask(portconstant+data["id"],data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Getting data failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Got data:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Getting data failed with message:\n"+result["message"]})

class blink:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.blink(portconstant+data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Blinking LED failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Blinked LED:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Blinking LED failed with message:\n"+result["message"]})		
		
class shutdown: #Run shutdown() and then quit using sys.exit()
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.shutdown(data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Shutting down failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Shutting down:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Shutting down failed with message:\n"+result["message"]})		

#Begin "nonstandardized" functions

#"Slightly nonstandard"...

class startardustat:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		if data["input"] == "": #If the port to connect to is left blank, just autoconnect
			autoconnect = True
		else:
			autoconnect = False
		try:
			result = ardustatlibrary.connecttoardustat(data["input"],data["id"],autoconnect)
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Connecting to ardustat failed unexpectedly."})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Connected to ardustat:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Connecting to ardustat failed with message:\n"+result["message"]})
				
class rawcmd: #Sends a command directly over socket interface to the ardustat. No sanity checking. Fix this later
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			connsocket = ardustatlibrary.connecttosocket(portconstant+data["id"])
			result = ardustatlibrary.socketwrite(connsocket["socket"],data["input"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Sending raw command failed unexpectedly"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Sent command:\n"+data["input"]+"."})
			else:
				return json.dumps({"success":False,"message":"Sending command failed with message:\n"+result["message"]})

class cyclinginputparse:
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		try:
			result = ardustatlibrary.cyclinginputparse(data["input"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Parsing input failed unexpectedly."})
		else:
			return json.dumps({"success":True,"message":"Parsing input:\n"+result})

class killself: #Run shutdown() and then quit using sys.exit()
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		if len(data["id"]) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		data["id"] = int(data["id"])
		try:
			result = ardustatlibrary.shutdown(data["id"])
		except:
			if enabledebugging == True: raise
			return json.dumps({"success":False,"message":"Shutting down failed unexpectedly. (If you are on a unix system, open a terminal and type \"killall "+pycommand+"\". If you are on Windows, press ctrl-alt-del to open up task manager, go to the \"processes\" tab, and kill all the processes that are named \"python.exe\"."})
		else:
			sys.exit()

#Functions that deal with csv files...

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
		cell_ADCminusreference_electrode = []
		for row in csvfile:
			try:
				float(row[0])
				float(row[1])
				float(row[2])
				float(row[3])
				float(row[6])
				float(row[9])
				float(row[13])
			except:
				pass
			else:
				timelist.append(float(row[0]))
				DAC0_setting.append(float(row[1]))
				DAC0_ADC.append(float(row[2]))
				cell_ADC.append(float(row[3]))
				resistance.append(float(row[5]))
				GND.append(float(row[6]))
				try:
					current.append(float(row[7]))
				except:
					current.append(False)
				try:
					cell_resistance.append(float(row[8]))
				except:
					cell_resistance.append(False)
				reference_electrode.append(float(row[9]))
				cell_ADCminusreference_electrode.append(float(row[13]))
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
			ylabel = "Reference Electrode (V)"
		elif data["xaxis"] == "cell_ADC-reference_electrode":
			data["xaxis"] = cell_ADCminusreference_electrode
			ylabel = "Cell Voltage Measurement - Reference Electrode (V)"
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
			ylabel = "Reference Electrode (V)"
		elif data["yaxis"] == "cell_ADC-reference_electrode":
			data["yaxis"] = cell_ADCminusreference_electrode
			ylabel = "Cell Voltage Measurement - Reference Electrode (V)"
		else:
			data["yaxis"] = [0]
			ylabel = "Unexpected error!"
		matplotlib.pyplot.clf()
		if data["xpoints"] != False:
			data["xaxis"] = data["xaxis"][(data["xpoints"] * -1):] #The last (data["xpoints"]) number of points
		if data["ypoints"] != False:
			data["yaxis"] = data["yaxis"][(data["ypoints"] * -1):] #Ditto
		matplotlib.pyplot.plot(data["xaxis"],data["yaxis"],data["plotstyle"])
		matplotlib.pyplot.xlabel(xlabel)
		matplotlib.pyplot.ylabel(ylabel)
		matplotlib.pyplot.savefig("image.png")
		matplotlib.pyplot.draw()
		return json.dumps({"success":True,"message":"Plotted "+xlabel+" on the x axis and "+ylabel+" on the y axis."})
	

class listcsvfiles:
	def POST(self):
		files = glob.glob("./*-parsed.csv")
		files.sort()
		filestr = ""
		for string in files:
			filestr = filestr+string[2:]+"\n"
		if filestr == "":
			return json.dumps({"success":False,"message":"No CSV files found!"})
		else:
			return json.dumps({"success":True,"message":filestr})
			
class datatable: #Generate a data table for the filename the user inputs. No HTTP parsing; chokes on non-alphanumeric characters besides '-'
	def POST(self):
		data = webdotpyparselib.webdataintodict(webdotpyparselib.webdataintoascii(web.data()))
		contents = open(data["input"], "r").read()	#VERY VERY VERY VERY INSECURE
		contents = str(contents)
		contents = "<table><tr><td>"+contents+"</td></tr></table>"
		contents = contents.replace("\n","</td></tr><tr><td>")
		contents = contents.replace(",","</td><td>")
		return contents

#Files

class index:
	def GET(self):
		return open("index.html","r").read()

class jqueryfile:
	def GET(self):
		return open("jquery-tools-full.min.js","r").read()

class favicon:
	def GET(self):
		web.header("Content-Type","image/x-icon")
		return open("favicon.ico", "rb").read()
				
if __name__ == "__main__":
	print "Starting up Ardustat web server. In your browser, go to http://localhost:8080/"
	print "Note: You must keep this terminal window open for the program to work."
	app.run()
