#!/bin/bash
set -x

if ! [ -x "$(command -v virtualenv)" ]; then
    sudo apt-get install -y python-virtualenv
fi

if [ ! -d cwr_venv ]; then
    virtualenv -p /usr/bin/python2.7 cwr_venv
fi
. cwr_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
