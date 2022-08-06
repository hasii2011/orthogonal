#!/usr/bin/env bash

function changeToProjectRoot {

    areHere=$(basename "${PWD}")
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot

clear

./scripts/cleanup.sh
python -m build --sdist --wheel

# Check package
twine check dist/*
