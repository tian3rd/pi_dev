#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from typing import Optional
import serial

END = b'\n'
ENCODING = 'utf-8'
MEGA = "/dev/cu.usbmodem141101"
NUM_PORTS_PER_CH = 8
NUM_CHS = 4
NUM_GAINS_PER_CH = 4
NUM_FILTERS_PER_CH = 3
DELAY_TIME = 50


class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ArduinoMega(object):
    def __init__(self, port=MEGA, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port=self.port, baudrate=baudrate)
        print(self.__class__.__name__ + ' connected')

    def send_command(self, command: str) -> str:
        command = command.strip().encode('utf-8') + END
        self.ser.write(command)
        self.ser.flush()
        return self.ser.read_until(END).strip().decode(ENCODING)

    def __str__(self) -> str:
        start_pin = 2
        outputs_status = self.get_output_ports()
        inputs_status = self.get_input_ports()
        arduino_info = "Arduino Mega Info:\n"
        vga_info = "VGA Info:\n"
        for ch in range(NUM_CHS):
            vga_info += "Channel {} -> ".format(chr(ch + ord('A')))
            for p in range(NUM_PORTS_PER_CH):
                port = ch * NUM_CHS + p
                arduino_info += "pin{:02d}: {} | ".format(
                    start_pin + port, outputs_status[port])
                vga_info += "{} | ".format(outputs_status[port])
            arduino_info += "\n"
            vga_info += "\n"
        return arduino_info + '\n' + vga_info

        # first show Arduino pin status from pin 2 to pin 65

        # then show the corresponding VGA board status

    def __repr__(self) -> str:
        return self.__class__.__name__ + "(" + self.port + ") at " + str(self.baudrate)

    def get_port(self, port: int) -> int:
        '''
        Returns the status of the port on VGA board. Note the port here is not the one in __init__
        Parameters:
            port: int for channel A, port 0 to 3 correspond to gains (24, 12, 6, 3), port 4 to 6 correspond to three filters, port 7 corresponds to the status.
        Returns:
            int: 0 LOW or 1 HIGH
        '''
        if port < 0 or port > 63:
            raise BaseException("Port must be between 0 and 63")
        result = int(self.send_command("R{:02d}".format(port)))
        return result

    def set_port(self, port: int, value: int) -> bool:
        if value > 1 or value < 0:
            raise BaseException("Value for pin on Arduino must be 0 or 1")
        if port < 0 or port > 31:
            raise BaseException("Port must be between 0 and 31")
        self.send_command("W{:02d}{:01d}".format(port, value))
        sleep(DELAY_TIME)
        if int(self.get_port(port)) != value:
            print("Failed to set port {} to {}".format(port, value))
            return False
        return True

    def get_output_ports(self) -> str:
        '''
        Returns the status of the 32 controlled ports (via MEDM interface) on VGA board.
        '''
        outputs_status = self.send_command("ROUTS")
        return outputs_status

    def get_input_ports(self) -> str:
        '''
        Returns the status of the readback ports on VGA board.
        '''
        inputs_status = self.send_command("RINTS")
        return inputs_status


# if __name__ == "__main__":
#     arduino = ArduinoMega()
#     print(arduino)
