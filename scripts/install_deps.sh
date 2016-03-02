#!/bin/bash
set -x

if ! [ -x "$(command -v virtualenv)" ]; then
    sudo apt-get install -y python-virtualenv
fi

if [ ! -d venv ]; then
    virtualenv -p /usr/bin/python2.7 venv
fi
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
