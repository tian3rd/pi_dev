import os.path
import datetime
from pcaspy import Driver, SimpleServer

# local script
import busworks
import importlib
importlib.reload(busworks)

# Version
major = '0'
minor = '1'
patch = 'a'
version = major + '.' + minor + '.' + patch

script_name = os.path.basename(__file__)

print('--- Running ' + script_name + ' ---')
# print(__file__)

# EPICS channel for the VGA control
IFO = 'N1'
SYSTEM = 'LSC'
SUBSYS = 'VGA'

busPrefix = IFO + ':' + SYSTEM + '-' + SUBSYS + '_'

db_type_int = {'type': 'int'}
db_type_enum = {'type': 'enum', 'enums': ['0', '1']}

num_devices = 4
devices = ['CHAN_' + str(_) + '_' for _ in range(num_devices)]
gain_channel = 'GAINS'
filter_channel = 'FILTERS'
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
        for channel in filter_channels:
            busDB[device + channel] = db_type_enum
    return busDB


busDB = generate_bus_db()

# # uncomment this block if you want to explictly specify the channel and type for busDB
# busDB_explicit = {'CHAN_0_GAINS': {'type': 'int'}, 'CHAN_0_FILTERS': {'type': 'int'}, 'CHAN_0_GAINS_RB': {'type': 'int'}, 'CHAN_0_FILTERS_RB': {'type': 'int'}, 'CHAN_0_FILTER04': {'type': 'enum'}, 'CHAN_0_FILTER05': {'type': 'enum'}, 'CHAN_0_FILTER06': {'type': 'enum'}, 'CHAN_0_FILTER07': {'type': 'enum'},
#                   'CHAN_1_GAINS': {'type': 'int'}, 'CHAN_1_FILTERS': {'type': 'int'}, 'CHAN_1_GAINS_RB': {'type': 'int'}, 'CHAN_1_FILTERS_RB': {'type': 'int'}, 'CHAN_1_FILTER04': {'type': 'enum'}, 'CHAN_1_FILTER05': {'type': 'enum'}, 'CHAN_1_FILTER06': {'type': 'enum'}, 'CHAN_1_FILTER07': {'type': 'enum'},
#                   'CHAN_2_GAINS': {'type': 'int'}, 'CHAN_2_FILTERS': {'type': 'int'}, 'CHAN_2_GAINS_RB': {'type': 'int'}, 'CHAN_2_FILTERS_RB': {'type': 'int'}, 'CHAN_2_FILTER04': {'type': 'enum'}, 'CHAN_2_FILTER05': {'type': 'enum'}, 'CHAN_2_FILTER06': {'type': 'enum'}, 'CHAN_2_FILTER07': {'type': 'enum'},
#                   'CHAN_3_GAINS': {'type': 'int'}, 'CHAN_3_FILTERS': {'type': 'int'}, 'CHAN_3_GAINS_RB': {'type': 'int'}, 'CHAN_3_FILTERS_RB': {'type': 'int'}, 'CHAN_3_FILTER04': {'type': 'enum'}, 'CHAN_3_FILTER05': {'type': 'enum'}, 'CHAN_3_FILTER06': {'type': 'enum'}, 'CHAN_3_FILTER07': {'type': 'enum'}}

# print('--- Generating EPICS database ---')
# print(busDB)

ini_file_name = 'lsc_vga_ctrl_ini_content.txt'
# len(python/) == 7
ini_file_dirpath_local_write = os.path.dirname(
    os.path.realpath(__file__))[:-7] + '/ini/'
ini_file_dirpath_rpi = 'opt/rtcds/anu/n1/softioc/lsc_vga_ctrl/ini/'


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


print('--- Writing EPICS database to ' + ini_file_dirpath_local_write + ' ---')
print('--- Writing EPICS database to ' + ini_file_dirpath_rpi + ' ---')

generate_ini_file(ini_file_dirpath_local_write, busDB)

print(busDB.keys())


class MyDriver(Driver):
    def __init__(self, device_addresses):
        super().__init__()
        # connect to busworks XT1111 in initialization
        self.buses = [busworks.BusWorksXT1111(
            address=address, port=502, num_chns=16) for address in device_addresses]
        # (self.buses[_].start() for _ in range(len(self.buses)))
        for bus in self.buses:
            bus.start()

    def read(self, reason):
        if reason in ['CHAN_' + str(_) + '_GAINS' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            value = self.buses[device_index].get_gains()
            self.setParam(reason, value)
            return value
        if reason in ['CHAN_' + str(_) + '_GAINS_RB' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            value = self.buses[device_index].get_readback_gains()
            self.setParam(reason, value)
            return value
        if reason in ['CHAN_' + str(_) + '_FILTERS' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            value = self.buses[device_index].get_filters()
            self.setParam(reason, value)
            return value
        if reason in ['CHAN_' + str(_) + '_FILTERS_RB' for _ in range(4)]:
            device_index = int(reason.split('_')[1])
            value = self.buses[device_index].get_readback_filters()
            self.setParam(reason, value)
            return value
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
                self.setParam(reason, value)
                self.updatePVs()
            except Exception as e:
                print(str(e))
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
            self.buses[device_index].set_filter_channels(filter_updated)
            self.setParam(reason, value)
            self.updatePVs()

    def read_database(self):
        # for key in busDB.keys():
        #     self.read(key)
        # self.updatePVs()
        self.read('CHAN_0_GAINS')
        self.read('CHAN_0_GAINS_RB')
        self.read('CHAN_0_FILTERS')
        self.read('CHAN_0_FILTERS_RB')
        (self.read('CHAN_0_FILTER0' + str(_)) for _ in range(4, 7))


if __name__ == '__main__':
    print('--- generate .ini file content in ' + ini_file_name + ' ---')
    generate_ini_file(ini_file_dirpath_local_write, busDB)

    print('--- now starting server ---')

    server = SimpleServer()
    server.createPV(busPrefix, busDB)
    # test 1 device for now
    device_addresses = ['192.168.1.100']
    driver = MyDriver(device_addresses)

    while True:
        server.process(0.1)
        driver.updatePVs()
        driver.read_database()
