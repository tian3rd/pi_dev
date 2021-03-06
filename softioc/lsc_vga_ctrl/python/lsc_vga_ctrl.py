import os.path
import datetime
import systemd.daemon
from pcaspy import Driver, SimpleServer
from time import sleep

# local script
import busworks
# for changes in busworks.py to reload to take effect immediately (debugging purpose)
import importlib
importlib.reload(busworks)

# Version
major = '0'
minor = '1'
patch = 'a'
version = major + '.' + minor + '.' + patch

# static ip addresses of acromag xt1111 units (it can be set up using Windows client software), can support 1 to 4 devices
device_addresses = ['192.168.1.100', '192.168.1.101']

script_name = os.path.basename(__file__)

print('--- Running ' + script_name + ' ---')
# print(__file__)

# EPICS channel for the VGA control
IFO = 'N1'
SYSTEM = 'LSC'
SUBSYS = 'VGA'

# 'N1:LSC-VGA_'

busPrefix = IFO + ':' + SYSTEM + '-' + SUBSYS + '_'

db_type_int = {'type': 'int'}
db_type_enum = {'type': 'enum', 'enums': ['0', '1']}
# log error messages longer than 40 chars
db_type_str = {'type': 'char', 'count': 300}

num_devices = 4
devices = ['CHAN_' + str(_) + '_' for _ in range(num_devices)]
gain_channel = 'GAINS'
gain_error = 'GAINS_ERROR'
filter_channel = 'FILTERS'
filter_error = 'FILTERS_ERROR'
# because filter1-3 corresponds to xt1111 i/o ports 04-06, so here use FILTER04-06 to refer to filter1-3
filter_channels = ['FILTER0' + str(_) for _ in range(4, 7)]
gain_readback = 'GAINS_RB'
filter_readback = 'FILTERS_RB'


def generate_bus_db():
    '''
    generate the EPICS database with device channel names and channel types
    Input:
        devices: list of device names
        gain_channel: name of the channel for the gains ()
        filter_channel: name of the channel for the filter
        filter_channels: list of names of the channels for the filters (i/o port 4-7)
    '''
    busDB = {}
    for device in devices:
        busDB[device + gain_channel] = db_type_int
        busDB[device + filter_channel] = db_type_int
        busDB[device + gain_readback] = db_type_int
        busDB[device + filter_readback] = db_type_int
        busDB[device + gain_error] = db_type_str
        busDB[device + filter_error] = db_type_str
        for channel in filter_channels:
            busDB[device + channel] = db_type_enum
    return busDB


busDB = generate_bus_db()

# # uncomment this block if you want to explictly specify the channel and type for busDB
# busDB_explicit = {'CHAN_0_GAINS': {'type': 'int'},
#                 'CHAN_0_FILTERS': {'type': 'int'},
#                 'CHAN_0_GAINS_RB': {'type': 'int'},
#                 'CHAN_0_FILTERS_RB': {'type': 'int'},
#                 'CHAN_0_GAINS_ERROR': {'type': 'char', 'count': 300},
#                 'CHAN_0_FILTERS_ERROR': {'type': 'char', 'count': 300},
#                 'CHAN_0_FILTER04': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_0_FILTER05': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_0_FILTER06': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_1_GAINS': {'type': 'int'},
#                 'CHAN_1_FILTERS': {'type': 'int'},
#                 'CHAN_1_GAINS_RB': {'type': 'int'},
#                 'CHAN_1_FILTERS_RB': {'type': 'int'},
#                 'CHAN_1_GAINS_ERROR': {'type': 'char', 'count': 300},
#                 'CHAN_1_FILTERS_ERROR': {'type': 'char', 'count': 300},
#                 'CHAN_1_FILTER04': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_1_FILTER05': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_1_FILTER06': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_2_GAINS': {'type': 'int'},
#                 'CHAN_2_FILTERS': {'type': 'int'},
#                 'CHAN_2_GAINS_RB': {'type': 'int'},
#                 'CHAN_2_FILTERS_RB': {'type': 'int'},
#                 'CHAN_2_GAINS_ERROR': {'type': 'char', 'count': 300},
#                 'CHAN_2_FILTERS_ERROR': {'type': 'char', 'count': 300},
#                 'CHAN_2_FILTER04': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_2_FILTER05': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_2_FILTER06': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_3_GAINS': {'type': 'int'},
#                 'CHAN_3_FILTERS': {'type': 'int'},
#                 'CHAN_3_GAINS_RB': {'type': 'int'},
#                 'CHAN_3_FILTERS_RB': {'type': 'int'},
#                 'CHAN_3_GAINS_ERROR': {'type': 'char', 'count': 300},
#                 'CHAN_3_FILTERS_ERROR': {'type': 'char', 'count': 300},
#                 'CHAN_3_FILTER04': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_3_FILTER05': {'type': 'enum', 'enums': ['0', '1']},
#                 'CHAN_3_FILTER06': {'type': 'enum', 'enums': ['0', '1']}}

# print('--- Generating EPICS database ---')
# print(busDB)

ini_file_name = 'lsc_vga_ctrl_ini_content.txt'
# len(python/) == 7
ini_file_dirpath_local_write = os.path.dirname(
    os.path.realpath(__file__))[:-7] + '/ini/'
