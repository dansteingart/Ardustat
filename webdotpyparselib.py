def webdataintoascii(data):
	data.replace("+"," ")
	while data.find("%") != -1:
			char = int(data[data.find("%")+1:data.find("%")+3],16)
			char = chr(char) #  '%##' is the ascii character corresponding to the hex value ##
			data = data[:data.find("%")] + char + data[data.find("%")+3:] #Insert the character back into the input string
	return data

def webdataintodict(data):
	thedict = {}
	data = data.split("&")
	for i in data:
		thestr = i[:i.find("=")]
		thedict[thestr] = i[i.find("=")+1:]
	return thedict
