#!/bin/bash
set -eux
virtualenv env
./env/bin/pip install requests
./env/bin/python setup.py develop
