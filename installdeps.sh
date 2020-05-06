#!/usr/local/bin/bash
#
# Assumes python 3 is on PATH
# Assumes you are in a virtual environment
#
clear
pip3 list > /dev/null 2>&1
STATUS=$?

if [[ ${STATUS} -eq 0 ]] ; then
    echo "in virtual environment"
    pip3 install --upgrade pip
    pip3 install wheel
    pip3 install matplotlib
    pip3 install networkx
    pip3 install pulp
    pip3 install twine
else
    echo "You are not in a virtual environment"

fi
