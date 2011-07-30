import socket, serial, os, time, pickle, math, json, glob, subprocess, ConfigParser

config = ConfigParser.ConfigParser()
config.read("ardustatrc.txt")

pycommand = str(config.get("values","pycommand"))
portconstant = int(config.get("values","portconstant"))
loggingpause = float(config.get("values","loggingpause"))
enabledebugging = config.get("values","enabledebugging")
if enabledebugging == "True": enabledebugging = True
else: enabledebugging = False
verbosemode = config.get("values","verbosemode")
if verbosemode == "True": verbosemode = True
else: verbosemode = False

def isArdustat(port): #Tests whether an ardustat is connected to a given port
	message = ""
	message = message + "\nTesting for ardustat on port "+str(port)+"."
	if verbosemode == True: print message.split("\n")[-1]
	try:
		ser=serial.Serial(port,57600,timeout=5) #The ardustat uses a baudrate of 57600. This can be changed in the firmware
	except:
		return {"success":False,"message":message}
	time.sleep(0.1)
	ser.readline() #Somehow this initializes the connection or something
	ser.write("s0000\n")
	time.sleep(0.1)
	try:
		line = ser.readlines()[-1]
	except:
		ser.close()
		message = message + "\nNo ardustat on port "+port+" or error getting serial data from ardustat."
		if verbosemode == True: print message.split("\n")[-1]
		return {"success":False,"message":message}
	if line.find("GO") !=-1 or line.find("ST") !=-1: #These are the start and end markers of the serial lines that the ardustat spits out
		ser.close()
		return {"success":True,"message":message}
	else:
		ser.close()
		message = message + "\nNo ardustat on port "+port+"."
		if verbosemode == True: print message.split("\n")[-1]
		return {"success":False,"message":message}

def findPorts():
	if os.name == "posix": #Mac OS X and Linux
		ports = glob.glob("/dev/tty.u*")+glob.glob("/dev/ttyU*")+glob.glob("/dev/ttyA*")
		return {"success":True,"ports":ports}
	elif os.name == "nt": #Windows
		ports = []
		for i in range(1,100):
			ports.append("COM"+str(i))
		return {"success":True,"ports":ports}
	
def guessUSB(): #This finds out what the possible serial ports are and runs isArdustat on them. Mac OS X and Linux handle serial ports differently than Windows, so we split the code up for each OS
	message = ""
	possibles = findPorts()["ports"]
	if len(possibles)>=1:
		for port in possibles:
			isardresult = isArdustat(port)
			message = message + isardresult["message"]
			if isardresult["success"] == True:
				message = message + "\nArdustat found on "+port+"."
				if verbosemode == True: print message.split("\n")[-1]
				return {"success":True,"port":port,"message":message}
	else:
		return {"success":False,"message":message+"\nCouldn't find any ardustats."}

def connecttoardustat(serialport,id,autoconnect=True):
	message = ""
	if autoconnect == True:
		result = guessUSB()
		if result["success"] == True:
			serialport = result["port"]
		else:
			return {"success":False,"message":"Couldn't find serial port to autoconnect to. guessUSB() returned:"+result["message"]}
	try:
		serialforwarderprocess = subprocess.Popen([pycommand,"tcp_serial_redirect.py","-p",serialport,"-P",str(portconstant+id),"-b","57600"])
	except:
		if enabledebugging == True: raise
		return {"success":False,"message":"Unexpected error starting serialforwarder.py."}
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
			return {"success":True,"message":"Started to open ardustat on port "+serialport+"."}
		else:
			return {"success":True,"message":"Started to open ardustat on port "+serialport+". guessUSB() returned:"+result["message"]}

def connecttosocket(port):
	message = ""
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		thesocket.connect(("localhost",port))
		thesocket.settimeout(1)
	except:
		if enabledebugging == True: raise
		message = message + "\nConnection to socket "+str(port)+" failed."
		if verbosemode == True: print message.split("\n")[-1]
		return {"success":False,"message":message}
	else:
		return {"success":True,"socket":thesocket}

def socketwrite(socketinstance,message,id=None):
	for i in range(1):
		socketinstance.send(message+"\n")
		time.sleep(0.05)
	return {"success":True}

def socketread(socketinstance):
	socketinstance.send("s0000\n")
	time.sleep(0.01)
	a = ""
	while 1:
		try:
			a += socketinstance.recv(1024)
		except:
			socketinstance.send("s0000\n")
		if a.find("ST\r\n") > 1:
			return {"success":True,"reading":a.strip()}

