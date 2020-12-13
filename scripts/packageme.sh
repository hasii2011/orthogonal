#!/usr/local/bin/bash

function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot

clear

./cleanup.sh
python3 setup.py sdist bdist_wheel

# Check package
twine check dist/*
