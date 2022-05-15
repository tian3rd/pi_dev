# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyfirmata
from time import sleep


class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


NUM_GAIN_CHNS = 4


class Arduino(object):
    def __init__(self, port: str):
        self.port = port
        self.connected = False
        self.try_to_connect()

    def try_to_connect(self):
        while not self.connected:
            try:
                self.board = pyfirmata.Arduino(self.port)
                self.it = pyfirmata.util.Iterator(self.board)
                self.it.start()
            except Exception as e:
                print("Can't connect to Arduino: " + str(e))
                sleep(3)
            else:
                self.connected = True
                self.inputs = []
                for pin in range(2, 10):
                    self.inputs.append(self.board.get_pin(f'd:{pin}:o'))
                self.outputs = []
                for pin in range(10, 14):
                    self.outputs.append(self.board.get_pin(f'd:{pin}:i'))
                for pin in range(0, 4):
                    self.outputs.append(self.board.get_pin(f'a:{pin}:i'))

    def turn_on_pin(self, pin: int) -> bool:
        try:
            self.inputs[pin].write(1)
        except Exception as e:
            self.connected = False
            print("Can't turn on pin {i}: ".format(i=pin) + str(e))
            self.try_to_connect()
        return self.is_on(pin)

    def turn_off_pin(self, pin: int) -> bool:
        self.inputs[pin].write(0)
        return not self.is_on(pin)

    def is_on(self, pin: int) -> bool:
        return self.inputs[pin].read() > 0.9

    def set_gains(self, gains):
        gains_in_binary = f'{int(bin(gains//3)[2:]):0{NUM_GAIN_CHNS}d}'
        for i in range(NUM_GAIN_CHNS):
            self.outputs[i].write(int(gains_in_binary[i]))

    def set_filters(self, chn: int, state: bool = True) -> bool:
        if chn < 0 or chn > 3:
            print('Filter channel should be in range [0, 3)')
            return False
        self.outputs[NUM_GAIN_CHNS + chn - 1].write(int(state))
        return True
