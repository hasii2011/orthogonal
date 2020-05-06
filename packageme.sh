#!/usr/local/bin/bash

clear

./cleanup.sh
python3 setup.py sdist bdist_wheel

# Check package
twine check dist/*
