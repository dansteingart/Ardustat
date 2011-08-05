import ardustatlibrary, sys

if len(sys.argv) == 4:
	filename = sys.argv[1]
	port = int(sys.argv[2])
	id = int(sys.argv[3])
	ardustatlibrary.log(filename,port,id)
