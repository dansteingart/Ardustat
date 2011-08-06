import ardustatlibrary as ard
import commands

the_socket = 7777
print commands.getoutput("./tcp_serial_redirect.py "+ard.findPorts()['ports'][0]+" 57600")


