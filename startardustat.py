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
	'/cyclinginput',	'cyclinginput',
	'/cyclinginputparse','cyclinginputparse',
	'/killself',		'killself',
	'/killeverything',	'killeverything',
	'/killcycling',		'killcycling',
	'/favicon.ico',		'favicon',
	'/jquery-tools-full.min.js','jqueryfile')


app = web.application(urls, globals())
#pycommand = "python" #Uncomment this line if you have a system that uses python 2 as its default
pycommand = "python2" #Uncomment this line if you have a system that uses python 3 as its default and can use python 2 with the "python2" command (i.e. Arch Linux)

class index:
	def GET(self):
		return open("index.html","r").read()
		
class startardustat: #Open serialforwarder.py as a subprocess so we can use it communicate with the ardustat over sockets. Save a dictionary containing its process ID and the ardustat ID # in a pickle so we can find and kill it later.
	def POST(self):
		data = web.data()
		input = data[6:data.find("&id=")]
		id = data[data.find("&id=")+4:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		id = int(id)
		while input.find("%") != -1: #Parse HTML encoding of input. Necessary for, for example, the '/'s in /dev/usbtty0
			char = int(input[input.find("%")+1:input.find("%")+3],16)
			char = chr(char) #  '%##' is the ascii character corresponding to the hex value ##
			input = input[:input.find("%")] + char + input[input.find("%")+3:] #Insert the character back into the input string
		if input == "": #If input is left blank, use the guessUSB function to autoconnect to the first ardustat it finds
			result = ardustatlibrary.guessUSB()
			if result["success"] == True:
				port = result["port"]
			else:
				print result
				return json.dumps({"success":False,"message":"Couldn't find serial port to autoconnect to. guessUSB() returned:"+result["message"]})
		else:
			port = input
		try:
			serialforwarderprocess = subprocess.Popen([pycommand,"tcp_serial_redirect.py","-p",port,"-P",str(50000+id),"-b","57600"])
		except:
			return json.dumps({"success":False,"message":"Unexpected error starting serialforwarder.py."})
		else:
			filename = "pidfile" + str(id) + ".pickle"
			pidfile = open(filename,"w") #Create an empty new file
			piddict = {}
			piddict["serialforwarder.py"] = serialforwarderprocess.pid
			pickle.dump(piddict, pidfile)
			pidfile.close()
			try:
				result["message"]
			except:
				return json.dumps({"success":True,"message":"Started to open ardustat on port "+port+"."})
			else:
				return json.dumps({"success":True,"message":"Started to open ardustat on port "+port+". guessUSB() returned:"+result["message"]})
			
class galvanostat:
	def POST(self):
		data = web.data()
		input = data[6:data.find("&id=")]
		id = data[data.find("&id=")+4:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		try:
			result = ardustatlibrary.galvanostat(float(input),50000+int(id),int(id))
		except:
			return json.dumps({"success":False,"message":"Unexpected error setting galvanostat"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Set galvanostat"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Setting galvanostat failed: "+result["message"]})

class potentiostat:
	def POST(self):
		data = web.data()
		input = data[6:data.find("&id=")]
		id = data[data.find("&id=")+4:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		try:
			result = ardustatlibrary.potentiostat(float(input),50000+int(id))
		except:
			return json.dumps({"success":False,"message":"Unexpected error setting potentiostat"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Set potentiostat: "+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Setting potentiostat failed: "+result["message"]})

class raiseground:
	def POST(self):
		data = web.data()
		input = data[6:data.find("&id=")]
		id = data[data.find("&id=")+4:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		try:
			result = ardustatlibrary.raiseGround(float(input),50000+int(id))
		except:
			return json.dumps({"success":False,"message":"Unexpected error raising ground"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Raised ground: "+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Raising ground failed:\n"+result["message"]})

class calibrate:
	def POST(self):
		data = web.data()
		input = data[6:data.find("&id=")]
		id = data[data.find("&id=")+4:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		id = int(id)
		try:
			result = ardustatlibrary.calibrate(float(input),50000+id,id)
		except:
			return json.dumps({"success":False,"message":"Unexpected error starting calibration"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Started calibration:\n"+result["message"]})
			else:
				return json.dumps({"success":False,"message":"Starting calibration failed:\n"+result["message"]})

class rawcmd: #Sends a command directly over socket interface to the ardustat. No sanity checking. Fix this later
	def POST(self):
		data = web.data()
		input = data[6:data.find("&id=")]
		id = data[data.find("&id=")+4:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		id = int(id)
		while input.find("%") != -1: #Parse HTML encoding of input. Necessary for, for example, the '/'s in /dev/usbtty0
			char = int(input[input.find("%")+1:input.find("%")+3],16)
			char = chr(char) #  '%##' is the ascii character corresponding to the hex value ##
			input = input[:input.find("%")] + char + input[input.find("%")+3:] #Insert the character back into the input string
		try:
			connsocket = ardustatlibrary.connecttosocket(50000+id)
			result = ardustatlibrary.socketwrite(connsocket["socket"],input)
		except:
			return json.dumps({"success":False,"message":"Unexpected error starting calibration"})
		else:
			if result["success"] == True:
				return json.dumps({"success":True,"message":"Sent command "+input+"."})
			else:
				return json.dumps({"success":False,"message":"Error sending command:\n"+result["message"]})

class begindatalog:
	def POST(self):
		data = web.data()
		input = data[6:data.find("&id=")]
		id = data[data.find("&id=")+4:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		id = int(id)
		result = ardustatlibrary.begindatalog(input,50000+id,id)
		return json.dumps({"success":True,"message":result["message"]})
				
class enddatalog:
	def POST(self):
		data = web.data()
		id = data[3:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		id = int(id)
		result = ardustatlibrary.enddatalog(id)
		return json.dumps({"success":True,"message":result["message"]})

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
	
	def POST(self): #If it's a "post", just return a string saying what the function plotted
		data = web.data()
		xaxis = data[6:data.find("&yaxis=")]
		yaxis = data[data.find("&yaxis=")+7:data.find("&xpoints=")]
		xpoints = data[data.find("&xpoints=")+9:data.find("&ypoints=")]
		if len(xpoints) > 0:
			xpoints = int(xpoints)
		else:
			xpoints = False
		ypoints = data[data.find("&ypoints=")+9:data.find("&plotstyle=")]
		if len(ypoints) > 0:
			ypoints = int(ypoints)
		else:
			ypoints = False
		plotstyle = data[data.find("&plotstyle=")+11:data.find("&filename=")]
		filename = data[data.find("&filename=")+10:]
		f = open(filename, "r") #ALSO VERY INSECURE
		csvfile = f.read()
		f.close()
		csvfile = csvfile.split("\n")
		for i in range(len(csvfile)):
			csvfile[i] = csvfile[i].split(",")
		if len(csvfile[0]) == 9:
			version = 6
		elif len(csvfile[0]) == 12:
			version = 7
		unixTime = []
		DACBArduino = []
		DACBReading = []
		cellVoltage = []
		DVRArduino = []
		current = []
		cellResistance = []
		if version == 7:
			GND = []
			referenceElectrode = []
		for row in csvfile:
			try:
				if version == 7:
					for i in range(9):
						float(row[i])
				elif version == 6:
					for i in range(7):
						float(row[i])
			except:
				pass
			else:
				unixTime.append(float(row[0]))
				DACBArduino.append(float(row[1]))
				DACBReading.append(float(row[2]))
				cellVoltage.append(float(row[3]))
				DVRArduino.append(float(row[4]))
				current.append(float(row[5]))
				cellResistance.append(float(row[6]))
				if version == 7:
					GND.append(float(row[7]))
					referenceElectrode.append(float(row[8]))
		#We need to do this so that only certain values can be passed to pylab.plot, otherwise there is arbitrary code execution
		if xaxis == "unixTime":
			xaxis = unixTime
			xlabel = "Unix Time"
		elif xaxis == "DACBArduino":
			xaxis = DACBArduino
			xlabel = "DAC Setting (V)"
		elif xaxis == "DACBReading":
			xaxis = DACBReading
			xlabel = "DAC Measurement (V)"
		elif xaxis == "cellVoltage":
			xaxis = cellVoltage
			xlabel = "Cell Voltage Measurement (V)"
		elif xaxis == "DVRArduino":
			xaxis = DVRArduino
			xlabel = "Resistor Setting (Ohm)"
		elif xaxis == "current":
			xaxis = current
			xlabel = "Current Calculation (A)"
		elif xaxis == "cellResistance":
			xaxis = cellResistance
			xlabel = "Cell Resistance Calculation (Ohm)"
		elif xaxis == "GND":
			xaxis = GND
			xlabel = "Ground Measurement (V)"
		elif xaxis == "referenceElectrode":
			xaxis = referenceElectrode
			xlabel = "Reference Electrode"
		else:
			xaxis = [0]
			xlabel = "Unexpected error!"
		if yaxis == "unixTime":
			yaxis = unixTime
			ylabel = "Unix Time"
		elif yaxis == "DACBArduino":
			yaxis = DACBArduino
			ylabel = "DAC Setting (V)"
		elif yaxis == "DACBReading":
			yaxis = DACBReading
			ylabel = "DAC Measurement (V)"
		elif yaxis == "cellVoltage":
			yaxis = cellVoltage
			ylabel = "Cell Voltage Measurement (V)"
		elif yaxis == "DVRArduino":
			yaxis = DVRArduino
			ylabel = "Resistor Setting (Ohm)"
		elif yaxis == "current":
			yaxis = current
			ylabel = "Current Calculation (A)"
		elif yaxis == "cellResistance":
			yaxis = cellResistance
			ylabel = "Cell Resistance Calculation (Ohm)"
		elif yaxis == "GND":
			yaxis = GND
			ylabel = "Ground Measurement (V)"
		elif yaxis == "referenceElectrode":
			yaxis = referenceElectrode
			ylabel = "Reference Electrode"
		else:
			yaxis = [0]
			ylabel = "Unexpected error!"
		#The next section only works on EPD!
		matplotlib.pyplot.clf()
		if xpoints != False:
			xaxis = xaxis[(xpoints * -1):] #The last (xpoints) number of points
		if ypoints != False:
			yaxis = yaxis[(ypoints * -1):] #Ditto
		matplotlib.pyplot.plot(xaxis,yaxis,plotstyle)
		matplotlib.pyplot.xlabel(xlabel)
		matplotlib.pyplot.ylabel(ylabel)
		matplotlib.pyplot.savefig("image.png")
		matplotlib.pyplot.draw()
		return json.dumps({"success":True,"message":"Plotted "+xlabel+" on the x axis and "+ylabel+" on the y axis."})
	
class ask:
	def POST(self):
		data = web.data()
		id = data[3:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			thesocket.connect(("localhost",50000+int(id)))
		except:
			return json.dumps({"success":False,"message":"Couldn't connect to serialforwarder.py"})
		thesocket.send("a")
		line = thesocket.recv(1023)
		thesocket.send("x") #shuts down connection
		thesocket.close()
		parsedline = ardustatlibrary.parse(line,int(id))
		return json.dumps(parsedline)

class blink:
	def POST(self):
		data = web.data()
		id = data[3:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		id = int(id)
		result = ardustatlibrary.blink(50000+id)
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

class cyclinginput:
	def POST(self):
		data = web.data()
		input = data[6:data.find("&repeat=")]
		repeat = data[data.find("&repeat=")+8:data.find("&id=")]
		repeat = int(repeat)
		id = data[data.find("&id=")+4:]
		id = int(id)
		while input.find("%") != -1:
			char = int(input[input.find("%")+1:input.find("%")+3],16)
			char = chr(char)
			input = input[:input.find("%")] + char + input[input.find("%")+3:]
		input = input.replace("+"," ")#HTML parses spaces as '+'
		try:
			cyclingprocess = subprocess.Popen([pycommand,"startcycling.py",input,str(repeat),str(50000+id),str(id)])
		except:
			return json.dumps({"success":False,"message":"Unexpected error starting startcycling.py."})
		else:
			filename = "pidfile" + str(id) + ".pickle"
			try:
				pidfileread = open(filename,"r")
			except: #File doesn't exist, but it should
				return json.dumps ({"success":False,"message":"Couldn't find a pidfile pickle database, which indicates that the connection to the ardustat wasn't initialized properly."})
			piddict = pickle.load(pidfileread)
			pidfileread.close()
			pidfilewrite = open(filename,"w")
			piddict["startcycling.py"] = cyclingprocess.pid
			pickle.dump(piddict, pidfilewrite)
			pidfilewrite.close()
			return json.dumps({"success":True,"message":"Started to cycle ardustat with ID #"+str(id)+"."})	
			
class cyclinginputparse:
	def POST(self):
		data = web.data()
		input = data[6:]
		while input.find("%") != -1:
			char = int(input[input.find("%")+1:input.find("%")+3],16)
			char = chr(char)
			input = input[:input.find("%")] + char + input[input.find("%")+3:]
		input = input.replace("+"," ")#HTML parses spaces as '+'
		result = ardustatlibrary.cyclinginputparse(input)
		return json.dumps({"success":True,"message":result})

class jqueryfile:
	def GET(self):
		return open("jquery-tools-full.min.js","r").read()

class favicon:
	def GET(self):
		web.header("Content-Type","image/x-icon")
		return open("favicon.ico", "rb").read()
		
class killself: #Run killeverything() and then quit using sys.exit()
	def POST(self):
		data = web.data()
		id = data[3:]
		if len(id) < 1: #No ID number given, so just assume nothing was started and quit
			pass
		try:
			id = int(id)
		except:
			pass
		thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		message = ""
		try:
			thesocket.connect(("localhost",50000+id))
			thesocket.send("^") #cleanly close serial connection
			thesocket.close()
			print "Cleanly closed serial connection"
		except:
			pass
		try:
			pidfile = open("pidfile"+str(id)+".pickle","r")
		except:
			pass
		else:
			try:
				piddict = pickle.load(pidfile)
				pidfile.close()
			except:
				pass
			else:
				try:
					piddict["serialforwarder.py"]
				except:
					pass
				else:
					numberofprocesseskilled = 0
					for process in piddict:
						print process, piddict[process]
						try:
							os.kill(piddict[process],9) #Kill the process with the PID in the dictionary with signal 9
						except:
							pass
		print "Closing application"
		sys.exit()
		
class killeverything: #Look in pidfile.pickle for the PIDs related to the ardustat ID # and kill the processes
	def POST(self):
		data = web.data()
		id = data[3:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		id = int(id)
		thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		message = ""
		try:
			thesocket.connect(("localhost",50000+id))
			thesocket.send("^") #cleanly close serial connection
			thesocket.close()
			print "Cleanly closed serial connection."
		except:
			pass
		try:
			pidfile = open("pidfile"+str(id)+".pickle","r")
		except:
			return json.dumps({"success":False,"message":"Could not read pidfile dictionary; no process ID numbers available"})
		else:
			try:
				piddict = pickle.load(pidfile)
				pidfile.close()
			except:
				return json.dumps({"success":False,"message":"No processes associated with ardustat ID number "+str(id)+" in pidfile dictionary"})
			else:
				try:
					piddict["serialforwarder.py"]
				except:
					return json.dumps({"success":False,"message":"No processes associated with ardustat ID number "+str(id)+" in pidfile dictionary"})
				else:
					numberofprocesseskilled = 0
					for process in piddict:
						print process, piddict[process]
						try:
							os.kill(piddict[process],9) #Kill the process with the PID in the dictionary with signal 9
							numberofprocesseskilled = numberofprocesseskilled + 1
						except:
							pass
					return json.dumps({"success":True,"message":"Killed "+str(numberofprocesseskilled)+" processes associated with ardustat ID number "+str(id)+"."})
					
class killcycling:
	def POST(self):
		data = web.data()
		id = data[3:]
		if len(id) < 1:
			return json.dumps({"success":False,"message":"No ID number was passed to this function."})
		id = int(id)
		try:
			pidfile = open("pidfile"+str(id)+".pickle","r")
		except:
			return json.dumps({"success":False,"message":"Could not read pidfile dictionary; no process ID numbers available"})
		else:
			try:
				piddict = pickle.load(pidfile)
				pidfile.close()
			except:
				return json.dumps({"success":False,"message":"No processes associated with ardustat ID number "+str(id)+" in pidfile dictionary"})
			else:
				try:
					os.kill(piddict["startcycling.py"],9)
				except:
					return json.dumps({"success":False,"message":"Error while attempting to kill cycling process!"})
				else:
					return json.dumps({"success":True,"message":"Killed the cycling process."})

if __name__ == "__main__":
	print "Starting up Ardustat web server. In your browser, go to http://localhost:8080/"
	print "Note: You must keep this terminal window open for the program to work."
	app.run()
