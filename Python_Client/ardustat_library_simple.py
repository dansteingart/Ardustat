import serial 
import socket
import glob
from time import sleep,time

class ardustat:
	def __init__(self):	
		self.port = ""
		self.ser = serial.Serial()
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.mode = "socket"

	def findPorts(self):
		"""A commands to find possible ardustat ports with no Arguments, """
		return glob.glob("/dev/tty.u*")

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
		sleep(.01)
		if self.mode == "serial":
			return self.ser.readlines()
		if self.mode == "socket":
			a = ""
			while 1:
				a += self.s.recv(1024)
				if a.find("ST\r\n") > 1: return a.strip()

	
	def parsedread(self):
		return self.parseline(self.rawread())
		
	def last_raw_reading(self):
		out = ""
		while self.ser.inWaiting() > 0: out = self.ser.readline()
		return out
	
	def refbasis(self,reading,ref):
		"""returns an absolute potential based on the ADC reading against the 2.5 V reference
		   (reading from pot as a value between 0 and 1023, reference value in V (e.g. 2.5))"""
		return round((float(reading)/float(ref))*2.5,3)
	
	def resbasis(self,reading,pot):
		"""returns the value for the givening potentiometer setting 
			(reading as value between 0 and 255, pot lookup variable)"""
		return round(10+(float(reading)/255.0)*pot,2)
		
	def parseline(self,reading):
		outdict = {}
		#format GO,1023,88,88,255,0,1,-0000,0,0,510,ST 
			#splitline[0] -> "GO"
			#splitline[1] -> DAC Setting
			#splitline[2] -> Cell Voltage
			#splitline[3] -> DAC Measurement
			#splitline[4] -> DVR Setting
			#splitline[5] -> "setout" variable in firmware. Don't know what this represents
			#splitline[6] -> Mode (0 = manual, 1 = OCV, 2 = potentiostat, 3 = galvanostat)
			#splitline[7] -> Last command received
			#splitline[8] -> GND Measurement
			#splitline[9] -> Reference Electrode
			#splitline[10] -> Reference Voltage
			#splitline[11] -> "ST"
		if reading.find("GO") == 0 and reading.find("ST") and reading.rfind("GO") == 0:
			outdict['valid'] = True
			outdict['raw'] = reading
			outdict['time'] = time()
			parts = reading.split(",")
			outdict['ref'] = float(parts[len(parts)-2])
			outdict['DAC0_ADC'] = self.refbasis(parts[3],outdict['ref'])
			outdict['cell_ADC'] = self.refbasis(parts[2],outdict['ref'])
			outdict['pot_step'] = parts[4]
			outdict['res'] = self.resbasis(outdict['pot_step'],10000.0)
			outdict['current'] = (float(outdict['DAC0_ADC'])-float(outdict['cell_ADC']))/outdict['res']			
		else:
			outdict['valid'] = False
		return outdict
			