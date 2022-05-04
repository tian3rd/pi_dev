#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.log import INFO
import re
from pcaspy import Driver, SimpleServer
import Tcm1601
from time import sleep, time
import logging
from datetime import datetime as dt

import systemd.daemon
import datetime
import os.path
import threading

controllerPrefix = 'N1:VAC-TNE_TCM1601_'

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

logging.basicConfig(filename=dt.today().strftime('%Y-%m-%d') + '_log', filemode='a', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


class myDriver(Driver):
    def __init__(self):
        super().__init__()
        self.controller = Tcm1601.TCM1601('/dev/ttyUSB0')
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
                # self.setParam('ELAPSED_TIME', '{t} s'.format(t=self.elapsed))
                # self.updatePVs()
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
                    current_status.append(reason + ": " + str(self.read_channels(reason)))
                    sleep(.1)
                self.updatePVs()
                if time() - self.script_start > 2:
                    logging.info(f'{" | ".join(current_status)}')
                    self.script_start = time()
            except Exception as e:
                err_msg = "ERROR occurred while running the script: {}".format(str(e))
                print(err_msg)
                logging.error(err_msg)
                continue


if __name__ == '__main__':
    print('--- now starting server ---')

    server = SimpleServer()
    server.createPV(controllerPrefix, controllerDB)

    driver = myDriver()

    systemd.daemon.notify('READY=1')

    while True:
        server.process(0.1)
