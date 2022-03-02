#!/usr/bin/env python

from pcaspy import Driver, SimpleServer
import rsconnect

rsPrefix = "RS_"

rsDB = {
    'COUNT': {'type': 'int'},
}


class MyDriver(Driver):
    def __init__(self):
        super().__init__()
        self.rs = rsconnect.RSConnect(host="", port=9988, interval=0.125)
        self.rs.start()

    def read(self, reason):
        if reason == 'COUNT':
            value = self.rs.get_count()

        return value


if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(rsPrefix, rsDB)
    driver = MyDriver()

    while True:
        server.process(0.1)
        driver.updatePVs()
