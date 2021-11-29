#
#!/usr/bin/env python3
#
# need to install the Adafruit CircuitPython libraries, see
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
#
# Follow the step to run the raspi-blinka.py script. The user need to be granted
# access tot eh hardware on the RPI, by adding it to the groups.
# sudo adduser controls i2c
# sudo adduser controls spi
#
# install
# - adafruit_Max31865
# $ sudo pip3 install adafruit-circuitpython-max31865

# - adafruit_htu21d
# $ sudo pip3 install adafruit-circuitpython-htu21d

# - adafruit_lps35hw
# $ sudo pip3 install adafruit-circuitpython-lps35hw

# Setting up DS18B20 Sensor ID
# in /boot/config.txt, need to set
# dtoverlay=w1-gpio
#
# # can be done by enabling 1-wire sensors with
# $ sudo raspi-config
#
# Sensor ID can be found in cd /sys/bus/w1/devices
# each sensor has a hardcoded ID
# something like '28-3c01b5567120'
#
# $ cd 28-3c01b5567120
# $ cat w1_slave
# 3c 01 55 05 7f a5 81 66 4b : crc=4b YES
# 3c 01 55 05 7f a5 81 66 4b t=19750
#
# # The number that follows t= is the temperature
# in micro degree celcius (10^-3).
# air_temp1_id = '28-3c01b5567120'

# Author: Perry W. F. Forsyth
# Date: 2021-07-07
# Contact: Perry.Forsyth@anu.edu.au
#
# New version based on pcaspy, all python based EPICS server
# Bram Slagmolen

# Version
major = '1'
minor = '2'
patch= 'c'
version = major + '.' + minor + patch


print('---- Running torpedo_env_ctrl_ss ----')

# Recording enviromental data using Adafruit sensors
import numpy as np
import datetime
import threading
import time
import systemd.daemon
import urllib.request
import json

import board
import busio
import digitalio
import adafruit_max31865
import adafruit_lps35hw
import DS18B20 as DS

from adafruit_htu21d import HTU21D
from time import sleep
from pcaspy import Driver, SimpleServer
#from epics import caput

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

# Setting up DS18B20 Sensor ID
# ls /sys/bus/w1/devices
air_temp1_id = '28-00000d7a2801' # - 1
air_temp2_id = '28-00000da0b4ab' # - 2
air_temp3_id = '28-00000d9ff9d0' # - 3
air_temp4_id = '28-00000da04ca6' # - 4
air_temp5_id = '28-00000d7968e2' # - 5

sensorPin = 4 # can be other

# Running Code
global jsonAir
jsonAir = {}

# Set time internval [s] for extracting
# data from the Purple Air partical counter
purpleairInterval = 10

# Set up the json dict
jsonAir["pressure"] = 0
jsonAir["current_dewpoint_f"] = 0
jsonAir["current_humidity"] = 0
jsonAir["current_temp_f"] = 0
jsonAir["pm10_0_atm"] = 0
jsonAir["pm10_0_atm_b"] = 0
jsonAir["pm2_5_atm"] = 0
jsonAir["pm2_5_atm_b"] = 0
jsonAir["pm1_0_atm"] = 0
jsonAir["pm1_0_atm_b"] = 0

# Previous EPICS Channels
#ChannelNames = [\
#    "N1:ENV-PT1000_TEMP_INMON",\
#    "N1:ENV-HUMIDITY_INMON",\
#    "N1:ENV-PRESSURE_INMON",\
#    "N1:ENV-HTU210F_TEMP_INMON"\
#    ]

IFO = 'N1'
SYSTEM = 'PEM'
SUBSYS = 'LAB'

#envPrefix = IFO + ':' + SYSTEM + '-'
envPrefix = IFO + ':'

