#!/usr/bin/env python3

'''Exercise the Arduino ncal_response interface'''


import time
import serial	# easy_install -U pyserial

ARDUINO_SERIAL_PORT = '/dev/ttyACM0'
SERIAL_PORT_BAUD = 115200
PERIOD_ms = 100
SLEEP_TIME_S = 0.003*PERIOD_ms
REPETITIONS = 10
PORT_TIMEOUT = 10     # seconds, linear pul frequency takes 5 s

class Cmd_Response(object):
  '''interface class with cmd_response Arduino sketch'''

  def __init__(self, serial_port, baud=115200, 
               delimiter='\n', timeout=PORT_TIMEOUT):
    self.serial_port = serial_port
    self.baud = baud
    self.delimiter = delimiter
    self.timeout = timeout
    self.port = serial.Serial(serial_port, baud, timeout=self.timeout)
    self.port.flushInput()

  def send(self, cmd):
    '''write the command to the USB port'''
    cmd1 = cmd + self.delimiter
    self.port.write(cmd1.encode())

  def receive(self):
    '''read the device response from the USB port'''
    rtrn = self.port.readline().strip()
    return rtrn.decode('utf-8')
  
  def request(self, cmd):
    '''return the result from the command'''
    self.send(cmd)
    return self.receive()
  
  def report(self, cmd):
    '''print the response to the command'''
    print(cmd)
    print(self.request(cmd))

def main():
  '''test the Arduino cmd_response interface'''
  #cr.request('!t %d' % PERIOD_ms)
  #cr.request('!ai:watch 0 1')
  #cr.request('!ai:watch 1 1')
  #cr.request('!pin 11 1')
  
#  for _ in ('?id', '?v', '?k', '?pf', '?af'):
#    cr.report(_)

  #global PERIOD_ms
  cr = Cmd_Response(ARDUINO_SERIAL_PORT, SERIAL_PORT_BAUD)
  time.sleep(0.5)

  #cr.request('!pd 0')

  isok = cr.request('?pf')
  print(repr(isok))

  value = 0.0
  cmd = '!sp ' + str(value)
  print(repr(cmd))
  isok = cr.request(cmd)
  print(repr(isok))

if __name__ == '__main__':
  main()
