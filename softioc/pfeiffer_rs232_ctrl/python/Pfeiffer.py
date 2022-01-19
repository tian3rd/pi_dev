import serial
from serial.serialutil import CR

# refer to page 65 of the TPG261 mannual for abbr/control symbols(CS).
CS = {
    'EXT': b'\x03',  # end of text (ctrl-C)
    'CR': b'\x0D',    # carriage return
    'LF': b'\x0A',    # line feed
    'ENQ': b'\x05',  # enquiry
    'ACK': b'\x06',  # acknowledge
    'NAK': b'\x15',  # negative acknowledge
}

# line termination
TERM = CS['CR'] + CS['LF']

# useful mnemonic for the command
MN = set([
    b'UNI',  # pressure unit
    b'DCD',  # display resolution
    b'ERR',  # error status
    b'PR1',  # pressure measurement gauge 1
    b'PR2',  # pressure measurement gauge 2
    b'TID',  # gauge identification
])

# gauge status
STATUS = {
    '0': 'ok',
    '1': 'under',
    '2': 'over',
    '3': 'sensor_error',
    '4': 'sensor_off',
    '5': 'no_sensor',
    '6': 'id_error',
}

# gauge errors
ERROR = {
    b'0000': 'No error',
    b'1000': 'Controller error',
    b'0100': 'NO HWR',
    b'0010': 'PAR',
    b'0001': 'SYN',
}

# pressure unit
UNITS = {
    b'0': 'mbar',
    b'1': 'Torr',
    b'2': 'Pascal',
}

# gauge type
TYPES = {
}


class TPG261Exception(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class TPG261(object):
    def __init__(self, port, baudrate=9600):
        self.term = 'connected'
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        self.ser.flushInput()
        # except serial.SerialException as e:
        #     raise TPG261Exception(e)

    def send(self, command):
        self.ser.flush()
        # self.ser.flushInput()
        
        if command not in MN:
            raise TPG261Exception('invalid command')
        # self.ser.write(command + b'\r\n')
        self.ser.write(command + TERM)
        out = self.ser.readline()
        if len(out) == 2:
            raise TPG261Exception('invalid response')
        # if len(out) > 2 and out[-3] == CS['NAK'][0]:
        if len(out) > 2 and out[-3] == b'\x15'[0]:
            raise TPG261Exception('negative ack')
        # self.ser.readline()
        # self.ser.write(b'\x05')
        self.ser.write(CS['ENQ'])
        out = self.ser.readline()[:-2]
        # self.ser.flushOutput()
        return out

    def get_units(self):
        return UNITS[self.send(b'UNI')]

    def get_display_resolution(self):
        return int(self.send(b'DCD'))

    def get_gauge_kind(self):
        return self.send(b'TID').decode()

    def get_pressure(self, channel=1, display_units=False):
        if channel == 1:
            status_code, value = self.send(b'PR1').decode().replace(" ", "").split(',')
        elif channel == 2:
            status_code, value = self.send(b'PR2').decode().replace(" ", "").split(',')
        if status_code != '0':
            raise TPG261Exception('channel status error')
        # return "{:.2f}".format(float(value))
        return float(value)

    def get_channel_status(self):
        status_code1, value1 = self.send(b'PR1').decode().replace(" ", "").split(',')
        status_code2, value2 = self.send(b'PR2').decode().replace(" ", "").split(',')
        return f'{STATUS[status_code1]}, {STATUS[status_code2]}'

    def get_current_errors(self):
        return ERROR[self.send(b'ERR')]