envDB = {
    'PEM-LAB_PT1000_TEMP_C'             : { 'prec' : 2 },
    'PEM-LAB_HUMIDITY'                  : { 'prec' : 2 },
    'PEM-LAB_PRESSURE_MBAR'             : { 'prec' : 2 },
    'PEM-LAB_HTU210F_TEMP_C'            : { 'prec' : 2 },
    'PEM-LAB_PURPLEAIR_TEMP_C'          : { 'prec' : 2 },
    'PEM-LAB_PURPLEAIR_HUMIDITY'        : { 'prec' : 2 },
    'PEM-LAB_PURPLEAIR_DEWPOINT_C'      : { 'prec' : 2 },
    'PEM-LAB_PURPLEAIR_PRESSURE_MBAR'   : { 'prec' : 2 },
    'PEM-LAB_PURPLEAIR_PM_1_0'          : { 'prec' : 2 },
    'PEM-LAB_PURPLEAIR_PM_2_5'          : { 'prec' : 2 },
    'PEM-LAB_PURPLEAIR_PM_10'           : { 'prec' : 2 },
    'PEM-LAB_PURPLEAIR_INTERVAL_S'      : { 'prec' : 2 },
    'PEM-LAB_AIR_A_TEMP_C'              : { 'prec' : 2,
                                            'scan' : 15},
    'ENV-PT1000_TEMP_INMON'             : { 'prec' : 2 },
    'ENV-HUMIDITY_INMON'                : { 'prec' : 2 },
    'ENV-PRESSURE_INMON'                : { 'prec' : 2 },
    'ENV-HTU210F_TEMP_INMON'            : { 'prec' : 2 },
    'TORPEDO_ENV_CTRL_VERSION'          : { 'type' : 'string' }
}

edc_iniFile = 'torpedo_env_ctrl_edc_daqd_ini_content.txt'
system_dir_name = 'torpedo_env_ctrl'
script_name = 'torpedo_env_ctrl_ss.py'


def generate_ini_file():
    '''Generate the .INI file content'''

    now = datetime.datetime.now()
    edc_Path = '/opt/rtcds/anu/n1/softioc/' + system_dir_name + '/ini/'
    # edc_iniFile = 'torpedo_env_ctrl_edc_daqd_ini_content.txt'
    
    edc_file = open( edc_Path + edc_iniFile , "w")
    edc_file.writelines(["# Auto generated file by " + script_name + "\n",
                         "# at " + now.strftime("%Y-%m-%d %H:%M:%S") + "\n",
                         "#\n"
                         "# Using the default parameters\n",
                         "[default]\n", 
                         "gain=1.00\n", 
                         "acquire=3\n", 
                         "dcuid=52\n", 
                         "ifoid=0\n", 
                         "datatype=4\n",
                         "datarate=16\n",
                         "offset=0\n",
                         "slope=1.0\n",
                         "units=undef\n",
                         "#\n",
                         "#\n",
                         "# Following content lines to be manually added to the\n",
                         "# edc.ini file, which points to /opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini\n",
                         "# Then the standalone_edc service (rts-edc.service on n1fe1) and the daqd\n",
                         "# service (rts-daqd.service on the n1fb10) will need to be restarted to\n",
                         "# the changes into effect.\n",
                         "#\n"])

    for key in envDB.keys():
        edc_file.writelines("[" + envPrefix + key + "]\n")

    edc_file.writelines(["#\n",
                         "# Legacy channels from the initial EPICs softIoc implementattion\n",
                         "# are listed below. These channels are copies if the channels listed above\n",
                         "#\n"
                         "# The EPICS softIoc service is managed by the systemd softEnvIOC.service\n",
                         "# When ready this service can be removed, and these channels deleted.\n", 
                         "#\n"])

    # for k in range(len(ChannelNames)):
    #     edc_f.writelines("[" + ChannelNames[k] + "]\n")

    edc_file.close()


