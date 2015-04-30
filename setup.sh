#!/bin/bash
set -eux
virtualenv env
./env/bin/pip install -r requirements.txt 
./env/bin/python setup.py develop
