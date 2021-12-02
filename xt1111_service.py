from pcaspy import Driver, SimpleServer
import busworks_xt1111

# connect to xt1111

busPrefix = "XT1111_"

busDB = {
    'GAINS': {'type': 'int', 'scan': 1},
    'FILTERS': {'type': 'int', 'scan': 1},
    'READBACKS': {'type': 'str', 'scan': 1},
}

class MyDriver(Driver):
    def __init__(self):
        super().__init__()
        # connect to busworks XT1111 in initialization
        self.bus = busworks_xt1111.BusWorksXT1111()
        self.bus.start()

    def read(self, reason):
        if reason == 'GAINS':
            return self.bus.get_gains()
        if reason == 'FILTERS':
            return self.bus.get_filters()
        if reason == 'READBACKS':
            return self.bus.get_readbacks()

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(busPrefix, busDB)
    driver = MyDriver()

    while True:
        server.process(0.1)