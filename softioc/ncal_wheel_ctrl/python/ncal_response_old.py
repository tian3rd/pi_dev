#!/usr/bin/env python3

'''Exercise the Arduino cmd_response interface'''


import time
import datetime
import serial	# easy_install -U pyserial
import systemd.daemon

from pcaspy import Driver, SimpleServer

ARDUINO_SERIAL_PORT = '/dev/ttyACM0'
HWSERIAL_PORT = '/dev/ttyAMA0'
SERIAL_PORT_BAUD = 115200
PERIOD_ms = 100
SLEEP_TIME_S = 0.003*PERIOD_ms
REPETITIONS = 10
PORT_TIMEOUT = 2     # seconds


IFO = 'N1'
SYSTEM = 'NCAL'
#SUBSYS = ''

ncalPrefix = IFO + ':' + SYSTEM + '-'

ncalDB = {
    'RAW_FREQ_MEAS'              : { 'prec' : 3 },
    'ANGULAR_FREQ_MEAS'          : { 'prec' : 3 },
    'PULL_FREQ'                  : { 'prec' : 2 },
    'PULSE_PER_SEC'              : { 'prec' : 3 },
    'ANG_FREQ_PID'               : { 'prec' : 3 },
    'ANGULAR_FREQUENCY_SETPOINT' : { 'prec' : 3 },
    'ANG_FREQ_SETP_REACHED'      : { 'prec' : 1 },
    'ANGULAR_ACCELERATION'       : { 'prec' : 3 },
    'NUMBER_HOLES_RB'            : { 'prec' : 3 },
    'DRIVER_STATE_RB'            : { 'prec' : 1 },
    'DRIVER_STATE'               : { 'prec' : 1 },
    'VERSION'                    : { 'type' : 'str'},
    'ID'                         : { 'type' : 'str'},
}

class myDriver (Driver):
    def  __init__(self):
        super(myDriver, self).__init__()

    def get_fast_data(self, dr):
        _dt = dr.receive()
        lst = _dt.split(",")
        self.setParam('RAW_FREQ_MEAS', float(lst[0]))
        self.setParam('ANGULAR_FREQ_MEAS', float(lst[1]))
        self.setParam('PULL_FREQ', float(lst[2]))
        self.setParam('PULSE_PER_SEC', float(lst[3]))
        self.setParam('ANG_FREQ_PID', float(lst[4]))
        self.updatePVs()

    # def read(self, reason):
    #     #status = True
    #     if reason == 'ANGULAR_FREQUENCY_SETPOINT':
    #       value = self.getParam(reason)
    #       print(value)
    #       isok = cr.request('!sp ' + str(value))
    #       if isok != 'Ok':
    #         #status = False
    #         print('error: set_setpoint >' + repr(isok))
    #     elif reason == 'ANGULAR_ACCELERATION':
    #       value = self.getParam(reason)
    #       isok = cr.request('!aa ' + str(value))
    #       if isok != 'Ok':
    #         #status = False
    #         print('error: set_angular_acc >' + repr(isok))
    #     elif reason == 'DRIVER_STATE':
    #       value = self.getParam(reason)
    #       print(value)
    #       isok = cr.request('!en ' + str(value))
    #       value = 1
    #       if isok != 'Ok':
    #         #status = False
    #         print('error: set_driver_state >' + repr(isok))
    #     #if status:
    #     #  self.setParam(reason, value)
    #     #return value

    def set_setpoint(self, cr):
         #cr.receive()
        _sp = self.getParam('ANGULAR_FREQUENCY_SETPOINT')
        _cmd = '!sp ' + str(_sp)
        #print(_cmd)
        isok = cr.request(_cmd)
        #time.sleep(0.01)
        #cr.report(_cmd)
        if isok != 'Ok':
          print('error: set_setpoint >' + repr(isok))

    def set_angular_acc(self, cr):
        # cr.receive()
        _aa = self.getParam('ANGULAR_ACCELERATION')
        isok = cr.request('!aa ' + str(_aa))
        if isok != 'Ok':
          print('error: set_angular_acc >' + isok)

    def set_driver_state(self, cr):
        # cr.receive()
        _en = self.getParam('DRIVER_STATE')
        isok = cr.request('!en ' + str(_en))
        if isok != 'Ok':
          print('error: set_driver_state >' + isok)

    def get_setpoint_reached(self, cr):
        _as = cr.request('?as')
        self.setParam('ANG_FREQ_SETP_REACHED', float(_as))
        self.updatePVs()

    def get_hole_numbers(self, cr):
        _h = cr.request('?h')
        #print(_h)
        self.setParam('NUMBER_HOLES_RB', float(_h))
        self.updatePVs()

    def get_driver_state(self, cr):
        _st = int(cr.request('?en'))
        self.setParam('DRIVER_STATE_RB', _st)
        self.updatePVs()

    def get_version(self, cr):
        _v = cr.request('?v')
        self.setParam('VERSION', _v)
        self.updatePVs()

    def get_id(self, cr):
        _id = cr.request('?id')
        self.setParam('ID', _id)
        self.updatePVs()


