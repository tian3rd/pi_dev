from pcaspy import Driver, SimpleServer
import Tcm1601

import systemd.daemon
import datetime
import os.path
import threading

tnePrefix = 'N1:VAC-TNE_TCM1601_'

tneDB = {
    'ERROR': {'type': 'str', },
    'MOTOR_CUR': {'type': 'str'},
    'ACT_ROT_SPEED': {'type': 'str'},
    'ADDRESS': {'type': 'int'},

}

class myDriver(Driver):
    def __init__(self):
        super().__init__()
        self.controller = Tcm1601.TCM1601('/dev/ttyUSB0')

    def read(self, reason):
        if reason == 'MOTO_CUR':
            value = self.controller.get_motor_current()
        if reason == 'ACT_ROT_SPEED':
            value = self.controller.get_act_rotspd()
        if reason == 'ADDRESS':
            value = self.controller.get_address()
        
        self.setParam(reason, value)
        return value

if __name__ == '__main__':
    print('--- now starting server ---')

    server = SimpleServer()
    server.createPV(tnePrefix, tneDB)

    driver = myDriver()

    systemd.daemon.notify('READY=1')

    while True:
        server.process(0.1)
    

    