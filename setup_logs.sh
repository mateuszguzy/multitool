#!/bin/bash

MODULES=$(grep -o "MODULES = \[\(.*\)\]" config/settings.py | cut -d "[" -f2 | cut -d "]" -f1 | tr -d " '")

current_date=$(date +'%Y%m%d')

for module in ${MODULES//,/ }; do
    module=$(echo "$module" | tr -d '"' | tr '[:upper:]' '[:lower:]')
    filename="${current_date}_${module}"
    touch "./logs/$filename.log" &>/dev/null
    # show every change in modules log files in console
    # to be changed when results showing based on user input will be implemented
    tail -n0 -f "./logs/$filename.log" &
done