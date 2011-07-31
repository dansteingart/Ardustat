import ardustatlibrary as ard
import time
the_socket = 7777

connresult = ard.connecttosocket(the_socket)

print connresult

socketinstance = connresult["socket"]

print ard.ocv(the_socket)
print ard.socketread(socketinstance)
time.sleep(3)
print ard.potentiostat(2,the_socket)
print ard.socketread(socketinstance)
print ard.ocv(the_socket)
print ard.socketread(socketinstance)
time.sleep(3)
print ard.potentiostat(1,the_socket)
print ard.socketread(socketinstance)



