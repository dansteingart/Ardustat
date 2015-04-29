#!/usr/bin/env python

print "python's resistance table called"
import pickle
import json
import sys
import os

cwd = os.getcwd()

res_dir = "resistance_tables/"

json_list = []
pickled_list = []

files = sorted(os.listdir(res_dir))


for name in files:
    if '.json' in name:
        json_list.append(name)
    elif '.p' in name:
        pickled_list.append(name)

id_list = []
for file in json_list:
    uscore_index = file.index('_') #index of the underscore
    fstop_index = file.index('.') #index of full stop
    number = file[uscore_index+1:fstop_index]
    id_list.append(number)
    
string = ''
for pickled in pickled_list:
    string += pickled
#print string

to_make_list = []
for number in id_list:
    #if number not in string:
    to_make_list.append(number)

for number in to_make_list:
    json_data = open(res_dir+'unit_'+number+'.json').read()[1:-1]
    #print json_data
    split_once = json_data.split(',')
    #print split_once
    split_twice = [] #is a list
    for i in split_once:
        split_twice.append(i.split(':'))
    #print split_twice
    res_numb = []
    res_val = []
    for i in split_twice:
        #res_numb.append( int(i[0][1:-1]) )
        res_val.append( float(i[1]) )
    to_pickle = {}
    for i in range(0, len(res_val)):
        to_pickle[i] = [res_val[i],0]
    print 'creating resistance table for ' , number
    
    #dump pickle to whatever I save things as
    pickle.dump( to_pickle, open(res_dir+'resistance_table_'+number+'.p' ,'wb'))