def refbasis(reading,ref): #Feturns an absolute potential based on the ADC reading against the 2.5 V reference
		return round((float(reading)/float(ref))*2.5,3)

def resbasis(pot,id=None): #Returns the value in ohms for the givening potentiometer setting
	message = ""
	if isinstance(id,int):
		try:
			f = open("resistances.pickle","r")
			resdict = pickle.load(f)
			f.close()
			res = resdict[str(id)] #This variable stores the resistance data for the Ardustat with that specific ID number
			message = message + "\nCalibration data found for id#"+str(id)
			if verbosemode == True: print message.split("\n")[-1]
			calibrated = True
		except: #If there's no resistance data
			message = message + "\nCalibration data not found for id #"+str(id)
			if verbosemode == True: print message.split("\n")[-1]
			res = []
			for i in range(256):
				res.append(i/255.*10000 + 100)
			calibrated = False
	else:
		message = message + "\nNo ID # passed to this function. Using non-calibrated resistances."
		if verbosemode == True: print message.split("\n")[-1]
		res = []
		for i in range(256):
			res.append(i/255.*10000 + 100)
		calibrated = False
	try:
		res[pot]
	except:
		message = message + "\nPotentiometer setting "+str(pot)+" out of range (0-255)!"
		if verbosemode == True: print message.split("\n")[-1]
		print message.split("\n")[-1]
		return {"success":False,"message":message,"resistance":False,"calibrated":calibrated}
	else:
		return {"success":True,"message":message,"resistance":res[pot],"calibrated":calibrated}

def ocv(port):
	message = ""
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	else:
		socketwrite(socketresult["socket"],"-0000")
		return {"success":True,"message":"Set to OCV"}

def setResistance(resistance,port,id=None):
	message = ""
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	closestvalue = 0
	for i in range(1,256):
		if math.fabs(resistance - resbasis(i,id)["resistance"]) < math.fabs(resistance - resbasis(closestvalue,id)["resistance"]): #If the absolute value of the difference between this resistance and the ideal resistance is less than the absolute value of the other closest difference...
			closestvalue = i
	closestvalue = str(closestvalue).rjust(4,"0")
	socketwrite(socketresult["socket"],"r"+closestvalue)
	setting = resbasis(int(closestvalue),id)["resistance"]
	message = message + "\nSet resistance to "+str(setting)
	if verbosemode == True: print message.split("\n")[-1]
	return {"success":True,"message":message,"setting":setting}

def setVoltageDifference(potential,port):
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	if potential >= 0:
		setting = str(int(1023*(potential/5.0))).rjust(4,"0")
	else:
		setting = str(int(1023*(math.fabs(potential)/5.0))+2000)
	socketwrite(socketresult["socket"],"g"+setting)
	return {"success":True,"message":"Sent command g"+setting+"."}

def raiseGround(potential,port):
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	setting = str(int(1023*(potential/5.0)) + 2000).rjust(4,"0")
	socketwrite(socketresult["socket"],"X"+setting)
	return {"success":True,"message":"Sent command X"+setting+"."}

def potentiostat(potential, port):
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	setting = str(int(1023*(potential/5.0))).rjust(4,"0")
	socketwrite(socketresult["socket"],"p"+setting)
	return {"success":True,"message":"Sent command p"+setting+"."}

