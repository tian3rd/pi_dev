#!/usr/bin/env python
# Main_Envirodata_ProcessStart_V1
# Author: Perry W. F. Forsyth
# Date: 2021-07-07
# Contact: Perry.Forsyth@anu.edu.au

# Version Date: 2021-07-07
# Version Number: 1.0.0
print('---- Running Main_Envirodata_ProcessStart_V1 ----')
#print('---- Loading Packages ----')
#import sys
#sys.path.append( \
# '/opt/projects/epics/pyext/pcaspy/lib64/python2.7\
#/site-packages/pcaspy-0.7.0-py2.7-linux-x86_64.egg')
#sys.path.append( \
# '/opt/projects/epics/pyext/pyepics/lib64/python2.7/\
#site-packages/pyepics-3.2.7-py2.7.egg')
#sys.path.append( \
#     '/opt/projects/epics/pyext/pcaspy/lib64/python2.7/\
#site-packages')
#sys.path.append( \
#     '/opt/projects/epics/pyext/pyepics/lib64/python2.7/\
#site-packages')

# Recording enviromental data using Adafruit sensors
import epics
import numpy as np
import systemd.daemon
import board
import busio
import digitalio
import adafruit_max31865
from adafruit_htu21d import HTU21D
import adafruit_lps35hw

# MAX31865 PT1000 sensor setup
spi = board.SPI() # Connected on SPI port
cs = digitalio.DigitalInOut(board.D22)  # Chip select of the MAX31865 board.
TempSensor = adafruit_max31865.MAX31865(spi, cs, wires=3,
                                    rtd_nominal=1000.0, ref_resistor=4300)

# Connecting Humnidity Sensor
i2c = busio.I2C(board.SCL,board.SDA) # Start up I2C
HumSensor = HTU21D(i2c)

# Connect Pressure Sensor
PresSensor = adafruit_lps35hw.LPS35HW(i2c)

# Running Code
ChannelNames = [\
    "N1:ENV-PT1000_TEMP_INMON",\
    "N1:ENV-HUMIDITY_INMON",\
    "N1:ENV-PRESSURE_INMON",\
    "N1:ENV-HTU210F_TEMP_INMON"\
    ]

def generate_ini_file():
    now = datetime.datetime.now()
    cdsPath = '/opt/rtcds/anu/n1/softioc/torpedo_env_ctrl/ini/'
    iniFile = 'Main_Envirodata_ProcessStart_V1_ini_content.txt'
    f = open( cdsPath+iniFile , "w")
    f.writelines(["# Auto generated file by Main_Envirodata_ProcessStart_V1.py\n",
                  "# at " + now.strftime("%Y-%m-%d %H:%M:%S") + "\n",
                  "#\n"
                  "# Default parameters\n",
                  "\n"])
    
    for k in range(len(ChannelNames)):
        f.writelines("[" + ChannelNames[k] + "]\n")

    f.close()

# Write .ini file channel content
print('---- generate .ini file ----')
generate_ini_file()

# Tell systemd that our service is ready
systemd.daemon.notify('READY=1')

# Operate Continously
print('---- Running save to sensors to epics channels ----')
while True:
    # Get values from sensors
    temp = TempSensor.temperature
    humidity = HumSensor.relative_humidity
    pressure = PresSensor.pressure
    temp2 = HumSensor.temperature

    # Assigning values to epics channels
    epics.caput(ChannelNames[0],temp)
    epics.caput(ChannelNames[1],humidity)
    epics.caput(ChannelNames[2],pressure)
    epics.caput(ChannelNames[3],temp2)
