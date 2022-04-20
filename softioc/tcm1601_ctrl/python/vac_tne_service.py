#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from pcaspy import Driver, SimpleServer
import Tcm1601

import systemd.daemon
import datetime
import os.path
import threading

controllerPrefix = 'N1:VAC-TNE_TCM1601_'

controllerDB = {
    'MOTOR_TMP': {'type': 'enum', 'enums': ['0', '1']},
    'ERROR_LAST': {'type': 'str'},
    'ERROR_CODE': {'type': 'str', },
    'ACT_ROT_SPD': {'type': 'str'},
    'TMP_I_MOT': {'type': 'str'},
    'TMP_OP_HRS': {'type': 'str'},
    'PRESSURE': {'type': 'str'},
    'ADDRESS': {'type': 'int'},
    'SWITCH_PNT': {'type': 'str'},
}


class myDriver(Driver):
    def __init__(self):
        super().__init__()
        self.controller = Tcm1601.TCM1601('/dev/ttyUSB0')

    def read(self, reason):
        value = 'NULL'
        if reason == 'MOTOR_TMP':
            value = 1 if self.controller.get_turbopump_status() == 'ON' else 0
        elif reason == 'ERROR_CODE':
            value = self.controller.get_error()
        elif reason == 'ERROR_LAST':
            value = self.controller.get_last_error()
        elif reason == 'ACT_ROT_SPD':
            value = self.controller.get_act_rotspd()
        elif reason == 'TMP_I_MOT':
            value = self.controller.get_motor_current()
        elif reason == 'TMP_OP_HRS':
            value = self.controller.get_operation_hours()
        elif reason == 'PRESSURE':
            value = self.controller.get_pressure()
        elif reason == 'ADDRESS':
            value = self.controller.get_address()
        elif reason == 'SWTICH_PNT':
            value = self.controller.get_switch_point()

        self.setParam(reason, value)
        return value

    def write(self, reason, value):
        if reason == 'MOTOR_TMP':
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
        self.setParam(reason, value)
        self.read(reason)
        self.updatePVs()


if __name__ == '__main__':
    print('--- now starting server ---')

    server = SimpleServer()
    server.createPV(controllerPrefix, controllerDB)

    driver = myDriver()

    systemd.daemon.notify('READY=1')

    while True:
        server.process(0.1)