def galvanostat(current,port,id=None): #This takes a specified current as input and calculates the right resistor setting and voltage difference to set it. See http://steingart.ccny.cuny.edu/ardustat-theory
	message = ""
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	thesocket = socketresult["socket"]
	
	if id == None:
		message = message + "\nWarning: No ID # passed to this function!"
		if verbosemode == True: print message.split("\n")[-1]
		
	if current == 0:  #Current is zero; do OCV
		ocv(port)
		message = message + "\nSet OCV mode since current was 0"
		if verbosemode == True: print message.split("\n")[-1]
		return {"success":True,"message":message}
	
	else:
		socketreadresult = socketread(thesocket)
		if socketreadresult == False:
			message = message + "\nCouldn't read data from socket."
			if verbosemode == True: print message.split("\n")[-1]
			return {"success":False,"message":message}
		
		parseddict = parse(socketreadresult["reading"],id)
		if parseddict["success"] == False:
			message = message + "\nCouldn't parse data: " + parseddict["message"]
			if verbosemode == True: print message.split("\n")[-1]
			return {"success":False,"message":message}
		
		if current > 0.001 or current < -0.001:
			voltagedifference = current * 1000 #1 milliamp corresponds to 1V, 1 microamp corresponds to 1 millivolt, etc
		else:
			voltagedifference = current * 10000
		minvoltagedifference = parseddict["cell_ADC"] * -1
		maxvoltagedifference = 5 - parseddict["cell_ADC"]
		if voltagedifference < minvoltagedifference: voltagedifference = minvoltagedifference
		if voltagedifference > maxvoltagedifference: voltagedifference = maxvoltagedifference
		resistancevalue = voltagedifference / current
		minresistance = resbasis(0,id)["resistance"]
		maxresistance = resbasis(255,id)["resistance"]
		
		while resistancevalue < minresistance: #If resistor can't go that low for that voltage setting...
			if voltagedifference >= 0:
				voltagedifference = voltagedifference + 0.00489 #Tick DAC up a setting
				if voltagedifference < maxvoltagedifference:
					resistancevalue = voltagedifference / current #Recalculate resistor setting
				else: #Voltage is maxed out and resistor still can't go low enough to source current...
					message = message + "\nYou connected a "+str(parseddict["cell_ADC"])+" cell. Max current for that cell is "+str(maxvoltagedifference/minresistance)+" A. Cannot set current as "+str(current)+" A."
					if verbosemode == True: print message.split("\n")[-1]
					return {"success":False,"message":message}
			else:
				voltagedifference = voltagedifference - 0.00489 #Tick DAC down a setting
				if voltagedifference > minvoltagedifference:
					resistancevalue = voltagedifference / current #Recalculate resistor setting
				else: #Voltage is at lowest value and resistor still can't go low enough to source current...
					message = message + "\nYou connected a "+str(parseddict["cell_ADC"])+" cell. Min current for that cell is "+str(minvoltagedifference/minresistance)+" A. Cannot set current as "+str(current)+" A."
					if verbosemode == True: print message.split("\n")[-1]
					return {"success":False,"message":message}

		
		if resistancevalue > maxresistance: #If resistor can't go that high for that voltage setting...
			resistancevalue = maxresistance
			voltagedifference = resistancevalue * current #Recalculate voltage difference
			if voltagedifference < minvoltagedifference: #Voltage difference is so low at max resistance that the closest DAC setting is 0.
				message = message + "\nYour current is lower than the maximum resistance of the potentiometer * the minimum voltage difference of the DAC."
				if verbosemode == True: print message.split("\n")[-1]
				return {"success":False,"message":message}
		
		#If we are at this point, then we find the resistor setting that corresponds to the resistance value
		resistanceresult = setResistance(resistancevalue, port, id)
		time.sleep(0.3)
		setVoltageDifference(voltagedifference, port)
		message = message + "\nSuccessfully set galvanostat. Set voltage difference to "+str(voltagedifference)+" V. Set resistance to "+str(resistanceresult["setting"])+" Ohm."
		if verbosemode == True: print message.split("\n")[-1]
		return {"success":True,"message":message}

def calibrate(resistance,port,id): #Since the actual resistances for digital potentiometer setting are unknown, we connect a resistor of known resistance and use the voltage divider equation to find the actual resistance of each potentiometer setting, then save it in a pickle
	message = ""
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	thesocket = socketresult["socket"]
	
	message = message + "Beginning calibration for ardustat with ID #"+str(id)
	print message
	socketwrite(thesocket,"X1023")
	time.sleep(0.2)
	socketwrite(thesocket,"R")
	time.sleep(0.2)
	rescount = 0
	reslist = [[] for x in range(256)]
	while rescount <= (256 * 5):
		line = socketread(thesocket)["reading"]
		parsedict = parse(line,id)
		if parsedict["success"] == True:
			line = line.split(",")
			try:
				reslist[int(line[4])].append((resistance*int(line[3]))/int(line[2]) - resistance) #Add calculated resistance for that potentiometer setting ( equal to (R(in)*DAC)/ADC - R(in) )
				rescount +=1
			except:
				self.ocv()
				if enabledebugging == True: raise
				message = message + "\nUnexpected error in calibration with serial input "+str(line)
				if verbosemode == True: print message.split("\n")[-1]
				print message.split("\n")[-1]
				return {"success":False,"message":message}
			print "Calibration: " + str(float(rescount)/(256*5)*100)[:4]+"%"
	ocv(port)
	#calculate average
	res = [sum(x)/len(x) for x in reslist]
	try:
		f = open("resistances.pickle","r")
		resdict = pickle.load(f)
		f.close()
	except:
		pass
	try:
		resdict[str(id)] = res
	except: #There is no existing resistance data; create the initial dictionary
		resdict = {str(id):res}
	try:
		f = open("resistances.pickle",'w')
	except:
		if enabledebugging == True: raise
		message = message + "\nCouldn't open resistances.pickle file for writing. It may be open in another program. Couldn't save calibration data."
		if verbosemode == True: print message.split("\n")[-1]
		return {"success":False,"message":message}
	try:
		pickle.dump(resdict,f)
	except:
		if enabledebugging == True: raise
		message = message + "\nCouldn't write data to resistances.pickle. Couldn't save calibration data."
		if verbosemode == True: print message.split("\n")[-1]
		return {"success":False,"message":message}
	else:
		message = message + "\nCalibration completed and saved for Ardustat #"+str(id)
		if verbosemode == True: print message.split("\n")[-1]
		return {"success":True,"message":message}
	f.close()

