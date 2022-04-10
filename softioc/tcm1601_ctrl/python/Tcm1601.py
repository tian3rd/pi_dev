#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tarfile import ENCODING
import serial
import subprocess

# Global variables for the commands to read from and write to the controller
# Refer to Pfeiffer Vacuum Manual TCM1601 Page 14

DATA_TYPE = {
    0: {
        'no.': 0,
        'type': 'boolean_old',
        'description': 'true/false in the form six zeros (ascii 48) or ones (ascii 49)',
        'size': 6,
    },
    1: {
        'no.': 1,
        'type': 'u_integer',
        'description': 'pre-symbol-less integer number with six positions (leading zeros)',
        'size': 6,
    },
    2: {
        'no.': 2,
        'type': 'u_real',
        'description': 'fixed comma number with four positions before and two after the comma standardized to 0.01 (leading zeros)',
        'size': 6,
    },
    3: {
        'no.': 3,
        'type': 'u_expo',
        'description': 'positive exponential number (leading zeros)',
        'size': 6,
    },
    4: {
        'no.': 4,
        'type': 'string',
        'description': 'optional symbol chain with ascii symbols >= 32 (decimal)',
        'size': 6,
    },
    7: {
        'no.': 7,
        'type': 'u_short_int',
        'description': 'pre-symbol-less integer number with three positions (leading zeros)',
        'size': 3,
    }
}

COMMAND = {
    'MotorTMP': {
        'number': 23,
        'display': 'Motor TMP',
        'description': 'Motor Tumbopump ON/OFF',
        'datatype': DATA_TYPE[0],
    },
    'ErrorCode': {
        'number': 303,
        'display': 'Error code',
        'description': 'Actual error code, no Err, Errxxx or Wrnxxx',
        'datatype': DATA_TYPE[4],
    },
    'ActRotSpd': {
        'number': 309,
        'display': 'Act rotspd',
        'description': 'Actual rotation speed TMP in Hz',
        'datatype': DATA_TYPE[1],
    },
    'TMPIMot': {
        'number': 310,
        'display': 'TMP I-Mot',
        'description': 'Motor current TMP in A',
        'datatype': DATA_TYPE[2],
    },
    'TMPOpHrs': {
        'number': 311,
        'display': 'TMP Op Hrs',
        'description': 'Motor operating hours TMP in h',
        'datatype': DATA_TYPE[1],
    },
    'Pressure': {
        'number': 340,
        'display': 'Pressure',
        'description': 'Actual pressure value in mbar',
        'datatype': DATA_TYPE[3],
    },
    'ADDRESS': {
        'number': 797,
        'display': 'Address',
        'description': 'Unit address',
        'datatype': DATA_TYPE[1],
    }
}

# command info such as {23: {'no': 0, 'type': 'boolean_old', ...}, 340: {}}
CMD_INFO = {COMMAND[cmd]['number']: COMMAND[cmd]['datatype']
            for cmd in COMMAND.keys()}

ON, OFF = '111111', '000000'

DEV_ADDR = 1

ENCODING = 'utf-8'


