from pcaspy import Driver, SimpleServer
import Pfeiffer

import systemd.daemon
import datetime
import os.path
import threading


gaugePrefix = 'N1:VAC-GAUGE_1_'

gaugeDB = {
    'ERROR': {'type': 'str', },
    'STATUS': {'type': 'str', },
    'UNITS': {'type': 'str', },
    'DISP_RES': {'prec': 0, },
    'TYPE': {'type': 'str', },
    'PRESSURE': {'prec': 2, 'scan': 0.1, },
}

script_name = os.path.basename(__file__)
edc_iniFile = 'pfeiffer_rs232_ctrl_edc_ini_content.txt'
# -7: len('python/') = 7
ini_file_dirpath_local_write = os.path.dirname(
    os.path.realpath(__file__))[:-7] + '/ini/'
ini_file_dirpath_rpi = '/opt/rtcds/anu/n1/softioc/pfeiffer_rs232_ctrl/ini/'


def generate_ini_file(ini_file_dirpath, gaugeDB):
    now = datetime.datetime.now()
    with open(ini_file_dirpath + edc_iniFile, 'w') as ini_file:
        ini_file.writelines(["# Auto generated file by " + script_name + "\n",
                             "# at " +
                             now.strftime("%Y-%m-%d %H:%M:%S") + "\n",
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
            ini_file.writelines("[" + gaugePrefix + key + "]\n")
    ini_file.close()


class myDriver(Driver):
    def __init__(self, device_address='/dev/ttyUSB1'):
        super().__init__()
        # https://pylablib.readthedocs.io/en/stable/.apidoc/pylablib.devices.Pfeiffer.html?highlight=get_gauge_kind
        self.gauge = Pfeiffer.TPG261(device_address)
        self.status = 'ok'
        self.channels = ['ERROR', 'STATUS',
                         'UNITS', 'DISP_RES', 'TYPE', 'PRESSURE']
        self.tid = threading.Thread(target=self.run)
        self.tid.setDaemon(True)
        self.tid.start()

    def read_channels(self, reason):
        # value = ''
        if reason == 'ERROR':
            # if self.status == 'ok':
            if 'ok' in self.status:
                value = 'No Error'
            else:
                current_errors = self.gauge.get_current_errors()
                value = current_errors[0]
        if reason == 'STATUS':
            self.status = self.gauge.get_channel_status()
            value = self.status
        if reason == 'UNITS':
            value = self.gauge.get_units()
        if reason == 'DISP_RES':
            value = self.gauge.get_display_resolution()
        if reason == 'TYPE':
            value = self.gauge.get_gauge_kind()
        # only get pressure when status is ok?
        if reason == 'PRESSURE':
            # if self.status == 'ok':
            if 'ok' in self.status:
                # value = self.gauge.get_pressure(channel=1, display_units=True)
                value = self.gauge.get_pressure(1, True)
            else:
                value = 8888
        self.setParam(reason, value)
        return value

    def run(self):
        while True:
            for reason in self.channels:
                print("READING: ", reason)
                self.read_channels(reason)
            self.updatePVs()


if __name__ == '__main__':
    print('Starting', script_name)

    print('Generating ini file content in ' + edc_iniFile)
    generate_ini_file(ini_file_dirpath_local_write, gaugeDB)

    print('Starting server')
    server = SimpleServer()
    server.createPV(gaugePrefix, gaugeDB)
    driver = myDriver()

    systemd.daemon.notify('READY=1')

    while True:
        server.process(0.1)