def begindatalog(filename,port,id):
	try:
		ardustatloggerprocess = subprocess.Popen([pycommand,"ardustatlogger.py",filename,str(port),str(id)])
	except:
		if enabledebugging == True: raise
		return {"success":False,"message":"Unexpected error starting ardustatlogger.py."}
	else:
		pidfilename = "pidfile" + str(id) + ".pickle"
		try:
			pidfileread = open(pidfilename,"r")
		except: #File doesn't exist, but it should
			return {"success":False,"message":"Couldn't find a pidfile pickle database, which indicates that the connection to the ardustat wasn't initialized properly."}
		piddict = pickle.load(pidfileread)
		pidfileread.close()
		pidfilewrite = open(pidfilename,"w")
		piddict["ardustatlogger.py"] = ardustatloggerprocess.pid
		#piddict["logfilename"] = filename
		pickle.dump(piddict, pidfilewrite)
		pidfilewrite.close()
		return {"success":True,"message":"Started to log data with filename "+filename+"."}
		
def log(filename,port,id): #This is the actual logging function
	print "Initializing logging function"
	message = ""
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	print "Connected to socket"
	thesocket = socketresult["socket"]
	initfileio = True
	calibratecheck = True
	while 1:
		time.sleep(loggingpause)
		line = socketread(thesocket)["reading"]
		parsedict = parse(line,id)
		if parsedict["success"] == True:
			if initfileio == True:
				message = message + "\nStarting file I/O:"
				print message.split("\n")[-1]
				rawdatafilename = filename+"-raw.csv"
				parseddatafilename = filename+"-parsed.csv"
				try:
					a = open(rawdatafilename,"r")
					b = open(parseddatafilename,"r")
					a.close()
					b.close()
				except:
					message = message + "\nCreating new files "+rawdatafilename+" and "+parseddatafilename+"."
					print message.split("\n")[-1]
					a = open(rawdatafilename,"w") #If no file exists, make an empty new file. If a file exists, just append to it.
					b = open(parseddatafilename,"w")
					a.close()
					b.close()
					rawdatafile = open(rawdatafilename,"a")
					parseddatafile = open(parseddatafilename,"a")
				else:
					message = message + "\nFiles already exist; continuing log"
					print message.split("\n")[-1]
					#Begin script to delete last, possibly corrupted line of data from file
					a = open(rawdatafilename,"r+")
					b = open(parseddatafilename,"r+")
					adata = a.readlines()
					bdata = b.readlines()
					a.close()
					b.close()
					a.write("\n".join(adata[:-2])+"\n")
					b.write("\n".join(adata[:-2])+"\n")
					#End script to delete last line of data
					rawdatafile = open(rawdatafilename,"a")
					parseddatafile = open(parseddatafilename,"a")
					initfileio = False
				message = message + "\n" + rawdatafilename+" and "+parseddatafilename+" are ready to record data."
				print message.split("\n")[-1]
				message = message + "\nID # is: "+str(id)
				print message.split("\n")[-1]
				if initfileio == True:
					rawdatafile.write("Unix Time,Data Start Marker,DAC setting,Cell Voltage (ADC 0),DAC Measurement (ADC 1),DVR Setting,Output Setting Value,Mode,Last Command,GND Measurement,Reference Electrode,Reference Voltage,Data Stop Marker\n")
					parseddatafile.write("Unix Time,DAC 0 Setting (V),DAC 0 Reading (ADC 1) (V),Cell Voltage (ADC 0) (V),Potentiometer Setting (0-255),Potentiometer Setting (Ohms),GND Reading (ADC 2) (V),Current Calculation (A),Cell Resistance Calculation (Ohms),Reference Electrode Reading (ADC 3) (V),Mode,Setting (V),Last Command Received,Calibrated,Cell Voltage Reading - Reference Electrode Reading (V)\n")
				initfileio = False

			try:
				rawdatafile.write(str(parsedict["time"])+","+line.replace("\0","")+"\n") #Tack on the unix time to the beginning of the raw data, clean it up, and record it
				d = lambda x: str(parsedict[x])+"," #Convert dictionary items to CSV format
				parsestring = d("time")+d("DAC0_setting")+d("DAC0_ADC")+d("cell_ADC")+d("pot_step")+d("resistance")+d("GND")+d("current")+d("cell_resistance")+d("reference_electrode")+d("mode")+d("setting")+d("last_command").replace("\0","")+d("calibration")+d("cell_ADC-reference_electrode")[:-1]+"\n"
				parseddatafile.write(parsestring)
				if parsedict["calibration"] == False and calibratecheck == True: #Nag the user to calibrate only once if their ardustat isn't calibrated
					message = message + "\nWarning: Your ardustat is not calibrated. This can lead to highly inaccurate data! Please calibrate your ardustat."
					print message.split("\n")[-1]
					calibratecheck = False
			except:
				message = message + "\nError writing data to files!"
				print message.split("\n")[-1]
				#Keep going anyway
		else:
			message = message + "\nError parsing data. Skipping through to get new data..."
			print message.split("\n")[-1]
		
