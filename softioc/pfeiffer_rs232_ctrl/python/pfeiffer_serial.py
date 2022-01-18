import serial
from serial.serialutil import CR

# refer to page 65 of the TPG261 mannual for abbr/control symbols(CS).
CS = {
    'EXT': b'\x03', # end of text (ctrl-C)
    'CR': b'\0D',    # carriage return
    'LF': b'\0A',    # line feed
    'ENQ': b'\05',  # enquiry
    'ACK': b'\x06', # acknowledge
    'NAK': b'\x15', # negative acknowledge
}

# line termination
TERM = CS['CR'] + CS['LF']

# useful mnemonic for the command
MN = set([
    b'UNI', # pressure unit
    b'DCD', # display resolution
    b'ERR', # error status
    b'PR1', # pressure measurement gauge 1
    b'PR2', # pressure measurement gauge 2
    b'TID', # gauge identification
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
    '0000': 'No error',
    '1000': 'Controller error',
    '0100': 'NO HWR',
    '0010': 'PAR',
    '0001': 'SYN',
}

class TPG261Exception(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


class TPG261(object):
    def __init__(self, port, baudrate=9600):
        self.term = b'\r\n'
        try:
            self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        except serial.SerialException as e:
            raise TPG261Exception(e)


    def send(self, command):
        if command not in MN:
            raise TPG261Exception('invalid command')
        self.ser.write(command + TERM)
        out = self.ser.readline()
        if len(out) == 2:
            raise TPG261Exception('invalid response')
        if len(out) > 2 and out[-3] == CS['NAK']:
            raise TPG261Exception('negative ack')
        self.ser.write(CS['ENQ'])
        out = self.ser.readline()
        return out.decode()

    def get_units(self):
        return self.send(b'UNI')

    def get_display_resolution(self):
        return self.send(b'DCD')

    def get_gauge_kind(self):
        return self.send(b'TID')

    def get_pressure(self, channel=1, display_units=False):
        if channel == 1: status_code, value = self.send(b'PR1').split(', ')
        elif channel == 2: status_code, value = self.send(b'PR2').split(', ')
        if status_code != '0':
            raise TPG261Exception('channel status error')
        # return "{:.2f}".format(float(value))
        return float(value)
    
    def get_channel_status(self):
        status_code1, value1 = self.send(b'PR1').split(', ')
        status_code2, value2 = self.send(b'PR2').split(', ')
        return f'{STATUS[status_code1]}, {STATUS[status_code2]}'
    
    def get_current_errors(self):
        return ERROR[self.send(b'ERR')]
