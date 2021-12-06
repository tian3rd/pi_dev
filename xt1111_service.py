from pcaspy import Driver, SimpleServer
import busworks_xt1111

# connect to xt1111

busPrefix = "XT1111_"

# , 'scan': 1 --- how to use scan?
busDB = {
    'GAINS': {'type': 'int'},
    'GAIN_CH00': {'type': 'int'},
    'GAIN_CH01': {'type': 'int'},
    'GAIN_CH02': {'type': 'int'},
    'GAIN_CH03': {'type': 'int'},
    'FILTERS': {'type': 'str'},
    'FILTER_CH04': {'type': 'int'},
    'FILTER_CH05': {'type': 'int'},
    'FILTER_CH06': {'type': 'int'},
    'LE_CH07': {'type': 'int'},
    'READBACKS': {'type': 'str'},
    # use char for error str longer than 40 chars
    'ERRORS': {'type': 'char', 'count': 300},
}

class MyDriver(Driver):
    def __init__(self):
        super().__init__()
        # connect to busworks XT1111 in initialization
        self.bus = busworks_xt1111.BusWorksXT1111()
        self.bus.start()
        self.error = False
        self.errorMsg = ''

    def read(self, reason):
        if reason == 'GAINS':
            value = self.bus.get_gains()
            self.setParam('GAINS', value)
            return value
        if reason in ['GAIN_CH0' + str(_) for _ in range(4)]:
            channel = int(reason[-1])
            value = self.bus.get_gains_in_binary(channel)
            self.setParam(reason, value)
            return value
        if reason == 'FILTERS':
            value = self.bus.get_filters()
            # print("filters: {}".format(value))
            self.setParam('FILTERS', value)
            return value
        if reason in ['FILTER_CH0' + str(_) for _ in range(4, 7)]:
            channel = int(reason[-1])
            value = int(self.bus.get_filters()[channel - 4])
            self.setParam(reason, value)
            return value
        if reason == 'LE_CH07':
            value = self.bus.get_le()
            self.setParam('LE_CH07', value)
            return value
        if reason == 'READBACKS':
            value = self.bus.get_readbacks()
            self.setParam('READBACKS', value)
            return value
        if reason == 'ERRORS':
            if self.error:
                # value = 'Error!'
                value = self.errorMsg
            else:
                value = 'No error'
            self.setParam('ERRORS', value)
            return value

    def write(self, reason, value):
        if reason == 'GAINS':
            try:
                self.bus.set_gains(value)
                self.error = False
                self.setParam('GAINS', value)
                driver.updatePVs()
            except Exception as e:
                self.error = True
                self.errorMsg = str(e)

        if reason == 'FILTERS':
            try:
                self.bus.set_filters(str(value))
                self.error = False
                self.setParam('FILTERS', str(value))
                driver.updatePVs()
            except Exception as e:
                self.error = True
                self.errorMsg = str(e)
    
    def read_database(self):
        self.read('READBACKS')
        self.read('GAINS')
        self.read('FILTERS')
        self.read('ERRORS')
        self.read('GAIN_CH00')
        self.read('GAIN_CH01')
        self.read('GAIN_CH02')
        self.read('GAIN_CH03')
        self.read('FILTER_CH04')
        self.read('FILTER_CH05')
        self.read('FILTER_CH06')
        self.read('LE_CH07')


if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(busPrefix, busDB)
    driver = MyDriver()

    while True:
        server.process(0.1)

        # update pvs so that GUI can update as well
        driver.updatePVs()

        # keep the readings uptodate
        driver.read_database()
        # driver.read('READBACKS')
        # driver.read('GAINS')
        # driver.read('FILTERS')
        # driver.read('ERRORS')
        # driver.read('GAIN_CH00')
        # driver.read('GAIN_CH01')
        # driver.read('GAIN_CH02')
        # driver.read('GAIN_CH03')
        # driver.read('FILTER_CH04')
        # driver.read('FILTER_CH05')
        # driver.read('FILTER_CH06')
        # driver.read('LE_CH07')