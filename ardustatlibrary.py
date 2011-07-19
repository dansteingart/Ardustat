import socket, serial, os, time, pickle, math, json, glob

def isArdustat(port): #Tests whether an ardustat is connected to a given port
	message = ""
	message = message + "\nTesting for ardustat on port "+str(port)+"."
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
		return {"success":False,"message":message}
	if line.find("GO") !=-1 or line.find("ST") !=-1: #These are the start and end markers of the serial lines that the ardustat spits out
		ser.close()
		return {"success":True,"message":message}
	else:
		ser.close()
		message = message + "\nNo ardustat on port "+port+"."
		return {"success":False,"message":message}

def findPorts():
	if os.name == "posix": #Mac OS X and Linux
		return glob.glob("/dev/tty.u*")+glob.glob("/dev/ttyU*")+glob.glob("/dev/ttyA*")
	elif os.name == "nt": #Windows
		ports = []
		for i in range(1,100):
			ports.append("COM"+str(i))
		return ports
	
def guessUSB(): #This finds out what the possible serial ports are and runs isArdustat on them. Mac OS X and Linux handle serial ports differently than Windows, so we split the code up for each OS
	message = ""
	possibles = findPorts()
	if len(possibles)>=1:
		for port in possibles:
			isardresult = isArdustat(port)
			message = message + isardresult["message"]
			if isardresult["success"] == True:
				message = message + "\nArdustat found on "+port+"."
				return {"success":True,"port":port,"message":message}
	else:
		return {"success":False,"message":message+"\nCouldn't find any ardustats."}

def connecttosocket(port):
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		thesocket.connect(("localhost",port))
	except:
		message = message + "\nConnection to socket "+str(port)+" failed."
		return {"success":False,"message":message}
	else:
		return {"success":True,"socket":thesocket}

def socketwrite(socketinstance,message):
	socketinstance.send(message)
	return {"success":True}

def socketread(socketinstance):
	socketwrite(socketinstance, "s0000")
	time.sleep(0.01)
	a = ""
	while 1:
		a += socketinstance.recv(1024)
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
			message = message + "Calibration data found for id#"+str(id)
			calibrated = True
		except: #If there's no resistance data
			message = message + "Calibration data not found for id #"+str(id)
			res = []
			for i in range(256):
				res.append(i/255.*10000 + 100)
			calibrated = False
	else:
		message = message + "No ID # passed to this function. Using non-calibrated resistances."
		res = []
		for i in range(256):
			res.append(i/255.*10000 + 100)
		calibrated = False
	return {"success":True,"message":message,"resistance":res[pot],"calibrated":calibrated}

def ocv(port):
	message = ""
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	socketwrite(socketresult["thesocket"],"-0000\n")

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
	message = "Set resistance to "+str(setting)
	return {"success":True,"message":message,"setting":setting}

