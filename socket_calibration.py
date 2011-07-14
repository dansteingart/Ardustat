from simpardlibnet import ardustat as ard
from time import sleep,time

a = ard()

a.connect(7777)

a.calibrate(9970,14)

