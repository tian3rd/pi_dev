#!/bin/bash

cd /opt/rtcds/anu/a1/iocmodbus/a1slowpid
python3 CDS_PID.py --PIDfilt A1:ISC-LASER_D_TEMP --input A1:LSC-PDH_ERR_D_LF_NORM_MON --output A1:ISC-LASER_D_TEMP_PID_VOLT &> /dev/null