def setVoltageDifference(potential,port):
	socketresult = connecttosocket(port)
	if socketresult["success"] == False: return {"success":False,"message":socketresult["message"]}
	setting = str(int(1023*(potential/5.0))).rjust(4,"0")
	socketwrite(socketresult["socket"],"g"+setting)
	return {"success":True,"message":"Sent command g"+setting+"."}

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
	
	if current < 0 or current > 0.02:  #Current out of range
		message = message + "\nCurrent "+str(current)+" out of range (0-0.02)."
		return {"success":False,"message":message}		
	
	if current == 0:  #Current is zero; do OCV
		ocv(port)
		message = message + "\nSet OCV mode since current was 0"
		return {"success":True,"message":message}
	
	else:
		socketreadresult = socketread(thesocket)
		if socketreadresult == False:
			message = message + "\nCouldn't read data from socket."
			return {"success":False,"message":message}
		
		parseddict = parse(socketreadresult["reading"],id)
		if parseddict["success"] == False:
			message = message + "\nCouldn't parse data: " + parseddict["message"]
			return {"success":False,"message":message}
		
		if current > 0.001:
			voltagedifference = current * 1000 #1 milliamp corresponds to 1V, 1 microamp corresponds to 1 millivolt, etc
		else:
			voltagedifference = current * 10000
		minvoltagedifference = 0.00489 #DAC has 4.89-millivolt resolution
		maxvoltagedifference = 5 - parseddict["cell_ADC"]
		if voltagedifference < minvoltagedifference: voltagedifference = minvoltagedifference
		if voltagedifference > maxvoltagedifference: voltagedifference = maxvoltagedifference
		resistancevalue = voltagedifference / current
		minresistance = resbasis(0,id)["resistance"]
		maxresistance = resbasis(255,id)["resistance"]
		
		while resistancevalue < minresistance: #If resistor can't go that low for that voltage setting...
			voltagedifference = voltagedifference + 0.00489 #Tick DAC up a setting
			if voltagedifference < maxvoltagedifference:
				resistancevalue = voltagedifference / current #Recalculate resistor setting
			else: #Voltage is maxed out and resistor still can't go low enough to source current...
				message = message + "\nYou connected a "+str(parseddict["cell_ADC"])+" cell. Max current for that cell is "+str(maxvoltagedifference/minresistance)+" A. Cannot set current as "+str(current)+" A."
				return {"success":False,"message":message}
		
		if resistancevalue > maxresistance: #If resistor can't go that high for that voltage setting...
			resistancevalue = maxresistance
			voltagedifference = resistancevalue * current #Recalculate voltage difference
			if voltagedifference < minvoltagedifference: #Voltage difference is so low at max resistance that the closest DAC setting is 0.
				message = message + "\nYour current is lower than the maximum resistance of the potentiometer * the minimum voltage difference of the DAC."
				return {"success":False,"message":message}
		
		#If we are at this point, then we find the resistor setting that corresponds to the resistance value
		resistanceresult = setResistance(resistancevalue, port, id)
		time.sleep(0.3)
		setVoltageDifference(voltagedifference, port)
		message = message + "\nSuccessfully set galvanostat. Set voltage difference to "+str(voltagedifference)+" V. Set resistance to "+str(resistanceresult["setting"])+" Ohm."
		return {"success":True,"message":message}

def raiseGround(voltage,port):
	message = ""
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		thesocket.connect(("localhost",port))
	except:
		message = message + "\nConnection to socket "+str(port)+" failed."
		return {"success":False,"message":message}
	else:
		if voltage <= 5 and voltage >= 0:
			value = voltage / 5 * 1023
			value = str(int(value))
			while len(value) < 4:
				value = "0" + value
			sendresult = thesocket.send("sd"+value) #The "d" command sets DAC A, which is connected to the auxiliary electrode, as opposed to DAC B, which is connected to the working electrode.
			message = message + "\nRaised ground to "+str(int(value)/1023.0*5)+"."
			thesocket.send("x") #shuts down connection
			thesocket.close()
			return {"success":True,"message":message}
		else:
			message = message + "\nVoltage "+str(voltage)+" out of range (0-5)."
			thesocket.send("x") #shuts down connection
			thesocket.close()
			return {"success":False,"message":message}

def calibrate(resistance,port,id): #Since the actual resistances for digital potentiometer setting are unknown, we connect a resistor of known resistance and use the voltage divider equation to find the actual resistance of each potentiometer setting, then save it in a pickle
	message = ""
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		thesocket.connect(("localhost",port))
	except:
		message = message + "\nConnection to socket "+str(port)+" failed."
		return {"success":False,"message":message}
	else:
		thesocket.send("c"+json.dumps({"resistance":resistance,"id":id}))
		time.sleep(0.1)
		thesocket.send("x")
		thesocket.close()
		return {"success":True,"message":"Started calibration with a "+str(resistance)+" ohm resistor for ardustat with ID #"+str(id)+"."}
		
def endcalibrate(port): #Blinks the ardustat LED by sending a space. This is used to see which ardustat commands are being sent to.
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	message = ""
	try:
		thesocket.connect(("localhost",port))
	except:
		message = message + "\nConnection to socket "+str(port)+" failed."
		return {"success":False,"message":message}
	else:
		thesocket.send("*")
		time.sleep(0.1)
		thesocket.send("x") #close serial connection
		thesocket.close()
		return {"success":True,"message":"Stopped calibration for ardustat with ID #"+str(id)+"."}


