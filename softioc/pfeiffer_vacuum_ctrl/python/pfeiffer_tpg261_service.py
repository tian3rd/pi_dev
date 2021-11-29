#
# this service requires
# - pcaspy 
# included with aligo-cds-epics-linux-arm
#
# - pyepics
# included with aligo-cds-epics-linux-arm
# 
# - pylablib,
# https://pylablib.readthedocs.io/en/latest/install.html
#
# - python systemd
# https://github.com/torfsen/python-systemd-tutorial
#
# Installation 
# sudo mkdir /usr/local/lib/pfeiffer_tpg261_service/
# sudo cp python/pfeiffer_tpg261_service.py /usr/local/lib/pfeiffer_tpg261_service/
#
# location
# /usr/local/lib/pfeiffer_tpg261_service/pfeiffer_tpg261_service.py
#
# Set user and group to root
# sudo chown root:root /usr/local/lib/pfeiffer_tpg261_service/pfeiffer_tpg261_service.py
#
# Set to execution
# sudo chmod 644 /usr/local/lib/pfeiffer_tpg261_service/pfeiffer_tpg261_service.py

from pcaspy import Driver, SimpleServer
from pylablib.devices import Pfeiffer

import systemd.daemon
import datetime


gaugePrefix = 'N1:VAC-GAUGE_1_'

gaugeDB = {
    'ERROR'     : { 'type' : 'str' },
    'STATUS'    : { 'type' : 'str' },
    'UNITS'     : { 'type' : 'str' },
    'DISP_RES'  : { 'prec' : 0 },
    'TYPE'      : { 'type' : 'str' },
    'PRESSURE'  : { 'prec' : 2,
                    'scan' : 0.1},
}

edc_iniFile = 'pfeiffer_vacuum_ctrl_edc_daqd_ini_content.txt'
system_dir_name = 'pfeiffer_vacuum_ctrl'
script_name = 'pfeiffer_tpg261_service.py'

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()

    # FIX ME - see to use the read function,
    # instead of individual def
    # def read(self, reason):
    #     # self.get_data()
        
    #     if reason == 'ERROR':
    #         current_error = gauge.get_current_errors()
    #         value = current_error[0]
    #     else:
    #         value = self.getParam(reason)
    #     # self.setParam(reason, value)
    #     return value

    def get_units(self):
        # Get device units for indication/reading ("mbar", "torr", or "pa")
        units = gauge.get_units()
        self.setParam('UNITS', units)

    def get_display_resolution(self):
        # Get controller display resolution (number of digits)
        display_res = gauge.get_display_resolution()
        self.setParam('DISP_RES', display_res)

    def get_gauge_kind(self):
        # Get gauge type 
        gauge_type = gauge.get_gauge_kind()
        self.setParam('TYPE', gauge_type)

    def get_pressure(self):
        # Get a list of all present error messages.
        # If there are no errors, return a single-element list ["no_error"].
        current_error = gauge.get_current_errors()
        self.setParam('ERROR', *current_error)

        # Get channel status.
        # Can be "ok", "under" (underrange), "over" (overrange), 
        # "sensor_error", "sensor_off", "no_sensor", or "id_error".
        status = gauge.get_channel_status()
        self.setParam('STATUS', status)

        if status == 'ok':
            # Get current pressure and convert into the units
            # as per 'x.get_units()'
            pp = gauge.get_pressure(1,True)
            self.setParam('PRESSURE', pp)       


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

    for key in gaugeDB.keys():
        edc_file.writelines("[" + gaugePrefix + key + "]\n")

    edc_file.close()


if __name__ == '__main__':

    print('Starting up ...')

    # Operate Continously
    print('---- generate .ini file content in  ----')
    print('---- ' + edc_iniFile + ' ----')
    generate_ini_file()

    # Connect to Gauge controler
    gauge = Pfeiffer.TPG260("/dev/ttyUSB0")

    # Start simple CA Server
    server = SimpleServer()
    server.createPV(gaugePrefix, gaugeDB)
    driver = myDriver()

    # Tell systemd that our service is ready
    systemd.daemon.notify('READY=1')

    # process CA transactions
    while True:
        server.process(0.1)

        driver.get_pressure()
        driver.get_display_resolution()
        driver.get_gauge_kind()
        driver.get_units()

        # Update content of the PVs
        driver.updatePVs()


