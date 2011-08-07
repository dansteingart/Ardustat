import ardustat_library_simple as ard

a = ard.ardustat()
a.connect(7777)
foo = a.calibrate(9974,16)

for f in foo:
	print f,foo[f]