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


# Author: Perry W. F. Forsyth
# Date: 2021-07-07
# Contact: Perry.Forsyth@anu.edu.au
#
# Bram Slagmolen - v2.0a

# torpedo_env_ctrl
major = '2'
minor = '0'
patch = 'd'
verion = major + '.' + minor + patch

print('---- Running torpedo_env_ctrl_ioc ----')

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

from adafruit_htu21d import HTU21D
from time import sleep
from epics import caget, caput, cainfo

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
global jsonAir
jsonAir = {}

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
SYSTEM = 'ENV'
SUBSYS = 'LAB_'

envPrefix = IFO + ':' + SYSTEM + '-' + SUBSYS

# Channels are already served by 
# the IOC Server
envDB = [\
    'PT1000_TEMP_C',\
    'HUMIDITY',\
    'PRESSURE_MBAR',\
    'HTU210F_TEMP_C',\
    'PURPLEAIR_TEMP_C',\
    'PURPLEAIR_HUMIDITY',\
    'PURPLEAIR_DEWPOINT_C',\
    'PURPLEAIR_PRESSURE_MBAR',\
    'PURPLEAIR_PM_1_0',\
    'PURPLEAIR_PM_2_5',\
    'PURPLEAIR_PM_10',\
]

def generate_ini_file():
    now = datetime.datetime.now()
    cdsPath = '/opt/rtcds/anu/n1/softioc/torpedo_env_ctrl/ini/'
    iniFile = 'torpedo_env_ctrl_ioc.ini'
    f = open( cdsPath+iniFile , "w")
    f.writelines(["# Auto generated file by torpedo_env_ctrl_ioc.py\n",
                  "# at " + now.strftime("%Y-%m-%d %H:%M:%S") + "\n",
                  "#\n"
                  "# Default parameters\n",
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
                  "\n"])
    
    for k in range(len(envDB)):
        f.writelines("[" + envPrefix + envDB[k] + "]\n")

    f.close()

def generate_ioc_db():
    now = datetime.datetime.now()
    cdsPath = '/opt/rtcds/anu/n1/softioc/torpedo_env_ctrl/ioc/'
    dbFile = 'TORPEDO_ENV_CTRL_IOC.db'
    f = open( cdsPath + dbFile , "w")
    f.writelines(['# Auto generated file by torpedo_env_ctrl_ioc.py\n',
                  '# at ' + now.strftime('%Y-%m-%d %H:%M:%S') + '\n',
                  '#\n'
                  '# Default parameters\n',
                  '\n'])

    for k in range(len(envDB)):
        f.writelines(['record(ai, "' + envPrefix + envDB[k] + '")\n',
                      '{\n',
                      '    field(SCAN, ".1 second")\n',
                      '    field(PREC, "2")\n'
                      '}\n'])
    f.close()


class RepeatedTimer(object):
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



class myEnvDriver:
    def  __init__(self):
        super(myEnvDriver, self).__init__()

    def get_temperature(self):
        value = TempSensor.temperature
        indx = envDB.index('PT1000_TEMP_C')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_humidity(self):
        value = HumSensor.relative_humidity
        indx = envDB.index('HUMIDITY')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_pressure(self):
        value = PresSensor.pressure
        indx = envDB.index('PRESSURE_MBAR')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_temperature_2(self):
        value = HumSensor.temperature
        indx = envDB.index('HTU210F_TEMP_C')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_pm1_air(self):
        pm1_a = jsonAir["pm1_0_atm"]
        pm1_b = jsonAir["pm1_0_atm_b"]
        value = (pm1_a + pm1_b) / 2.0
        indx = envDB.index('PURPLEAIR_PM_1_0')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_pm25_air(self):
        pm25_a = jsonAir["pm2_5_atm"]
        pm25_b = jsonAir["pm2_5_atm_b"]
        value = (pm25_a + pm25_b) / 2.0
        indx = envDB.index('PURPLEAIR_PM_2_5')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_pm10_air(self):
        pm10_a = jsonAir["pm10_0_atm"]
        pm10_b = jsonAir["pm10_0_atm_b"]
        value = (pm10_a + pm10_b) / 2.0
        indx = envDB.index('PURPLEAIR_PM_10')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_temp_air(self):
        temp_f = jsonAir["current_temp_f"]
        value = (temp_f - 32) / 1.8
        indx = envDB.index('PURPLEAIR_TEMP_C')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_humidity_air(self):
        value = jsonAir["current_humidity"]
        indx = envDB.index('PURPLEAIR_HUMIDITY')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_dewpoint_air(self):
        dewpoint_f = jsonAir["current_dewpoint_f"]
        value = (dewpoint_f - 32)  / 1.8
        indx = envDB.index('PURPLEAIR_DEWPOINT_C')
        caput(envPrefix + envDB[indx] + '.VAL', value)

    def get_pressure_air(self):
        value = jsonAir["pressure"]
        indx = envDB.index('PURPLEAIR_PRESSURE_MBAR')
        caput(envPrefix + envDB[indx] + '.VAL', value)



if __name__ == '__main__':

    # Operate Continously
    print('---- generate .ini file ----')
    generate_ini_file()
    
    generate_ioc_db()

    # Start and set up 
    # updates jsanAir every 1 s
    print('---- start purpleair json pull ----')
    rt = RepeatedTimer(1, get_purpleair_data, "http://192.168.30.231/json")
    sleep(2)
    # print(jsonAir)

    # Start simple CA Server
    #envServer = SimpleServer()
    #envServer.createPV(envPrefix, envDB)
    envDriver = myEnvDriver()

    # Tell systemd that our service is ready
    systemd.daemon.notify('READY=1')

    while True:
        #envServer.process(0.1)

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

