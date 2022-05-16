#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from datetime import datetime as dt
import systemd.daemon
from time import sleep
from pcaspy import Driver, SimpleServer
import threading


import arduino_mega
import importlib
importlib.reload(arduino_mega)

# Version
major = '0'
minor = '1'
patch = 'a'
version = major + '.' + minor + '.' + patch

# on mac os
# arduino_mega_ADDR = "/dev/cu.usbmodem141101"
# on raspberry pi (rpi)
arduino_mega_ADDR = "/dev/ttyACM0"


script_name = os.path.basename(__file__)

print('--- Running ' + script_name + ' ---')
# print(__file__)

# EPICS channel for the VGA control
IFO = 'N1'
SYSTEM = 'LSC'
SUBSYS = 'VGA'

# 'N1:LSC-VGA_'
VGA_PREFIX = IFO + ':' + SYSTEM + '-' + SUBSYS + '_'

arduino_megaDB = {
    'CHAN_0_GAINS': {'type': 'int'},
    'CHAN_0_FILTERS': {'type': 'int'},
    'CHAN_0_GAINS_RB': {'type': 'int'},
    'CHAN_0_FILTERS_RB': {'type': 'int'},
    # 'CHAN_0_GAINS_ERROR': {'type': 'char', 'count': 300},
    # 'CHAN_0_FILTERS_ERROR': {'type': 'char', 'count': 300},
    'CHAN_0_FILTER00': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_0_FILTER01': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_0_FILTER02': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_1_GAINS': {'type': 'int'},
    'CHAN_1_FILTERS': {'type': 'int'},
    'CHAN_1_GAINS_RB': {'type': 'int'},
    'CHAN_1_FILTERS_RB': {'type': 'int'},
    # 'CHAN_1_GAINS_ERROR': {'type': 'char', 'count': 300},
    # 'CHAN_1_FILTERS_ERROR': {'type': 'char', 'count': 300},
    'CHAN_1_FILTER00': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_1_FILTER01': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_1_FILTER02': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_2_GAINS': {'type': 'int'},
    'CHAN_2_FILTERS': {'type': 'int'},
    'CHAN_2_GAINS_RB': {'type': 'int'},
    'CHAN_2_FILTERS_RB': {'type': 'int'},
    # 'CHAN_2_GAINS_ERROR': {'type': 'char', 'count': 300},
    # 'CHAN_2_FILTERS_ERROR': {'type': 'char', 'count': 300},
    'CHAN_2_FILTER00': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_2_FILTER01': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_2_FILTER02': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_3_GAINS': {'type': 'int'},
    'CHAN_3_FILTERS': {'type': 'int'},
    'CHAN_3_GAINS_RB': {'type': 'int'},
    'CHAN_3_FILTERS_RB': {'type': 'int'},
    # 'CHAN_3_GAINS_ERROR': {'type': 'char', 'count': 300},
    # 'CHAN_3_FILTERS_ERROR': {'type': 'char', 'count': 300},
    'CHAN_3_FILTER00': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_3_FILTER01': {'type': 'enum', 'enums': ['0', '1']},
    'CHAN_3_FILTER02': {'type': 'enum', 'enums': ['0', '1']},
}

ini_file_name = 'lsc_vga_ctrl_ini_content.txt'
# len(python/) == 7
ini_file_dirpath_local_write = os.path.dirname(
    os.path.realpath(__file__))[:-7] + '/ini/'
ini_file_dirpath_rpi = '/opt/rtcds/anu/n1/softioc/lsc_vga_ctrl/ini/'


