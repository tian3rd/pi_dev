from pcaspy import Driver, SimpleServer
import busworks_xt1111

# connect to xt1111

busPrefix = "XT1111_"

busDB = {
    'GAINS': {'type': 'int'},
    'GAIN_CH00': {'type': 'int'},
    'GAIN_CH01': {'type': 'int'},
    'GAIN_CH02': {'type': 'int'},
    'GAIN_CH03': {'type': 'int'},
    'GAIN00': {'type': 'enum', 'enums': ['0', '1']},
    'GAIN01': {'type': 'enum', 'enums': ['0', '1']},
    'GAIN02': {'type': 'enum', 'enums': ['0', '1']},
    'GAIN03': {'type': 'enum', 'enums': ['0', '1']},
    'FILTERS': {'type': 'str'},
    'FILTER_CH04': {'type': 'int'},
    'FILTER_CH05': {'type': 'int'},
    'FILTER_CH06': {'type': 'int'},
    'FILTER04': {'type': 'enum', 'enums': ['0', '1']},
    'FILTER05': {'type': 'enum', 'enums': ['0', '1']},
    'FILTER06': {'type': 'enum', 'enums': ['0', '1']},
    'LE_CH07': {'type': 'int'},
    'READBACKS': {'type': 'str'},
    'READBACK_GAINS': {'type': 'int'},
    'READBACK08': {'type': 'int'},
    'READBACK09': {'type': 'int'},
    'READBACK10': {'type': 'int'},
    'READBACK11': {'type': 'int'},
    'READBACK12': {'type': 'int'},
    'READBACK13': {'type': 'int'},
    'READBACK14': {'type': 'int'},
    'READBACK15': {'type': 'int'},
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
        # GAIN_CH00-04 are readings for black/red indicators
        if reason in ['GAIN_CH0' + str(_) for _ in range(4)]:
            channel = int(reason[-1])
            value = self.bus.get_gains_in_binary(channel)
            self.setParam(reason, value)
            return value
        # GAIN00-04 are for choice buttons
        if reason in ['GAIN0' + str(_) for _ in range(4)]:
            channel = int(reason[-1])
            value = self.bus.get_gains_in_binary(channel)
            self.setParam(reason, value)
            return value
        # A temporary string value of filter states: e.g., "000", "101"
        if reason == 'FILTERS':
            value = self.bus.get_filters()
            # print("filters: {}".format(value))
            self.setParam('FILTERS', value)
            return value

        # FILTER_CH04-07 are readings for black/red indicators
        if reason in ['FILTER_CH0' + str(_) for _ in range(4, 7)]:
            channel = int(reason[-1])
            value = int(self.bus.get_filters()[channel - 4])
            self.setParam(reason, value)
            return value
        # FILTER04-07 are for choice buttons
        if reason in ['FILTER0' + str(_) for _ in range(4, 7)]:
            channel = int(reason[-1])
            value = self.bus.get_filters_in_binary(channel)
            self.setParam(reason, value)
            return value
        if reason == 'LE_CH07':
            value = self.bus.get_le()
            self.setParam('LE_CH07', value)
            return value
        # A temporary string of row2 (i/o 08-11) and row3 (i/o 12-15)
        if reason == 'READBACKS':
            value = self.bus.get_readbacks()
            self.setParam('READBACKS', value)
            return value
        # READBACK08-15 are indivisual readings for black/red indicators
        if reason in ['READBACK' + _ for _ in ['08', '09', '10', '11', '12', '13', '14', '15']]:
            channel = int(reason[-2:])
            value = self.bus.get_readback(channel)
            self.setParam(reason, value)
            return value
        # Display of decimal readback gains from i/o 08-11
        if reason == 'READBACK_GAINS':
            value = self.bus.get_readback_gains()
            self.setParam('READBACK_GAINS', value)
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
                self.updatePVs()
            except Exception as e:
                self.error = True
                self.errorMsg = str(e)

        if reason in ['GAIN0' + str(_) for _ in range(4)]:
            gain = bin(self.bus.read_registers()[0])[2:]
            gain = '0' * (4 - len(gain)) + gain
            channel = int(reason[-1])
            if str(value) != gain[3 - channel]:
                if channel != 0:
                    gain = gain[: (3 - channel)] + str(value) + \
                        gain[(4 - channel):]
                else:
                    gain = gain[: (3 - channel)] + str(value)
            # conver binary to decimal
            gain_updated = int(gain, 2)
            self.bus.set_gain_channels(gain_updated)
            self.setParam(reason, value)
            self.updatePVs()

        if reason in ['GAIN_CH0' + str(_) for _ in range(4)]:
            try:
                original_value = self.bus.read_registers()[0]
                channel = int(reason[-1])
                temp = 1 << (channel)
                reverse_channel_bit = temp ^ original_value
                self.bus.set_gain_channels(reverse_channel_bit)
                self.setParam(reason, value)
                self.updatePVs()
            except Exception as e:
                self.error = True
                self.errorMsg = str(e)

        if reason == 'FILTERS':
            try:
                self.bus.set_filters(str(value))
                self.error = False
                self.setParam('FILTERS', str(value))
                self.updatePVs()
            except Exception as e:
                self.error = True
                self.errorMsg = str(e)

        if reason in ['FILTER0' + str(_) for _ in range(4, 7)]:
            assert self.bus.read_registers()[1] >= 8
            filter_str = bin(self.bus.read_registers()[1])[2:][::-1]
            channel = int(reason[-1])
            if str(value) != filter_str[channel - 4]:
                filter_str = filter_str[:(channel - 4)] + \
                    str(value) + filter_str[(channel - 3):]
            # convert it back to decimal
            filter_updated = int(filter_str[::-1], 2)
            self.bus.set_filter_channels(filter_updated)
            self.setParam(reason, value)
            self.updatePVs()

    def read_database(self):
        self.read('READBACKS')
        self.read('GAINS')
        self.read('FILTERS')
        self.read('ERRORS')
        # read four gain channels
        for i in range(4):
            self.read('GAIN_CH0' + str(i))
            self.read('GAIN0' + str(i))
        # read three filter channels
        for i in range(4, 7):
            self.read('FILTER_CH0' + str(i))
        # read on/off channel
        self.read('LE_CH07')
        # read the signals from readback channels
        for ch in ['08', '09', '10', '11', '12', '13', '14', '15']:
            self.read('READBACK' + ch)
        # read readback gains
        self.read('READBACK_GAINS')


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
