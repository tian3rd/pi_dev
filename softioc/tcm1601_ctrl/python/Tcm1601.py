#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tarfile import ENCODING
import serial
import subprocess
from time import sleep


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
    'RUTimeCtr': {
        'number': 4,
        'datatype': DATA_TYPE[0],
    },
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
    'Mag_Tmp': {
        'number': 304,
        'datatype': DATA_TYPE[0],
    },
    'Turbo_Tmp': {
        'number': 305,
        'datatype': DATA_TYPE[0]
    },
    'ErrorLast': {
        'number': 360,
        'display': 'Past Error',
        'description': 'Error storage, Position 1',
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
    'Address': {
        'number': 797,
        'display': 'Address',
        'description': 'Unit address',
        'datatype': DATA_TYPE[1],
    },
    'TMSheatSet': {
        'number': 704,
        'display': 'TMSheatSet',
        'descripton': 'TMS Heating Temperature set value in degree celcius',
        'datatype': DATA_TYPE[1],
    },
    'SwitchPnt': {
        'number': 701,
        'display': 'SwitchPnt',
        'description': 'Rotation speed switchpoint in %',
        'datatype': DATA_TYPE[1],
    },
    'TMPRot_Set':{
        'number': 707,
        'datatype': DATA_TYPE[2],
    },
    'TMPRUTime': {
        'number': 700,
        'display': 'TMPRUTime',
        'description': 'maximum run-up time in mins',
        'datatype': DATA_TYPE[1],
    },
    'TMS_ActTmp': {
        'number': 331,
        'display': 'TMS ActTmp',
        'description': 'Heating TMS, actual value in celcius',
        'datatype': DATA_TYPE[1],
    },
    'Heat_Type': {
        'number': 335,
        'datatype': DATA_TYPE[7],
    },
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
        self.dt = .100

    @property
    def addr(self):
        return self._addr

    @addr.setter
    def addr(self, value):
        if not isinstance(value, int):
            raise TCM1601Exception('Address must be an integer')
        elif value < 0 or value > 255:
            raise TCM1601Exception('Address must be between 0 and 255')
        self._addr = value

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
        # self.ser.flush()
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
        # sleep(self.dt)
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
        print('dataframe: {df}'.format(df=dataframe))
        cmd_number = int(dataframe[5:8])
        print('cmd_no: {cn}'.format(cn=cmd_number))
        response_type = CMD_INFO[cmd_number]['no.']
        print('response type: {rt}'.format(rt=response_type))
        data_length = CMD_INFO[cmd_number]['size']
        cmd_response = dataframe[-4 - data_length: -4]
        print('cmd response: {cr}'.format(cr=cmd_response))
        if response_type == 0:
            return "OFF" if int(cmd_response) == 0 else "ON"
        elif response_type == 1:
            return int(cmd_response)
        elif response_type == 2:
            return int(cmd_response) / 100
        elif response_type == 3:
            return float(cmd_response)
        elif response_type == 4:
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
        # specify the exact number of bytes to read, otherwise it's much slower using readline(), or read()
        return self.ser.read(read_size)

    def get_error(self) -> str:
        '''
        Ge the error info from controller.
        '''
        err_msg = self.decode_bytes(self.status_request('ErrorCode'))
        return err_msg

    def get_last_error(self) -> str:
        '''
        Ge the last error info from controller.
        '''
        err_msg = self.decode_bytes(self.status_request('ErrorLast'))
        return err_msg

    def get_act_rotspd(self) -> str:
        '''
        Get the actual rotation speed in Hz.
        '''
        return "{spd} Hz".format(spd=self.decode_bytes(self.status_request('ActRotSpd')))

    def get_motor_current(self) -> str:
        '''
        Get the motor current TMP in A.
        '''
        return "{cur} A".format(cur=self.decode_bytes(self.status_request('TMPIMot')))

    def get_operation_hours(self) -> str:
        '''
        Get the operation hours TMP in h.
        '''
        return "{hrs} h".format(hrs=self.decode_bytes(self.status_request('TMPOpHrs')))

    def get_pressure(self) -> str:
        '''
        Get the pressure value in mbar.
        '''
        return "{mbar} mbar".format(mbar=self.decode_bytes(self.status_request('Pressure')))

    def get_mag_tmp(self) -> str:
        return f"{self.decode_bytes(self.status_request('Mag_Tmp'))}"

    def get_turbo_tmp(self) -> str:
        return f"{self.decode_bytes(self.status_request('Turbo_Tmp'))}"

    def get_turbopump_status(self) -> str:
        '''
        Get the turbopump status.
        '''
        return self.decode_bytes(self.status_request('MotorTMP'))
    
    def get_heat_type(self) -> str:
        '''
        Get the turbopump status.
        '''
        return self.decode_bytes(self.status_request('Heat_Type'))

    def get_address(self) -> int:
        '''
        Get the address of the controller.
        '''
        return self.decode_bytes(self.status_request('Address'))
        # return self.addr

    def get_temperature(self) -> str:
        return "{tmp} degrees".format(tmp=self.decode_bytes(self.status_request('TMSheatSet')))

    def get_tmprot_set(self) -> str:
        return "{} ".format(self.decode_bytes(self.status_request('TMPRot_Set')))

    def get_switch_point(self) -> str:
        return "{sp} %".format(sp=self.decode_bytes(self.status_request('SwitchPnt')))

    def get_tmp_rutimes(self) -> str:
        return "{ru} mins".format(ru=self.decode_bytes(self.status_request('TMPRUTime')))

    def get_tms_act_tmp(self) -> str:
        return "{temp} degrees".format(temp=self.decode_bytes(self.status_request('TMS_ActTmp')))

    def set_address(self, new_addr) -> bool:
        '''
        Set a new address for the controller.
        '''
        self.send_control_command(
            COMMAND['Address']['number'], '{:06d}'.format(new_addr))
        self.addr = new_addr
        return True if self.get_address() == new_addr else False

    def set_tmp_rutime(self, run_time=2):
        self.send_control_command(
            COMMAND['TMPRUTime']['number'], '{:06d}'.format(run_time))
        return True if self.get_tmp_rutimes() == "{ru} mins".format(ru=run_time) else False
        
    
    def set_switch_pnt(self, value) -> bool:
        '''
        Set a new switch point for the controller.
        '''
        if not isinstance(value, int):
            raise TCM1601Exception('Value must be an integer')
        elif value > 100 or value < 0:
            raise TCM1601Exception(
                'Value percentage must be between 0 and 100')
        self.send_control_command(
            COMMAND['SwitchPnt']['number'], '{:06d}'.format(value))
        return True if self.get_switch_point() == "{v} %".format(v=value) else False

    def turn_on_turbopump(self) -> bool:
        '''
        Turn on the turbopump.
        '''
        self.send_control_command(COMMAND['MotorTMP']['number'], ON)
        return True if self.get_turbopump_status() == "ON" else False

    def turn_off_turbopump(self) -> bool:
        '''
        Turn off the turbopump.
        '''
        self.send_control_command(COMMAND['MotorTMP']['number'], OFF)
        return True if self.get_turbopump_status() == "OFF" else False
