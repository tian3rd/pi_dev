from pcaspy import Driver, SimpleServer
import busworks_xt1111

# connect to xt1111

busPrefix = "XT1111_"

# , 'scan': 1 --- how to use scan?
busDB = {
    'GAINS': {'type': 'int'},
    'FILTERS': {'type': 'str'},
    'READBACKS': {'type': 'str'},
}

class MyDriver(Driver):
    def __init__(self):
        super().__init__()
        # connect to busworks XT1111 in initialization
        self.bus = busworks_xt1111.BusWorksXT1111()
        self.bus.start()

    def read(self, reason):
        if reason == 'GAINS':
            value = self.bus.get_gains()
            self.setParam('GAINS', value)
            return value
        if reason == 'FILTERS':
            value = self.bus.get_filters()
            # print("filters: {}".format(value))
            self.setParam('FILTERS', value)
            return value
        if reason == 'READBACKS':
            value = self.bus.get_readbacks()
            self.setParam('READBACKS', value)
            return value

    def write(self, reason, value):
        if reason == 'GAINS':
            self.bus.set_gains(value)
            self.setParam('GAINS', value)
        if reason == 'FILTERS':
            self.bus.set_filters(str(value))
            self.setParam('FILTERS', str(value))
            driver.updatePVs()

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(busPrefix, busDB)
    driver = MyDriver()

    while True:
        server.process(0.1)

        # update pvs so that GUI can update as well
        driver.updatePVs()