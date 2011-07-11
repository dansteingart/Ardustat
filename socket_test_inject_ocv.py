from simpardlibnet import ardustat as ard
from time import sleep
a = ard()

a.connect(7777)
a.ocv()
sleep(.1)
print a.rawread()