class TCM1601Exception(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class TCM1601(object):
    def __init__(self, port, baudrate=9600, timeout=1):
        '''
        Initialize the controller.
        Parameters:
            port: the serial port to use, e.g., '/dev/ttyUSB0'. use 'python3 -m serial.tools.list_ports' to find the port
            baudrate: the baudrate to use, defaults to 9600
            timeout: the timeout limit, defaults to 1s
        '''
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.addr = DEV_ADDR
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate,
                                 timeout=self.timeout)

    @property
    def addr(self):
        return self.addr

    @addr.setter
    def addr(self, address):
        if not isinstance(address, int):
            raise TCM1601Exception('Address must be an integer')
        elif address < 0 or address > 255:
            raise TCM1601Exception('Address must be between 0 and 255')
        self.send_control_command(
            COMMAND['ADDRESS'], '{:06d}'.format(address))

    def send_data_request(self, param_num: int, encoding: str = ENCODING):
        '''
        Send a data request to the controller.
        Parameters:
            ser: serial port to send the request to
            param_num: the parameter number to request
            addr: the address of the controller
            encoding: the encoding to use
        Returns:
            The encoded data request
        '''
        # 00: read, refer to Pfeiffer Vacuum Protocol page 7
        dataframe = "{:03d}00{:03d}02=?".format(self.addr, param_num)
        dataframe += "{:03d}\r".format(sum([ord(x) for x in dataframe]) % 256)
        encoded = dataframe.encode(encoding)
        print('Sending: {df}\n'
              'Encoded in ({enc}): {encd}'
              .format(df=dataframe, enc=encoding, encd=encoded))
        self.ser.write(dataframe.encode(encoding))
        # ensure the data is written
        self.ser.flush()
        return encoded

    def send_control_command(self, param_num, data_str, encoding=ENCODING):
        '''
        Send a control command to the controller.
        Parameters:
            ser: serial port to send the request to
            param_num: the parameter number to request
            data_str: the data to send
            addr: the address of the controller
            encoding: the encoding to use
        Returns:
            The encoded control command
        '''
        # 10: write
        dataframe = "{:03d}10{:03d}{:02d}{:s}".format(
            self.addr, param_num, len(data_str), data_str)
        dataframe += "{:03d}\r".format(sum([ord(x) for x in dataframe]) % 256)
        encoded = dataframe.encode(encoding)
        print('Sending: {df}\n'
              'Encoded in ({enc}): {encd}'
              .format(df=dataframe, enc=encoding, encd=encoded))
        self.ser.write(encoded)
        return encoded

    def decode_bytes(self, dataframe, encoding=ENCODING):
        '''
        Decode the bytes received from the controller.
        Parameters:
            dataframe: the dataframe to decode
            encoding: the encoding to use
        Returns:
            The decoded response
        '''
        dataframe = dataframe.decode(encoding)
        cmd_number = int(dataframe[5:8])
        response_type = CMD_INFO[cmd_number]['no.']
        data_length = CMD_INFO[cmd_number]['size']
        cmd_response = dataframe[-4 - data_length: -4]
        if response_type == 0:
            return "ON" if int(cmd_response) == 0 else "OFF"
        elif cmd_number == 1:
            return int(cmd_response)
        elif cmd_number == 2:
            return int(cmd_response) / 100
        elif cmd_number == 3:
            return float(cmd_response)
        elif cmd_number == 4:
            return cmd_response

    def status_request(self, command):
        '''
        Send a status request to the controller.
        Parameters:
            command: the COMMAND to send
        Returns:
            The original response in bytes    
        '''
        req = self.send_data_request(COMMAND[command]['number'])
        read_size = len(req) + COMMAND[command]['datatype']['size'] - 2
        return self.ser.read(read_size * 8)

    def get_act_rotspd(self):
        '''
        Get the actual rotation speed in Hz.
        '''
        return "{spd} Hz".format(spd=self.decode_bytes(self.status_request('ActRotSpd')))

    def get_motor_current(self):
        '''
        Get the motor current TMP in A.
        '''
        return "{cur} A".format(cur=self.decode_bytes(self.status_request('TMPIMot')))

    def get_operation_hours(self):
        '''
        Get the operation hours TMP in h.
        '''
        return "{hrs} h".format(hrs=self.decode_bytes(self.status_request('TMPOpHrs')))

    def get_pressure(self):
        '''
        Get the pressure value in mbar.
        '''
        return "{mbar} mbar".format(mbar=self.decode_bytes(self.status_request('Pressure')))

    def get_turbopump_status(self):
        '''
        Get the turbopump status.
        '''
        return self.decode_bytes(self.status_request('MotorTMP'))

    def get_address(self):
        '''
        Get the address of the controller.
        '''
        return self.decode_bytes(self.status_request('Address'))
        # or return self.addr

    def turn_on_turbopump(self):
        '''
        Turn on the turbopump.
        '''
        self.send_control_command(COMMAND['MotorTMP'], ON)
        return True if self.get_turbopump_status() == "ON" else False

    def turn_off_turbopump(self):
        '''
        Turn off the turbopump.
        '''
        self.send_control_command(COMMAND['MotorTMP'], OFF)
        return True if self.get_turbopump_status() == "OFF" else False