def enddatalog(id):
	try:
		pidfile = open("pidfile"+str(id)+".pickle","r")
	except:
		if enabledebugging == True: raise
		return {"success":False,"message":"Could not read pidfile dictionary; no process ID numbers available"}
	else:
		try:
			piddict = pickle.load(pidfile)
			pidfile.close()
		except:
			if enabledebugging == True: raise
			return {"success":False,"message":"No processes associated with ardustat ID number "+str(id)+" in pidfile dictionary"}
		else:
			try:
				os.kill(piddict["ardustatlogger.py"],9)
			except:
				if enabledebugging == True: raise
				return {"success":False,"message":"Error while attempting to kill logging process!"}
			else:
				return {"success":True,"message":"Killed the logging process."}
		
def blink(port): #Blinks the ardustat LED by sending a space. This is used to see which ardustat commands are being sent to.
	message = ""
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	socketwrite(socketresult["socket"]," 0000")
	return {"success":True,"message":"Sent command \" 0000\"."}

def ask(port, id=None):
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	thesocket = socketresult["socket"]
	p = parse(socketread(socketresult["socket"])["reading"],id)
	printstring = 'Data Loaded:\nDAC 0 arduino setting.............: ' + str(p["DAC0_setting"])
	printstring += ' V\nDAC 0 reading..............(ADC 1): ' + str(p["DAC0_ADC"])  
	printstring += ' V\nCell Voltage reading.......(ADC 0): ' + str(p["cell_ADC"]) 
	printstring += ' V\nResistor arduino setting..........: ' + str(p["resistance"]) 
	printstring += ' Ohm\nCurrent calculation...............: ' + str(p["current"]) 
	printstring += ' A\nCell resistance calculation.......: ' + str(p["cell_resistance"]) 
	printstring += ' Ohm\nGND reading................(ADC 2): ' + str(p["GND"]) 
	printstring += " V\nReference electrode reading(ADC 3): " + str(p["reference_electrode"]) 
	printstring += " V\nVoltage reference value....(ADC 5): " + str(p["ref"]) 
	printstring += " \nMode..............................: " +str(p["mode"])
	printstring += "\nLast command sent.................: " + str(p["last_command"]) 
	printstring += "\nRaw data: " + str(p["raw"]).replace("\n","")
	printstring += "\nCalibrated: " + str(p["calibration"])
	return {"success":True,"message":printstring}

		
