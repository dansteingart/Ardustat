import serial 
import socket
import glob
import os
import time
import pickle
import math
import json
import matplotlib.pyplot

class ardustat:
	def __init__(self):	
		self.port = ""
		self.ser = serial.Serial()
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.mode = "socket"

	def findPorts(self):
		if os.name == "posix": #Mac OS X and Linux
			return glob.glob("/dev/tty.u*")+glob.glob("/dev/ttyU*")+glob.glob("/dev/ttyA*")
		elif os.name == "nt": #Windows
			ports = []
			for i in range(1,100):
				ports.append("COM"+str(i))
			return ports
			
	#isArdustat() and guessUSB() lifted from the old ardustatlibrary.py with slight modifications to enable an autoConnect function
	def isArdustat(self,port): #Tests whether an ardustat is connected to a given port
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
		line = ser.readline()
		if line.find("GO") !=-1 or line.find("ST") !=-1: #These are the start and end markers of the serial lines that the ardustat spits out
			ser.close()
			return {"success":True,"message":message}
		else:
			ser.close()
			message = message + "\nNo ardustat on port "+port+"."
			return {"success":False,"message":message}
		
	def guessUSB(self): #This finds out what the possible serial ports are and runs isArdustat on them. Mac OS X and Linux handle serial ports differently than Windows, so we split the code up for each OS
		message = ""
		possibles = self.findPorts()
		if len(possibles)>=1:
			for port in possibles:
				isardresult = self.isArdustat(port)
				message = message + isardresult["message"]
				if isardresult["success"] == True:
					message = message + "\nArdustat found on "+port+"."
					return {"success":True,"port":port,"message":message}
		else:
			return {"success":False,"message":message+"\nCouldn't find any ardustats."}
	
	def autoConnect(self,mode="serial"):
		guessusbresult = self.guessUSB()
		if guessusbresult["success"] == True:
			if mode == "serial":
				self.mode = "serial"
				print self.connect(guessusbresult["port"])
			elif mode == "socket":
				print "Socket autoconnection not supported yet"
		else:
			print guessusbresult["message"]

	def connect(self,port):
		if self.mode == "serial":
			self.ser = serial.Serial(port,57600)
			self.ser.timeout = 1
			self.ser.open()
			return "connected to serial"
		if self.mode == "socket":
			self.s.connect(("localhost",port))
			return "connected to socket"
		
	
	def ocv(self):
		self.rawwrite("-0000")
	
	def potentiostat(self,potential):
		potential = str(int(1023*(potential/5.0))).rjust(4,"0")
		self.rawwrite("p"+potential)
		
	def rawwrite(self,command):
		if self.mode == "serial":
			self.ser.write(command+"\n")
		if self.mode == "socket":
			self.s.send(command)
	
	def rawread(self):
		self.rawwrite("s0000")
		time.sleep(.01)
		if self.mode == "serial":
			return self.ser.readlines()[-1] #If readlines returns a list, get the last element in the list
		if self.mode == "socket":
			a = ""
			while 1:
				a += self.s.recv(1024)
				if a.find("ST\r\n") > 1: return a.strip()
	
	def last_raw_reading(self):
		out = ""
		while self.ser.inWaiting() > 0: out = self.ser.readline()
		return out
	
	def refbasis(self,reading,ref):
		"""returns an absolute potential based on the ADC reading against the 2.5 V reference
		   (reading from pot as a value between 0 and 1023, reference value in V (e.g. 2.5))"""
		return round((float(reading)/float(ref))*2.5,3)
	
	def resbasis(self,pot,id=None):
		"""returns the value for the givening potentiometer setting 
			(reading as value between 0 and 255, pot lookup variable)"""
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
		
	def parse(self,reading,id=None):
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
			outdict['DAC0_setting'] = int(parts[2]) / 1023.0 * 5.0
			outdict['DAC0_ADC'] = self.refbasis(parts[3],outdict['ref'])
			outdict['cell_ADC'] = self.refbasis(parts[2],outdict['ref'])
			outdict['pot_step'] = int(parts[4])
			outdict['resistance'] = self.resbasis(outdict['pot_step'],id)["resistance"]
			outdict['GND'] = self.refbasis(parts[8],outdict['ref'])
			try:
				current = (float(outdict['DAC0_ADC'])-float(outdict['cell_ADC']))/outdict['resistance']
						 #(float(outdict['DAC0_ADC'])-float(outdict['cell_ADC']))/outdict['res']			
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
			outdict['reference_electrode'] = self.refbasis(parts[9],outdict['ref'])
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
			outdict['calibration'] = self.resbasis(outdict['pot_step'],id)["calibrated"]
		else:
			outdict['success'] = False
		return outdict
	
	def viewData(self,id=None):
		p = self.parse(self.rawread(),id)
		printstring = 'Data Loaded:\nDAC 0 arduino setting.............: ' + str(p["DAC0_setting"])
		printstring += ' V\nDAC 0 reading..............(ADC 1): ' + str(p["DAC0_ADC"])  
		printstring += ' V\nCell Voltage reading.......(ADC 0): ' + str(p["cell_ADC"]) 
		printstring += ' V\nResistor arduino setting..........: ' + str(p["resistance"]) 
		printstring += ' Ohm\nCurrent calculation...............: ' + str(p["current"]) 
		printstring += ' A\nCell resistance calculation.......: ' + str(p["cell_resistance"]) 
		printstring += ' Ohm\nGND reading................(ADC 2): ' + str(p["GND"]) 
		printstring += " V\nReference electrode reading(ADC 3): " + str(p["reference_electrode"]) 
		printstring += " V\nVoltage reference value....(ADC 5): " + str(p["ref"]) 
		printstring += " V\nMode..............................: " +str(p["mode"])
		printstring += "\nLast command sent.................: " + str(p["last_command"]) 
		printstring += "\nRaw data: " + str(p["raw"]).replace("\n","")
		printstring += "\nCalibrated: " + str(p["calibration"])
		print printstring
	
	def setGNDDAC(self,potential,auto_set_other_dac_to_zero=True):
		if auto_set_other_dac_to_zero == True:
			potential = str(int(1023*(potential/5.0)) + 2000).rjust(4,"0")
			self.rawwrite("X"+potential)
		else:
			potential = str(int(1023*(potential/5.0))).rjust(4,"0")
			self.rawwrite("d"+potential)
	
	def setDAC(self,potential,auto_set_other_dac_to_zero=True):
		potential = str(int(1023*(potential/5.0))).rjust(4,"0")
		if auto_set_other_dac_to_zero==True:
			self.rawwrite("X"+potential)
		else:
			self.rawwrite("+"+potential)
		
	def setResistance(self,resistance,id=None):
		message = ""
		closestvalue = 0
		for i in range(1,256):
			if math.fabs(resistance - self.resbasis(i,id)["resistance"]) < math.fabs(resistance - self.resbasis(closestvalue,id)["resistance"]): #If the absolute value of the difference between this resistance and the ideal resistance is less than the absolute value of the other closest difference...
				closestvalue = i
		closestvalue = str(closestvalue).rjust(4,"0")
		self.rawwrite("r"+closestvalue)
		message = "Set resistance to "+str(self.resbasis(int(closestvalue),id)["resistance"])
		print message.split("\n")[-1]
		return {"success":True,"message":message,"setting":self.resbasis(int(closestvalue),id)["resistance"]}
		
	def calibrate(self, resistance, id):
		message = ""
		message = message + "Beginning calibration for ardustat with ID #"+str(id)
		print message
		self.rawwrite("+1023")
		time.sleep(0.2)
		self.rawwrite("R")
		time.sleep(0.2)
		rescount = 0
		reslist = [[] for x in range(256)]
		while rescount <= (256 * 5):
			line = self.rawread()
			parsedict = self.parse(line,id)
			if parsedict["success"] == True:
				line = line.split(",")
				try:
					reslist[int(line[4])].append((resistance*int(line[3]))/int(line[2]) - resistance) #Add calculated resistance for that potentiometer setting ( equal to (R(in)*DAC)/ADC - R(in) )
					rescount +=1
				except:
					self.ocv()
					message = message + "\nUnexpected error in calibration with serial input "+str(line)
					print message.split("\n")[-1]
					return {"success":False,"message":message}
				print "Calibration: " + str(float(rescount)/(256*5)*100)[:4]+"%"
		self.ocv()
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
			message = message + "\nCouldn't open resistances.pickle file for writing. It may be open in another program. Couldn't save calibration data."
			print message.split("\n")[-1]
			return {"success":False,"message":message}
		try:
			pickle.dump(resdict,f)
		except:
			message = message + "\nCouldn't write data to resistances.pickle. Couldn't save calibration data."
			print message.split("\n")[-1]
			return {"success":False,"message":message}
		else:
			message = message + "\nCalibration completed and saved for Ardustat #"+str(id)
			print message.split("\n")[-1]
			return {"success":True,"message":message}
		f.close()

	def setVoltageDifference(self,potential):
		setting = str(int(1023*(potential/5.0))).rjust(4,"0")
		self.rawwrite("g"+setting)

	def galvanostat(self,current,id=None): #This takes a specified current as input and calculates the right resistor setting and voltage difference to set it. See http://steingart.ccny.cuny.edu/ardustat-theory
		message = ""
		if id == None:
			message = message + "\nWarning: No ID # passed to this function!"
			print message.split("\n")[-1]
		if current < 0 or current > 0.02:  #Current out of range
			message = message + "\nCurrent "+str(current)+" out of range (0-0.02)."
			print message.split("\n")[-1]
			return {"success":False,"message":message}
		
		if current == 0:  #Current is zero; set voltage difference to 0 and resistance to max. If we use the normal method with an input of 0 it just throws a divide by 0 error
			self.ocv()
			time.sleep(0.3)
			self.rawwrite("r0255")
			message = message + "\nSuccessfully set galvanostat. Set voltage differance as 0 and resistance as "+str(self.resbasis(255,id)["resistance"])+"."
			print message.split("\n")[-1]
			return {"success":True,"message":message}
		
		else:
			parseddict = self.parse(self.rawread(),id)
			if parseddict["success"] != False: #If parsing the data was successful
				if current > 0.001:
					voltagedifference = current * 1000 #1 milliamp corresponds to 1V, 1 microamp corresponds to 1 millivolt, etc
				else:
					voltagedifference = current * 10000
				minvoltagedifference = 0.00489 #DAC has 4.89-millivolt resolution
				maxvoltagedifference = 5 - parseddict["cell_ADC"]
				if voltagedifference < minvoltagedifference: voltagedifference = minvoltagedifference
				if voltagedifference > maxvoltagedifference: voltagedifference = maxvoltagedifference
				resistancevalue = voltagedifference / current
				minresistance = self.resbasis(0,id)["resistance"]
				maxresistance = self.resbasis(255,id)["resistance"]
				while resistancevalue < minresistance: #If resistor can't go that low for that voltage setting...
					voltagedifference = voltagedifference + 0.00489 #Tick DAC up a setting
					if voltagedifference < maxvoltagedifference:
						resistancevalue = voltagedifference / current #Recalculate resistor setting
					else: #Voltage is maxed out and resistor still can't go low enough to source current...
						message = message + "\nYou connected a "+str(parseddict["cell_ADC"])+" cell. Max current for that cell is "+str(maxvoltagedifference/minresistance)+" A. Cannot set current as "+str(current)+" A."
						print message.split("\n")[-1]
						return {"success":False,"message":message}
				
				if resistancevalue > maxresistance: #If resistor can't go that high for that voltage setting...
					resistancevalue = maxresistance
					voltagedifference = resistancevalue * current #Recalculate voltage difference
					if voltagedifference < minvoltagedifference: #Voltage difference is so low at max resistance that the closest DAC setting is 0.
						message = message + "\nYour current is lower than the maximum resistance of the potentiometer * the minimum voltage difference of the DAC."
						print message.split("\n")[-1]
						return {"success":False,"message":message}
				#If we are at this point, then we find the resistor setting that corresponds to the resistance value
				resistanceresult = self.setResistance(resistancevalue, id)
				time.sleep(0.3)
				self.setVoltageDifference(voltagedifference)
				message = message + "\nSuccessfully set galvanostat. Set voltage difference to "+str(voltagedifference)+" V. Set resistance to "+str(resistanceresult["setting"])+" Ohm."
				print message.split("\n")[-1]
				return {"success":True,"message":message}
			else:	#Issue parsing data
				message = message + "\nError parsing data! Galvanostat not set."
				print message.split("\n")[-1]
				return {"success":False,"message":message}
	
	def logappend(self,filename="ardustatlog",id=False):
		try:
			rawdatafile = open(filename+".csv","a")
		except: #File does not exist
			rawdatafile = open(filename+".csv","w") #Make new empty file
			rawdatafile.close()
			rawdatafile = open(filename+".csv","a")
		try:
			jsondatafile = open(filename+".jsondata","a")
		except: #File does not exist
			jsondatafile = open(filename+".jsondata","w") #Make new empty file
			jsondatafile.close()
			jsondatafile = open(filename+".jsondata","a")
		thedata = self.rawread()
		rawdatafile.write(thedata+"\n")
		parsedict = self.parse(thedata,id)
		if parsedict["success"] == True:
			jsondatafile.write(str(json.dumps(parsedict))+"\r\n")
		rawdatafile.close()
		jsondatafile.close()

	
	def plotdata(self,filename, yaxis, xaxis="thetime"):
		f = open(filename,"r")
		data = f.readlines()
		f.close()
		thetime = []
		ref = []
		DAC0_setting = []
		DAC0_ADC = []
		cell_ADC = []
		pot_step = []
		resistance = []
		GND = []
		cell_resistance = []
		current = []
		for i in range(len(data)):
			data[i] = json.loads(data[i].replace("\n","").replace("\r",""))
			thetime.append(data[i]['time'])
			ref.append(data[i]['ref'])
			DAC0_setting.append(data[i]['DAC0_setting'])
			DAC0_ADC.append(data[i]['DAC0_ADC'])
			cell_ADC.append(data[i]['cell_ADC'])
			pot_step.append(data[i]['pot_step'])
			resistance.append(data[i]['resistance'])
			GND.append(data[i]['GND'])
			cell_resistance.append(data[i]['cell_resistance'])
			current.append(data[i]['current'])
		thedict = {"thetime":thetime,"ref":ref,"DAC0_setting":DAC0_setting,"DAC0_ADC":DAC0_ADC,"cell_ADC":cell_ADC,"pot_step":pot_step,"resistance":resistance,"GND":GND,"cell_resistance":cell_resistance,"current":current}
		matplotlib.pyplot.plot(thedict[xaxis],thedict[yaxis])
		matplotlib.pyplot.savefig("image.png")
