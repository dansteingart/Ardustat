import ardustat_library_simple as ard

a = ard.ardustat()
a.connect(7777)
a.load_resistance_table(16)

print a.res_table