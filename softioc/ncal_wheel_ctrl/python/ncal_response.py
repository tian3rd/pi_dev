#
#!/usr/bin/env python3
#
# Installation 
# sudo mkdir /usr/local/lib/ncal_wheel_ctrl_service
# sudo cp python/ncal_response.py /usr/local/lib/ncal_wheel_ctrl_service/ncal_wheel_ctrl.py
#
# location of this file
# /etc/systemd/system/ncal_wheel_ctrl_service.service
#
# Set user and group to root
# sudo chown root:root /usr/local/lib/ncal_wheel_ctrl_service/ncal_wheel_ctrl.py
#
# Set to execution
# sudo chmod 644 /usr/local/lib/ncal_wheel_ctrl_service/ncal_wheel_ctrl.py
#
# installing systemd in python, see https://github.com/torfsen/python-systemd-tutorial
# $ sudo apt-get install python-systemd python3-systemd



'''Exercise the Arduino ncal_response interface'''


import time
import datetime
import serial	# easy_install -U pyserial
import systemd.daemon
import threading

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
    'RAW_FREQ_MEAS_OL'           : { 'prec' : 3 },
    'ANGULAR_FREQ_MEAS_OL'       : { 'prec' : 3 },
    'PULL_FREQ'                  : { 'prec' : 2 },
    'PULSE_PER_SEC'              : { 'prec' : 3 },
    'ANG_FREQ_PID'               : { 'prec' : 3 },
    'ANGULAR_FREQUENCY_SETPOINT' : { 'prec' : 3 },
    'ANG_FREQ_SETP_REACHED'      : { 'prec' : 1 },
    'ANGULAR_ACCELERATION'       : { 'prec' : 3 },
    'NUMBER_HOLES_RB'            : { 'prec' : 3 },
    'DRIVER_STATE_RB'            : { 'prec' : 1 },
    'DRIVER_STATE'               : { 'prec' : 1 },
    'VERSION'                    : { 'type' : 'str',
                                     'scan' : 1},
    'ID'                         : { 'type' : 'str',
                                     'scan' : 1},
    'ANGULAR_FREQUENCY_SETPOINT_RB' : { 'prec' : 3}
}

edc_iniFile = 'ncal_wheel_ctrl_edc_daqd_ini_content.txt'
system_dir_name = 'ncal_wheel_ctrl'
script_name = 'ncal_wheel_ctrl.py'

lst = ['0','0','0','0','0','0','0']

class myDriver (Driver):
    def  __init__(self):
        super(myDriver, self).__init__()
        self.eid = threading.Event()
        self.tid = threading.Thread(target = self.get_fast_data) 
        self.tid.setDaemon(True)
        self.tid.start()
        self.static_read()


    def get_fast_data(self):
        while True:
            lst = dr.receive().split(',')                
            self.setParam('RAW_FREQ_MEAS', float(lst[0]))
            self.setParam('ANGULAR_FREQ_MEAS', float(lst[1]))
            self.setParam('RAW_FREQ_MEAS_OL', float(lst[2]))
            self.setParam('ANGULAR_FREQ_MEAS_OL', float(lst[3]))
            self.setParam('PULL_FREQ', float(lst[4]))
            self.setParam('PULSE_PER_SEC', float(lst[5]))
            self.setParam('ANG_FREQ_PID', float(lst[6]))
            self.updatePVs()

    def static_read(self):
        self.setParam('VERSION', cr.request('?v'))
        self.setParam('ID', cr.request('?id'))
        self.setParam('NUMBER_HOLES_RB', float(cr.request('?h')))
        self.setParam('ANGULAR_ACCELERATION', float(cr.request('?aa')))
        self.setParam('ANGULAR_FREQUENCY_SETPOINT', float(cr.request('?sp')))
        self.setParam('DRIVER_STATE_RB', float(cr.request('?en')))
        self.updatePVs()

    # def read(self, reason):
    #     # self.get_setpoint_reached()
        
    #     if reason == 'ANGULAR_FREQUENCY_SETPOINT_RB':
    #         value = float(cr.request('?sp'))
    #     else:
    #         value = self.getParam(reason)
    #     # self.setParam(reason, value)
    #     return value


    def write(self, reason, value):
        status = True
        self.get_setpoint_reached()

        if reason == 'ANGULAR_FREQUENCY_SETPOINT':
            isok = cr.request('!sp ' + str(value))
            if isok != 'Ok':
                status = False
                print('error: set_setpoint >' + isok)
        elif reason == 'DRIVER_STATE':
            isok = cr.request('!en ' + str(value))
            if isok == 'Ok':
                self.setParam('DRIVER_STATE_RB', float(cr.request('?en')))
            elif isok != 'Ok':
                status = False
                print('error: set_driver_state >' + isok)
        elif reason == 'ANGULAR_ACCELERATION':
            isok = cr.request('!aa ' + str(value))
            if isok != 'Ok':
                status = False
                print('error: set_angular_acc >' + isok)
        else:
            status = False

        if status:
            self.setParam(reason, float(value))
        return status

    def get_setpoint_reached(self):
        _as = cr.request('?as')
        self.setParam('ANG_FREQ_SETP_REACHED', float(_as))
        self.updatePVs()


class ncal_response(object):
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


def generate_ini_file():
    '''Generate the .INI file content'''

    now = datetime.datetime.now()
    edc_Path = '/opt/rtcds/anu/n1/softioc/' + system_dir_name + '/ini/'
    # edc_iniFile = 'torpedo_env_ctrl_edc_daqd_ini_content.txt'

    edc_file = open( edc_Path + edc_iniFile , "w")
    edc_file.writelines(["# Auto generated file by " + script_name + "\n",
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
                      "# Following content lines to be manually added to the edc.ini file,\n",
                      "# which points to /opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini\n",
                      "#\n",
                      "# Then the standalone_edc service (rts-edc.service on n1fe1) and the daqd\n",
                      "# service (rts-daqd.service) on the n1fb10) will need to be restarted to\n",
                      "# the changes into effect.\n",
                      "\n"])

    for key in ncalDB.keys():
        edc_file.writelines("[" + ncalPrefix + key + "]\n")

    edc_file.close()


# Setup the Serial interfaces
cr = ncal_response(ARDUINO_SERIAL_PORT, SERIAL_PORT_BAUD)
time.sleep(0.5)

dr = ncal_response(HWSERIAL_PORT, SERIAL_PORT_BAUD)
time.sleep(0.5)


def main():
    '''the Arduino ncal_response interface'''

    print('---- Starting up ----')

    # Operate Continously
    print('---- generate .ini file content in  ----')
    print('---- ' + edc_iniFile + ' ----')
    generate_ini_file()

    print('---- sleep for 2 seconds ----')
    time.sleep(2)

    # Start simple CA Server
    ncalServer = SimpleServer()
    ncalServer.createPV(ncalPrefix, ncalDB)
    ncalDriver = myDriver()

    # Tell systemd that our service is ready
    systemd.daemon.notify('READY=1')

    print('---- Entering Server loop ----')

    while True:
        ncalServer.process(0.1)


if __name__ == '__main__':
    main()
