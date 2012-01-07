import ardustat_library_simple as ard
from time import sleep
a = ard.ardustat()
print "foo"
a.connect()
a.load_resistance_table(16)
sleep(2)
a.blink()
print "foo"
print a.parsedread()