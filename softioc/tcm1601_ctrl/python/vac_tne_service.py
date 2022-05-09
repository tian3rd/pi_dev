#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcaspy import Driver, SimpleServer
from time import sleep, time
import logging
from datetime import datetime as dt
import systemd.daemon
import os.path
import threading

import Tcm1601

script_name = os.path.basename(__file__)
print('--- Running ' + script_name + ' ---')

# EPICS channel for TCM1601 controller
IFO = 'N1'
SYSTEM = 'FLX'
SUBSYS = 'TNE_TCM1601'

# controllerPrefix = 'N1:VAC-TNE_TCM1601_'
# rename the channel name prefix to 'N1:FLX-TNE_TCM1601_'
controllerPrefix = IFO + ':' + SYSTEM + '-' + SUBSYS + '_'

controllerDB = {
    'MOTOR_TMP': {'type': 'enum', 'enums': ['0', '1']},
    'ERROR_LAST': {'type': 'str'},
    # 'ERROR_CODE': {'type': 'str', },
    'ACT_ROT_SPD': {'type': 'str'},
    'TMP_I_MOT': {'type': 'str'},
    # 'TMP_OP_HRS': {'type': 'str'},
    # # 'PRESSURE': {'type': 'str'},
    # 'ADDRESS': {'type': 'int'},
    # 'SWITCH_PNT': {'type': 'str'},
    'TMS_ACT_TMP': {'type': 'str'},
    'ELAPSED_TIME': {'type': 'str'},
}

# local logging files for quick debugging
logging.basicConfig(filename=dt.today().strftime('%Y-%m-%d') + '_log', filemode='a',
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

ini_file_name = 'vac_tne_ini_content.txt'
ini_file_dirpath_local_write = os.path.dirname(
    os.path.realpath(__file__))[:-7] + '/ini/'
ini_file_dirpath_controller = '/opt/rtcds/anu/n1/softioc/tcm1601_ctrl/ini/'


def generate_ini_file(ini_file_dirpath, controllerDB):
    '''
    Generate the ini file for the controller.
    Input:
        ini_file_dirpath: the directory path to the ini file
        controllerDB: the dictionary of the controller channels and types
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
        for channel in controllerDB:
            ini_file.writelines("[" + controllerPrefix + channel + "]\n")
    ini_file.close()


class MyDriver(Driver):
    def __init__(self, controller_address='/dev/ttyUSB0'):
        super().__init__()
        self.controller = Tcm1601.TCM1601(controller_address)
        self.script_start = time()
        self.start_timing = -1
        self.elapsed = -2
        self.tid = threading.Thread(target=self.run)
        self.tid.setDaemon(True)
        self.tid.start()

    def read_channels(self, reason):
        value = 'NULL'
        try:
            if reason == 'MOTOR_TMP':
                value = 1 if self.controller.get_turbopump_status() == 'ON' else 0
            elif reason == 'ELAPSED_TIME':
                value = '{t} s'.format(t=self.elapsed)
            elif reason == 'ERROR_CODE':
                value = self.controller.get_error()
            elif reason == 'ERROR_LAST':
                value = self.controller.get_last_error()
            elif reason == 'ACT_ROT_SPD':
                value = self.controller.get_act_rotspd()
                spd = int(value.split()[0])
                if spd > 1 and spd < 599:
                    self.elapsed = time() - self.start_timing
            elif reason == 'TMP_I_MOT':
                value = self.controller.get_motor_current()
            elif reason == 'TMP_OP_HRS':
                value = self.controller.get_operation_hours()
            elif reason == 'PRESSURE':
                value = self.controller.get_pressure()
            elif reason == 'ADDRESS':
                value = self.controller.get_address()
            elif reason == 'SWITCH_PNT':
                value = self.controller.get_switch_point()
            elif reason == 'TMS_ACT_TMP':
                value = self.controller.get_tms_act_tmp()
        except Exception as e:
            err_msg = "ERROR occurred while reading: {}".format(str(e))
            print(err_msg)
            logging.error(err_msg)

        self.setParam(reason, value)
        self.updatePVs()
        return value

    def write(self, reason, value):
        try:
            if reason == 'MOTOR_TMP':
                self.start_timing = time()
                success = self.controller.turn_on_turbopump() if int(
                    value) == 1 else self.controller.turn_off_turbopump()
                if not success:
                    print('Error turning on/off turbopump')
            elif reason == 'ADDRESS':
                value = int(value)
                self.controller.set_address(value)
            elif reason == 'SWTICH_PNT':
                value = int(value)
                success = self.controller.set_switch_point(value)
                if not success:
                    print('Failed to set switch point')
        except Exception as e:
            err_msg = "ERROR occurred while writing: {}".format(str(e))
            print(err_msg)
            logging.error(err_msg)
        self.setParam(reason, value)
        self.read(reason)
        self.updatePVs()

    def run(self):
        while True:
            try:
                current_status = []
                for reason in controllerDB.keys():
                    # if reason != 'ELAPSED_TIME':
                    print("READING: ", reason)
                    current_status.append(
                        reason + ": " + str(self.read_channels(reason)))
                    sleep(.1)
                self.updatePVs()
                if time() - self.script_start > 2:
                    logging.info(f'{" | ".join(current_status)}')
                    self.script_start = time()
            except Exception as e:
                err_msg = "ERROR occurred while running the script: {}".format(
                    str(e))
                print(err_msg)
                logging.error(err_msg)
                continue


if __name__ == '__main__':
    print('--- generate .ini file content in ' + ini_file_name + ' ---')
    # local_write for local testing
    generate_ini_file(ini_file_dirpath_local_write, controllerDB)
    # # if mounted, use cds file write instead
    # generate_ini_file(ini_file_dirpath_controller, controllerDB)

    print('--- now starting server ---')

    sleep(1)

    server = SimpleServer()
    server.createPV(controllerPrefix, controllerDB)

    driver = MyDriver()

    systemd.daemon.notify('READY=1')

    while True:
        server.process(0.1)
