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
# sudo cp pfeiffer_tpg261_service.py /usr/local/lib/pfeiffer_tpg261_service/
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
# from epics import caget, caput, cainfo, PV

import systemd.daemon
import threading


gaugePrefix = 'N1:VAC-GAUGE_1_'

gaugeDB = {
    'ERROR'     : { 'type' : 'str' },
    'STATUS'    : { 'type' : 'str' },
    'UNITS'     : { 'type' : 'str' },
    'DISP_RES'  : { 'prec' : 0 },
    'TYPE'      : { 'type' : 'str' },
    'PRESSURE'  : { 'prec' : 2, },
}

class myDriver(Driver):
    def  __init__(self):
        super(myDriver, self).__init__()
        # self.eid = threading.Event()
        # self.tid = threading.Thread(target = self.get_data) 
        # self.tid.setDaemon(True)
        # self.tid.start()
 
    def read(self, reason):
        # self.get_data()
        
        if reason == 'ERROR':
            current_error = gauge.get_current_errors()
            value = current_error[0]
            # self.setParam(reason, *value)
        elif reason == 'STATUS':
            value = gauge.get_channel_status()
            # self.setParam(reason, value)
        elif reason == 'UNITS':
            value = gauge.get_units()
            # self.setParam(reason, value)
        elif reason == 'DISP_RES':
            value = gauge.get_display_resolution()
            # self.setParam(reason, value)
        elif reason == 'TYPE':
            value = gauge.get_gauge_kind()
            # self.setParam(reason, value)
        elif reason == 'PRESSURE':
            value = gauge.get_pressure(1,True)
            # self.setParam(reason, value)
        else:
            value = self.getParam(reason)
        # self.setParam(reason, value)
        return value

    def get_data(self):
        self.get_pressure()
        self.get_display_resolution()
        self.get_gauge_kind()
        self.get_units()
        self.updatePVs()

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

# Connect to Gauge controler
gauge = Pfeiffer.TPG260("/dev/ttyUSB0")

if __name__ == '__main__':

    print('Starting up ...')

    # Connect to Gauge controler
    # gauge = Pfeiffer.TPG260("/dev/ttyUSB0")

    # Start simple CA Server
    server = SimpleServer()
    server.createPV(gaugePrefix, gaugeDB)
    driver = myDriver()

    # Tell systemd that our service is ready
    systemd.daemon.notify('READY=1')

    # process CA transactions
    while True:
        server.process(0.1)

        # driver.get_pressure()
        # driver.get_current_errors()
        # driver.get_channel_status()
        # driver.get_display_resolution()
        # driver.get_gauge_kind()
        # driver.get_units()

        # # Update content of the PVs
        # driver.updatePVs()


