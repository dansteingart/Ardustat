import ardustat_library_simple as ard
a=ard.ardustat()
a.connect(7777)
a.calibrate(15082,16) #change the first argument to this function based on the measured resistance
