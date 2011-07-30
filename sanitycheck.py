import ardustatlibrary as ard
import time
the_socket = 7777

print ard.connecttosocket(the_socket)

print ard.ocv(the_socket)
print ard.socketread(ard.connecttosocket(the_socket)['socket'])
time.sleep(3)
print ard.potentiostat(2,the_socket)
print ard.socketread(ard.connecttosocket(the_socket)['socket'])
print ard.ocv(the_socket)
print ard.socketread(ard.connecttosocket(the_socket)['socket'])
time.sleep(3)
print ard.potentiostat(1,the_socket)
print ard.socketread(ard.connecttosocket(the_socket)['socket'])



