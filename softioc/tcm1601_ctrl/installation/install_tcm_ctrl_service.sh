#!/bin/bash

# systemctl service name
# we assume the filename will in the form of <sys>_ctrl_service etc
sys=tcm1601

# soft IOC python script name incl .py
pythonscript=${sys}_ctrl_service.py

echo " "
echo "installing the service file:"
echo " $ sudo cp ../systemd/${sys}_ctrl_service.service /etc/systemd/system/"
sudo cp ../systemd/${sys}_ctrl_service.service /etc/systemd/system/

# need to check if directory exists
echo " "
echo "if not exists, make directory"
echo " $ sudo mkdir /usr/local/lib/${sys}_ctrl_service"
if [[ ! -d "/usr/local/lib/${sys}_ctrl_service" ]]
then
    sudo mkdir /usr/local/lib/${sys}_ctrl_service
fi

if [[ -d "/usr/local/lib/${sys}_ctrl_service"]]
then
    echo " "
    echo "installing the python script in /usr/local/lib/${sys}_ctrl_service"
    echo " $ sudo cp ../python/*.py /usr/local/lib/${sys}_ctrl_service/"
    sudo cp ../python/*.py /usr/local/lib/${sys}_ctrl_service/
fi

echo " "
echo " to enable the service execute: "
echo " $ sudo systemctl enable ${sys}_ctrl_service.service"
echo " "
echo "to star the srcive, execute:"
echo " $ sudo systemctl start ${sys}_ctrl_service.service"
echo " "
echo "to check the status, execute:"
echo " $ sudo systemctl status ${sys}_ctrl_service.service"