class RepeatedTimer(object):
    '''Timer setup'''
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class myEnvDriver (Driver):
    def  __init__(self):
        super(myEnvDriver, self).__init__()

    def get_temperature(self):
        temp = TempSensor.temperature
        DS.pinsStartConversion([sensorPin])
        air_temp1 = DS.read(False, sensorPin, air_temp1_id)
        #caput(ChannelNames[0]+'.VAL', temp)
        self.setParam('ENV-PT1000_TEMP_INMON', temp)
        self.setParam('PEM-LAB_PT1000_TEMP_C', temp)
        self.setParam('PEM-LAB_AIR_TEMP_C', air_temp1)

    def get_humidity(self):
        humidity = HumSensor.relative_humidity
        #caput(ChannelNames[1]+'.VAL', humidity)
        self.setParam('ENV-HUMIDITY_INMON', humidity)
        self.setParam('PEM-LAB_HUMIDITY', humidity)

    def get_pressure(self):
        pressure1 = PresSensor.pressure
        #caput(ChannelNames[2]+'.VAL', pressure1)
        self.setParam('ENV-PRESSURE_INMON', pressure1)
        self.setParam('PEM-LAB_PRESSURE_MBAR', pressure1)

    def get_temperature_2(self):
        temp2 = HumSensor.temperature
        #caput(ChannelNames[3]+'.VAL', temp2)
        self.setParam('ENV-HTU210F_TEMP_INMON', temp2)
        self.setParam('PEM-LAB_HTU210F_TEMP_C', temp2)

    def get_pm1_air(self):
        pm1_a = jsonAir["pm1_0_atm"]
        pm1_b = jsonAir["pm1_0_atm_b"]
        pm1 = (pm1_a + pm1_b) / 2.0
        self.setParam('PEM-LAB_PURPLEAIR_PM_1_0', pm1)

    def get_pm25_air(self):
        pm25_a = jsonAir["pm2_5_atm"]
        pm25_b = jsonAir["pm2_5_atm_b"]
        pm25 = (pm25_a + pm25_b) / 2.0
        self.setParam('PEM-LAB_PURPLEAIR_PM_2_5', pm25)

    def get_pm10_air(self):
        pm10_a = jsonAir["pm10_0_atm"]
        pm10_b = jsonAir["pm10_0_atm_b"]
        pm10 = (pm10_a + pm10_b) / 2.0
        self.setParam('PEM-LAB_PURPLEAIR_PM_10', pm10)

    def get_temp_air(self):
        temp_f = jsonAir["current_temp_f"]
        temp_c = (temp_f - 32) / 1.8
        self.setParam('PEM-LAB_PURPLEAIR_TEMP_C', temp_c)

    def get_humidity_air(self):
        hum = jsonAir["current_humidity"]
        self.setParam('PEM-LAB_PURPLEAIR_HUMIDITY', float(hum))

    def get_dewpoint_air(self):
        dewpoint_f = jsonAir["current_dewpoint_f"]
        dewpoint_c = (dewpoint_f - 32)  / 1.8
        self.setParam('PEM-LAB_PURPLEAIR_DEWPOINT_C', dewpoint_c)

    def get_pressure_air(self):
        press = jsonAir["pressure"]
        self.setParam('PEM-LAB_PURPLEAIR_PRESSURE_MBAR', float(press))

    def set_version(self):
        self.setParam('TORPEDO_ENV_CTRL_VERSION', version)

    def set_purpleair_interval(self):
        self.setParam('PEM-LAB_PURPLEAIR_INTERVAL_S', purpleairInterval)


def get_purpleair_data(url):
    # url = "http://192.168.30.231/json"
    operUrl = urllib.request.urlopen(url)
    if(operUrl.getcode()==200):
        data = operUrl.read()
        global jsonAir
        jsonAir = json.loads(data)
    else:
        print("Error receiving purpleair data", operUrl.getcode())
    #return jsonData

if __name__ == '__main__':

    # Operate Continously
    print('---- generate .ini file content in  ----')
    print('---- ' + edc_iniFile + ' ----')
    generate_ini_file()
    
    # Start and set up 
    # updates jsanAir every 1 s
    print('---- start purpleair json pull ----')
    rt = RepeatedTimer(purpleairInterval, get_purpleair_data, "http://192.168.30.231/json")
    sleep(2)
    # print(jsonAir)

    # Start simple CA Server
    envServer = SimpleServer()
    envServer.createPV(envPrefix, envDB)
    envDriver = myEnvDriver()

    # Tell systemd that our service is ready
    systemd.daemon.notify('READY=1')

    envDriver.set_version()
    envDriver.set_purpleair_interval()
    envDriver.updatePVs()

    while True:
        envServer.process(1)

        envDriver.get_humidity()
        envDriver.get_pressure()
        envDriver.get_temperature()
        envDriver.get_temperature_2()

        envDriver.get_pressure_air()
        envDriver.get_dewpoint_air()
        envDriver.get_humidity_air()
        envDriver.get_temp_air()
        envDriver.get_pm1_air()
        envDriver.get_pm25_air()
        envDriver.get_pm10_air()

        # Update content of the PVs
        envDriver.updatePVs()