class Ncal_Response(object):
  '''interface class with ncal_response Arduino sketch'''

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


edc_iniFile = 'ncal_wheel_ctrl_edc_daqd_ini_content.txt'

def generate_ini_file():
    now = datetime.datetime.now()
    edc_Path = '/opt/rtcds/anu/n1/softioc/ncal_wheel_ctrl/ini/'
    # edc_iniFile = 'torpedo_env_ctrl_edc_daqd_ini_content.txt'
    edc_f = open( edc_Path + edc_iniFile , "w")
    edc_f.writelines(["# Auto generated file by torpedo_env_ctrl_ss.py\n",
                      "# at " + now.strftime("%Y-%m-%d %H:%M:%S") + "\n",
                      "#\n"
                      "# Using the default parameters\n",
                      "[default]\n", 
                      "gain=1.00\n", 
                      "acquire=3\n", 
                      "dcuid=52\n", 
                      "ifoid=0\n", 
                      "datatype=4\n",
                      "datarate=16\n",
                      "offset=0\n",
                      "slope=1.0\n",
                      "units=undef\n",
                      "\n",
                      "#\n",
                      "# Following content lines to be manually added to the\n",
                      "# edc.ini file, which points to /opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini\n",
                      "# Then the standalone_edc service (rts-edc.service on n1fe1) and the daqd\n",
                      "# service (rts-daqd.service) on the n1fb10) will need to be restarted to\n",
                      "# the changes into effect.\n",
                      "\n"])

    for key in ncalDB.keys():
        edc_f.writelines("[" + ncalPrefix + key + "]\n")

    edc_f.close()

#cr = Ncal_Response(ARDUINO_SERIAL_PORT, SERIAL_PORT_BAUD)
#time.sleep(0.5)

def main():
  '''test the Arduino cmd_response interface'''

  print('Starting up ...')

  # Operate Continously
  print('---- generate .ini file content in  ----')
  print('---- ' + edc_iniFile + ' ----')
  generate_ini_file()

  # Setup the Serial interfaces
  global PERIOD_ms
  dr = Ncal_Response(HWSERIAL_PORT, SERIAL_PORT_BAUD)
  time.sleep(0.5)

  cr = Ncal_Response(ARDUINO_SERIAL_PORT, SERIAL_PORT_BAUD)
  time.sleep(0.5)

  # Start simple CA Server
  ncalServer = SimpleServer()
  ncalServer.createPV(ncalPrefix, ncalDB)
  ncalDriver = myDriver()

  # Tell systemd that our service is ready
  systemd.daemon.notify('READY=1')

  # Extracting Parameters from controller
  iaa = cr.request('?aa')
  # print('?aa ', iaa)
  ncalDriver.setParam('ANGULAR_ACCELERATION', float(iaa))

  isp = cr.request('?sp')
  # print('?sp ', isp)
  ncalDriver.setParam('ANGULAR_FREQUENCY_SETPOINT', float(isp))

  ien = cr.request('?en')
  # print('?en ', ien)
  ncalDriver.setParam('DRIVER_STATE', int(ien))

  ncalDriver.updatePVs()

  while True:
    ncalServer.process(0.1)

    ncalDriver.get_fast_data(dr)

    ncalDriver.get_driver_state(cr)
    ncalDriver.get_hole_numbers(cr)
    ncalDriver.get_id(cr)
    ncalDriver.get_setpoint_reached(cr)
    ncalDriver.get_version(cr)

    #cr.receive()
    ncalDriver.set_angular_acc(cr)
    ncalDriver.set_driver_state(cr)
    ncalDriver.set_setpoint(cr)
    #ncalDriver.read('ANGULAR_FREQUENCY_SETPOINT', cr)
    
    # Update content of the PVs
    #ncalDriver.updatePVs()
    




if __name__ == '__main__':
  main()