ini_file_dirpath_rpi = '/opt/rtcds/anu/n1/softioc/lsc_vga_ctrl/ini/'


def generate_ini_file(ini_file_dirpath, busDB):
    '''
    generate the ini file with default parameters and the busDB attributes
    Input:
        ini_file_dirpath: directory path to write the ini file
        busDB: dictionary with device channel names and channel types
    '''
    now = datetime.datetime.now()
    with open(ini_file_dirpath + ini_file_name, 'w') as ini_file:
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
                             "#\n",
                             "#\n",
                             "# Following content lines to be manually added to the\n",
                             "# edc.ini file, which points to /opt/rtcds/anu/n1/chans/daq/N1FE1_EDC.ini\n",
                             "# Then the standalone_edc service (rts-edc.service on n1fe1) and the daqd\n",
                             "# service (rts-daqd.service on the n1fb10) will need to be restarted to\n",
                             "# the changes into effect.\n",
                             "#\n"])
        for key in busDB.keys():
            ini_file.writelines("[" + busPrefix + key + "]\n")
    ini_file.close()


# print('--- Writing EPICS database to ' + ini_file_dirpath_local_write + ' ---')
# print('--- Writing EPICS database to ' + ini_file_dirpath_rpi + ' ---')

# print(busDB.keys())


class MyDriver(Driver):
    def __init__(self, device_addresses):
        super().__init__()
        # connect to busworks XT1111 in initialization
        self.buses = [busworks.BusWorksXT1111(
            address=address, port=502, num_chns=16) for address in device_addresses]
        # (self.buses[_].start() for _ in range(len(self.buses)))
        for bus in self.buses:
            bus.start()
        self.gains_error = ''
        self.gerror = False
        self.filters_error = ''
        self.ferror = False

    def read(self, reason):
        if reason in ['CHAN_' + str(_) + '_GAINS' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            value = self.buses[device_index].get_gains()
        if reason in ['CHAN_' + str(_) + '_GAINS_ERROR' for _ in range(4)]:
            value = self.gains_error
        if reason in ['CHAN_' + str(_) + '_GAINS_RB' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            value = self.buses[device_index].get_readback_gains()
        if reason in ['CHAN_' + str(_) + '_FILTERS' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            value = self.buses[device_index].get_filters()
        if reason in ['CHAN_' + str(_) + '_FILTERS_ERROR' for _ in range(4)]:
            value = self.filters_error
        if reason in ['CHAN_' + str(_) + '_FILTERS_RB' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            value = self.buses[device_index].get_readback_filters()
        # FILTER04-07 are for choice buttons
        if reason in ['CHAN_' + str(i) + '_FILTER0' + str(j) for i in range(4) for j in range(4, 7)]:
            device_index = int(reason.split('_')[1])
            channel_index = int(reason[-1])
            value = self.buses[device_index].get_filters_in_binary(
                channel_index)
        self.setParam(reason, value)
        return value

    def write(self, reason, value):
        if reason in ['CHAN_' + str(_) + '_GAINS' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            try:
                self.buses[device_index].set_gains(value)
                self.gerror = False
                self.gains_error = ''
                self.setParam(reason, value)
            except Exception as e:
                print('Error in setting GAINS: {}'.format(str(e)))
                self.gerror = True
                self.gains_error = str(e)
            finally:
                self.read(reason + '_ERROR')
                self.read(reason)
                self.read(reason + '_RB')
                self.updatePVs()
        if reason in ['CHAN_' + str(i) + '_FILTER0' + str(j) for i in range(4) for j in range(4, 7)]:
            device_index = int(reason.split('_')[1])
            channel_index = int(reason[-1])
            assert self.buses[device_index].read_registers(
            )[1] >= 8, "Device " + str(device_index) + " ENABLE should be on!"
            filter_str = bin(self.buses[device_index].read_registers()[1])[
                2:][::-1]
            if str(value) != filter_str[channel_index - 4]:
                filter_str = filter_str[:(
                    channel_index - 4)] + str(value) + filter_str[(channel_index - 4) + 1:]
            filter_updated = int(filter_str[::-1], 2)
            try:
                self.buses[device_index].set_filter_channels(filter_updated)
                self.ferror = False
                self.filters_error = ''
                self.setParam(reason, value)
            except Exception as e:
                print('Error in setting FILTERS: {}'.format(str(e)))
                self.ferror = True
                self.filters_error = str(e)
            finally:
                self.read(reason[:-2] + 'S_ERROR')
                self.read(reason[:-2] + 'S')
                self.read(reason[:-2] + 'S_RB')
                self.updatePVs()


if __name__ == '__main__':
    print('--- generate .ini file content in ' + ini_file_name + ' ---')
    # use _local_write for local testing and debugging
    generate_ini_file(ini_file_dirpath_local_write, busDB)
    # use _rpi for service on rpi server (in /etc/systemd/system/lsc_vga_ctrl_service.service)
    # generate_ini_file(ini_file_dirpath_rpi, busDB)

    print('--- now starting server ---')

    # when restarting rpi, give it time to load all packages, otherwise the service has errors
    sleep(1)

    server = SimpleServer()
    server.createPV(busPrefix, busDB)

    driver = MyDriver(device_addresses)

    # Tell systemd that our service is ready
    systemd.daemon.notify('READY=1')

    while True:
        server.process(0.1)
