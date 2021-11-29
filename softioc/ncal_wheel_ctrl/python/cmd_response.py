#!/usr/bin/env python

'''Exercise the Arduino cmd_response interface'''


import time
import serial	# easy_install -U pyserial


ARDUINO_SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_PORT_BAUD = 115200
PERIOD_ms = 100
SLEEP_TIME_S = 0.003*PERIOD_ms
REPETITIONS = 10
PORT_TIMEOUT = 2     # seconds


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
    self.port.write(cmd + self.delimiter)

  def receive(self):
    '''read the device response from the USB port'''
    return self.port.readline().strip()
  
  def request(self, cmd):
    '''return the result from the command'''
    self.send(cmd)
    return self.receive()
  
  def report(self, cmd):
    '''print the response to the command'''
    print "%s  " % cmd,
    print self.request(cmd)


def measure(port, pwm, reps=1):
  '''report reading(s): LED  photocell  <photocell>'''
  port.request('!pwm 11 %d' % pwm)
  time.sleep(SLEEP_TIME_S)
  port.receive()
  for _ in range(reps):
    time.sleep(PERIOD_ms*0.0011)
    V_led_raw = int(port.request('?ai 0'))
    V_led = float(port.request('?ai:mean 0'))/1000.
    V_P   = float(port.request('?ai:mean 1'))/1000.
    print "%d %d %.3f %.3f" % (pwm, V_led_raw, V_led, V_P)


def main():
  '''test the Arduino cmd_response interface'''
  global PERIOD_ms
  cr = Cmd_Response(ARDUINO_SERIAL_PORT, SERIAL_PORT_BAUD)
  time.sleep(2.0)
  cr.request('!t %d' % PERIOD_ms)
  cr.request('!ai:watch 0 1')
  cr.request('!ai:watch 1 1')
  cr.request('!pin 11 1')

  if False:         # development use
    for _ in ('?id', '?v', '?t', '?k', '?rate'):
      cr.report(_)
 
    time.sleep(SLEEP_TIME_S)
    rate = cr.request('?rate')
    print rate
    print cr.request('?t')
    print cr.request('?ai 0')
    print cr.request('?ai:mean 0')
    print cr.request('?ai:mean 1')

  for pwm in range(0, 256, 5):
    measure(cr, pwm)
  for pwm in range(255, 0, -5):
    measure(cr, pwm)

  # change to a longer averaging period
  PERIOD_ms = 1000
  cr.request('!t ' + str(PERIOD_ms))

  for pwm in range(0, 256, 5):
    measure(cr, pwm, REPETITIONS)

  cr.request('!pwm 11 0')   # turn the pwm off


if __name__ == '__main__':
  main()