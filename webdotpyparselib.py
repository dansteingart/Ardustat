#If the user sends variables to a web.py function, e.g. sets "input" to AB-CD and "filename" to "new file", web.py will send them as "input=AB%2DCD&filename=new+file". Webdataintoascii wil convert that to "input=AB-CD&filename=new file" and webdataintodict will convert it into a python dictionary {"input":"AB-CD","filename":"new file"}.

def webdataintoascii(data):
	data = data.replace("+"," ")
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