def parse(reading,id=None):
	outdict = {}
	#format GO,1023,88,88,255,0,1,-0000,0,0,510,ST 
	#0 -> "GO"
	#1 -> DAC Setting
	#2 -> Cell Voltage
	#3 -> DAC Measurement
	#4 -> DVR Setting
	#5 -> Setting that potentiostat or galvanostat functions are using
	#6 -> Mode (0 = manual, 1 = OCV, 2 = potentiostat, 3 = galvanostat)
	#7 -> Last command received
	#8 -> GND Measurement
	#9 -> Reference Electrode
	#10 -> Reference Voltage
	#11 -> "ST"
	if reading.find("GO") == 0 and reading.find("ST") and reading.rfind("GO") == 0:
		outdict['success'] = True
		outdict['raw'] = reading
		outdict['time'] = time.time()
		parts = reading.split(",")
		outdict['ref'] = float(parts[len(parts)-2])
		outdict['DAC0_setting'] = int(parts[1]) / 1023.0 * 5.0
		outdict['DAC0_ADC'] = refbasis(parts[3],outdict['ref'])
		outdict['cell_ADC'] = refbasis(parts[2],outdict['ref'])
		outdict['pot_step'] = int(parts[4])
		outdict['resistance'] = resbasis(outdict['pot_step'],id)["resistance"]
		outdict['GND'] = refbasis(parts[8],outdict['ref'])
		try:
			current = (float(outdict['DAC0_ADC'])-float(outdict['cell_ADC']))/outdict['resistance']
		except: #Divide by 0
			current = False
		outdict['current'] = current
		try:
			if outdict['DAC0_ADC'] == 0: #DAC 1 is set...
				cellresistance = (outdict['cell_ADC']/outdict['GND'])*outdict['resistance']/(1-(outdict['cell_ADC']/outdict['GND']))
			elif outdict['GND'] == 0:
				cellresistance = (outdict['cell_ADC']/outdict['DAC0_ADC'])*outdict['resistance']/(1-(outdict['cell_ADC']/outdict['DAC0_ADC']))
			else:
				cellresistance = False
		except:
			cellresistance = False
		outdict['cell_resistance'] = cellresistance
		outdict['reference_electrode'] = refbasis(parts[9],outdict['ref'])
		if parts[6] == "0":
			mode = "Manual"
		elif parts[6] == "1":
			mode = "OCV"
		elif parts[6] == "2":
			mode = "Potentiostat"
		elif parts[6] == "3":
			mode = "Galvanostat"
		else:
			mode = "Unknown"
		outdict['mode'] = mode
		outdict['setting'] = refbasis(parts[5],outdict['ref'])
		outdict['last_command'] = parts[7]
		outdict['calibration'] = resbasis(outdict['pot_step'],id)["calibrated"]
		outdict['cell_ADC-reference_electrode'] = outdict['cell_ADC']-outdict['reference_electrode']
	else:
		outdict['success'] = False
	return outdict

def cyclinginputparse(thestr): #Tells the user what their cycling script will do in plain english
	thestr = thestr.split("\n")
	returnstr = ""
	for line in thestr:
		newline = line.split(" ")
		if newline[0] == "0":
			returnstr = returnstr + "Set current to " + newline[1] + " mA until potential reaches "+newline[2]+" V\n"
		elif newline[0] == "1":
			returnstr = returnstr + "Set current to " + newline[1] + " mA for "+newline[2]+" seconds\n"
		elif newline[0] == "2":
			returnstr = returnstr + "Set potential to "+ newline[1] + " V until current reaches "+newline[2]+" mA\n"
		elif newline[0] == "3":
			returnstr = returnstr + "Set potential to "+ newline[1] + " V for "+newline[2]+" seconds\n"
		else:
			returnstr = returnstr + "Syntax error!\n"
	if thestr[len(thestr)-1] != "1 0 0":
		returnstr = returnstr + "Warning! Your script does not end with \"1 0 0\". Every script should end with this!\n"
	return returnstr

def shutdown(id):
	try:
		pidfile = open("pidfile"+str(id)+".pickle","r")
	except:
		if enabledebugging == True: raise
		return {"success":False,"message":"Could not read pidfile dictionary; no process ID numbers available"}
	else:
		try:
			piddict = pickle.load(pidfile)
			pidfile.close()
		except:
			return {"success":False,"message":"No processes associated with ardustat ID number "+str(id)+" in pidfile dictionary"}
		else:
			for process in piddict:
				try:
					os.kill(piddict[process],9)
				except:
					pass
			return {"success":True,"message":"Killed the following processes: "+str(piddict)+"."}
