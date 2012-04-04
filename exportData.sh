#!/bin/bash

echo -e "Input name of file:"

read file_name

mongoexport -csv -o CSVfiles/$file_name.csv -d ardustat -c $file_name -f time,cell_potential,working_potential,current

