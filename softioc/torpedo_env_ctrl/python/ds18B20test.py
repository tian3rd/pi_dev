#
# #!/usr/bin/env python3

import time
import os.path
import DS18B20 as DS
from os import path

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
# We got 5 DS18B20 sensors (for now:)
# otherwise the order is as per $ ls -al /sys/bus/w1/devices/
# 28-00000d7a2801 - 1
# 28-00000da0b4ab - 2
# 28-00000d9ff9d0 - 3
# 28-00000da04ca6 - 4
# 28-00000d7968e2 - 5
#
# $ cd 28-3c01b5567120
# $ cat w1_slave
# 3c 01 55 05 7f a5 81 66 4b : crc=4b YES
# 3c 01 55 05 7f a5 81 66 4b t=19750
#
# To change resolution
# 9 bit (90 ms): 0.5 deg C
# 10 bit (190 ms): 0.25 deg C
# 11 bit (375 ms): 0.125 deg C
# 12 bit (750 ms): 0.0625 deg C
# $ cd /sys/bus/w1/devices/28-*
# $ sudo su
# # echo 11 > resolution
# # cat resolution
#
# To make it permanent (after reboot)
# # echo save > eeprom
#
# For faster readout see to install the BitBangingDS18B20 code at
# github https://github.com/danjperron/BitBangingDS18B20 and follow
# its instructions (especially the Python Add-on, need to do python3 only).
# This will install the DS18B20 module
#
# # The number that follows t= is the temperature
# in micro degree celcius (10^-3).
air_temp1_id = '28-00000d7a2801' # - 1
air_temp2_id = '28-00000da0b4ab' # - 2
air_temp3_id = '28-00000d9ff9d0' # - 3
air_temp4_id = '28-00000da04ca6' # - 4
air_temp5_id = '28-00000d7968e2' # - 5

sensorPin = 4

def get_ds18b20_data(sensor_id):
    '''Extract the data from the DS18B20'''
    f = open("/sys/bus/w1/devices/" + sensor_id + "/w1_slave","r")
    contents = f.readlines()
    f.close()
    return contents

def get_ds18b20_temp(sensor_id):
    contents = get_ds18b20_data(sensor_id)
    while contents[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        contents = get_ds18b20_data(sensor_id)
    index = contents[1].find('t=')
    if index != -1:
        temperature = contents[1][index+2:]
        return float(temperature)/1000.0

if __name__ =="__main__":


    while True:
        #temp = get_ds18b20_temp(air_temp1_id)
        # print('S1: ' + str(get_ds18b20_temp(air_temp1_id)) +
        #       ', S2: ' + str(get_ds18b20_temp(air_temp2_id)) +
        #       ', S4: ' + str(get_ds18b20_temp(air_temp4_id)) +
        #       ', S5: ' + str(get_ds18b20_temp(air_temp5_id)))
        DS.pinsStartConversion([sensorPin])
        temp1 = DS.read(False, sensorPin, air_temp1_id)
        temp2 = DS.read(False, sensorPin, air_temp2_id)
        temp4 = DS.read(False, sensorPin, air_temp4_id)
        temp5 = DS.read(False, sensorPin, air_temp5_id)
        print('S1: ' + str(temp1) + ', S2: ' + str(temp2) + ', S4: ' + str(temp4) + ', S5: ' + str(temp5))
        #time.sleep(0.75)