def generate_ini_file(ini_file_dirpath, db):
    '''
    generate the ini file with default parameters and the busDB attributes
    Input:
        ini_file_dirpath: directory path to write the ini file
        busDB: dictionary with device channel names and channel types
    '''
    now = dt.now()
    with open(ini_file_dirpath + ini_file_name, 'w') as ini_file:
        ini_file.writelines(["# Auto generated file by " + script_name + "\n",
                             "# at " +
                             now.strftime("%Y-%m-%d %H:%M:%S") + "\n",
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
        for key in db.keys():
            ini_file.writelines("[" + VGA_PREFIX + key + "]\n")
    ini_file.close()


gain_chs = ['CHAN_' + str(_) + '_GAINS' for _ in range(4)]
gain_rb_chs = ['CHAN_' + str(_) + '_GAINS_RB' for _ in range(4)]
filter_chs = ['CHAN_' + str(_) + '_FILTERS' for _ in range(4)]
filter_rb_chs = ['CHAN_' + str(_) + '_FILTERS_RB' for _ in range(4)]
filter_separate_chs = [
    'CHAN_' + str(i) + '_FILTER0' + str(j) for i in range(4) for j in range(4)]

max_gain = (2 ** arduino_mega.NUM_GAINS_PER_CH - 1) * 3
max_filter = (2 ** arduino_mega.NUM_FILTERS_PER_CH - 1)


class MyDriver(Driver):
    def __init__(self):
        super().__init__()
        self.ard = arduino_mega.ArduinoMega(
            port=arduino_mega_ADDR, baudrate=9600)
        self.read_times = 0
        self.tid = threading.Thread(target=self.run)
        self.tid.setDaemon(True)
        self.tid.start()

    def read_channel(self, reason):
        ch = int(reason.split('_')[1])
        start_port = ch * arduino_mega.NUM_PORTS_PER_CH
        if reason in gain_chs:
            value = max_gain - int('0b' + self.ard.get_output_ports(
            )[start_port: start_port + arduino_mega.NUM_GAINS_PER_CH], 2) * 3
        elif reason in gain_rb_chs:
            value = int('0b' + self.ard.get_input_ports(
            )[start_port: start_port + arduino_mega.NUM_GAINS_PER_CH], 2) * 3
        elif reason in filter_chs:
            start_port += arduino_mega.NUM_GAINS_PER_CH
            value = int('0b' + self.ard.get_output_ports()[
                        start_port: start_port + arduino_mega.NUM_FILTERS_PER_CH], 2)
        elif reason in filter_rb_chs:
            start_port += arduino_mega.NUM_GAINS_PER_CH
            value = int('0b' + self.ard.get_input_ports()[
                        start_port: start_port + arduino_mega.NUM_FILTERS_PER_CH], 2)
        # FILTER00-02 are for choice buttons
        elif reason in filter_separate_chs:
            filt = int(reason[-1])
            # note even if in arduino script the return type is int, when it returns to rpi via serial, the transmitted data type is always string, so cast it to int is necessay
            value = 1 - int(self.ard.get_port(
                ch * arduino_mega.NUM_GAINS_PER_CH + arduino_mega.NUM_GAINS_PER_CH + filt))
        print(f"reason: {reason}, value: {value}")
        self.setParam(reason, value)
        self.updatePVs()
        return value

    def write(self, reason, value):
        ch = int(reason.split('_')[1])

        if reason in gain_chs:
            try:
                ports = [ch * arduino_mega.NUM_PORTS_PER_CH +
                         _ for _ in range(arduino_mega.NUM_GAINS_PER_CH)]
                vals = bin((max_gain - value) //
                           3)[2:].zfill(arduino_mega.NUM_GAINS_PER_CH)
                for p in range(len(ports)):
                    if not self.ard.set_port(ports[p], int(vals[p])):
                        print('Error setting port ' + str(ports[p]))
            except Exception as e:
                print(e)
            # finally:
            #     self.read(reason)
            #     self.read(reason + '_RB')

        elif reason in filter_separate_chs:
            try:
                filt = int(reason[-1])
                port = ch * arduino_mega.NUM_PORTS_PER_CH + arduino_mega.NUM_GAINS_PER_CH + filt
                if not self.ard.set_port(port, 1 - value):
                    print('Error setting port ' + str(port))
            except Exception as e:
                print(e)
            # finally:
            #     self.read_channel(reason[:-2] + 'S')
            #     self.read_channel(reason[:-2] + 'S_RB')
            #     self.read_channel(reason)
        # self.read(reason)
        self.setParam(reason, value)
        self.updatePVs()

    def run(self):
        while True:
            try:
                for reason in arduino_megaDB:
                    self.read_times += 1
                    print(f"{self.read_times} times: READING {reason}")
                    self.read_channel(reason)
                    sleep(.1)
                print(self.ard)
                sleep(.1)
            except Exception as e:
                print(f"ERROR: {str(e)} in channel: {reason}")
                sleep(5)
                continue


if __name__ == '__main__':
    print('--- generate .ini file content in ' + ini_file_name + ' ---')
    # use _local_write for local testing and debugging
    generate_ini_file(ini_file_dirpath_local_write, arduino_megaDB)
    # use _rpi for service on rpi server (in /etc/systemd/system/lsc_vga_ctrl_service.service)
    # generate_ini_file(ini_file_dirpath_rpi, busDB)

    print('--- now starting server ---')

    # when restarting rpi, give it time to load all packages, otherwise the service has errors
    sleep(1)

    server = SimpleServer()
    server.createPV(VGA_PREFIX, arduino_megaDB)

    driver = MyDriver()

    # Tell systemd that our service is ready
    systemd.daemon.notify('READY=1')

    while True:
        server.process(0.1)