def begindatalog(filename, port, id): #This tells serialforwarder to start logging data
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		thesocket.connect(("localhost",port))
	except:
		return {"success":False,"message":"Connection to socket "+str(port)+" failed."}
	else:
		logdict = {"filename":filename,"id":id}
		thesocket.send("l"+json.dumps(logdict))
		time.sleep(0.1)
		thesocket.send("x")
		thesocket.close()
		return {"success":True,"message":"Started logging data; used filename "+filename+" and ID #"+str(id)}
		
def enddatalog(port):
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		thesocket.connect(("localhost",port))
	except:
		return {"success":False,"message":"Connection to socket "+str(port)+" failed."}
	else:
		thesocket.send("~") #Command to stop logging
		time.sleep(0.1)
		thesocket.send("x")
		thesocket.close()
		return {"success":True,"message":"Told serialforwarder.py to end logging."}

def cycle(input, repeat, port, id): #Scripted control mechanism for ardustat. To understand the syntax, see the cycling instructions in the 'Instructions' folder
	input = input.split("\n")
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	message = ""
	try:
		thesocket.connect(("localhost",port))
	except:
		message = message + "\nConnection to socket "+str(port)+" failed."
		return {"success":False,"message":message}
	else:
		keepcycling = True
		while keepcycling == True:
			for line in input:
				newline = line.split(" ")
				if newline[0] == "0": #Sets current to a specified level until the potential reaches a specified level
					print "Setting current to " + newline[1] + " mA until potential reaches "+newline[2]+" V\n"
					currentinamperes = float(newline[1])*0.001
					galvanostat(currentinamperes, port, id)
					potentiallimit = float(newline[2])
					loop = True
					while loop==True:
						thesocket.send("a")
						line = thesocket.recv(1023)
						parsedict = parse(line,id)
						if parsedict["success"] == True:
							if parsedict["cellVoltage"] >= potentiallimit:
								loop = False
							else:
								print "Potential is "+str(parsedict["cellVoltage"])+" V < "+str(potentiallimit)+" V."
						else:
							print "Error parsing data for cycling!"
					print "Potential has reached "+str(potentiallimit)+" V."					
				elif newline[0] == "1": #Sets current to a specified level for a specified amount of time
					print "Setting current to " + newline[1] + " mA for "+newline[2]+" seconds\n"
					currentinamperes = float(newline[1])*0.001
					galvanostat(currentinamperes, port, id)
					time.sleep(float(newline[2]))
				elif newline[0] == "2": #Sets potential to a specified level until current reaches a specified level
					print "Setting potential to "+ newline[1] + " V until current reaches "+newline[2]+" mA\n"
					potentiostat(float(newline[1]), port)
					time.sleep(0.1)
					currentinamperes = float(newline[2])*0.001
					currentlimit = currentinamperes
					loop = True
					while loop == True:
						thesocket.send("a")
						line = thesocket.recv(1023)
						parsedict = parse(line,id)
						if parsedict["success"] == True:
							if parsedict["current"] >= currentlimit:
								loop = False
							else:
								print "Current is "+str(parsedict["current"])+" A < "+str(currentlimit)+" A."
						else:
							print "Error parsing data for cycling!"
					print "Current has reached "+str(currentlimit)+" A."
						
				elif newline[0] == "3": #Sets potential to a specified level for a specified amount of time
					print "Setting potential to "+ newline[1] + " V for "+newline[2]+" seconds\n"
					potentiostat(float(newline[1]), port)
					time.sleep(float(newline[2]))
				else:
					print "Syntax error!\n"
			if repeat == 1:
				keepcycling = True
			else:
				keepcycling = False
		thesocket.send("x")
		thesocket.close()
		return {"success":True,"message":"Cycling functions completed."}
		
def blink(port): #Blinks the ardustat LED by sending a space. This is used to see which ardustat commands are being sent to.
	thesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	message = ""
	try:
		thesocket.connect(("localhost",port))
	except:
		message = message + "\nConnection to socket "+str(port)+" failed."
		return {"success":False,"message":message}
	else:
		thesocket.send("s ")
		time.sleep(0.1)
		thesocket.send("x") #close serial connection
		thesocket.close()
		return {"success":True,"message":"The id number was "+str(id)+". The command sent was  ."}
		
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
		outdict['last_command'] = parts[7]
		outdict['calibration'] = resbasis(outdict['pot_step'],id)["calibrated"]
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
