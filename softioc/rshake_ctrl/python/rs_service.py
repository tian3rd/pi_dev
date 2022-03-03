#!/usr/bin/env python

from pcaspy import Driver, SimpleServer
import rsconnect

rsPrefix = "RS_"

rsDB = {
    # update count value frequently using 'scan'
    'COUNT': {'type': 'int', 'scan': 0.1},
    'PRESSURE': {'prec': 2, 'unit': 'pa', 'scan': 0.1},
}


class MyDriver(Driver):
    def __init__(self):
        super().__init__()
        self.rs = rsconnect.RShake(host="", port=9988, interval=0.125)

    def read(self, reason):
        if reason == 'COUNT':
            value = self.rs.count
        if reason == 'PRESSURE':
            value = self.rs.count/56000

        return value


if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(rsPrefix, rsDB)
    driver = MyDriver()

    while True:
        server.process(0.1)
        driver.updatePVs()
