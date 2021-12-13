from pymodbus.client.sync import ModbusTcpClient
from time import sleep


class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class BusWorksXT1111(object):
    """
    An object written to facilitate the control of an ACROMAG BusWorks XT1111-000 through a TCP connection. 
    XT1111-000 has a default static address of 192.168.1.100 with 16 i/o channels.
    Port 502 is the default port used for modbus communication.
    """

    def __init__(self, address='192.168.1.100', port=502, num_chns=16):
        # IP-number of the device
        self.address = address
        # Port to use
        self.port = port
        # Number of channels of the device
        self.num_chns = num_chns
        # Time between updating the registers of device, set default as 0.05s. E.g., set gains/filters
        self.dt = 0.05

        # self.port_status = [0 for _ in range(4)]

    @property
    def address(self):
        '''
        The IP-address of the device. Must be a string.
        '''
        return self._address

    @address.setter
    def address(self, value):
        if not isinstance(value, str):
            raise BaseException(
                ('Address must be a string. Input is of type {}').format(type(value)))
        self._address = value

    @property
    def port(self):
        '''
        Port to use.
        '''
        return self._port

    @port.setter
    def port(self, value):
        if not isinstance(value, int):
            raise BaseException(
                'Port must be an int. Input is of type {}'.format(type(value)))
        self._port = value

    @property
    def num_chns(self):
        '''
        Number of output channels of the device.
        '''
        return self._num_chns

    @num_chns.setter
    def num_chns(self, value):
        if not isinstance(value, int):
            raise BaseException(
                'num_chns must be an integer, not {}'.format(type(value)))
        self._num_chns = value

    def start(self):
        '''
        Establishes the TCP connection between the computer and the device.
        '''
        self.XT1111 = ModbusTcpClient(self.address, port=self.port)
        # use i/o channel 07 as device on/off status indicator
        self.set_device_on()

    def stop(self, reset=True):
        '''
        Stops the TCP connection between the computer and the device. If reset is True, the registers of all channels are set to 0.
        '''
        if reset:
            self.XT1111.write_registers(0, 0)
            self.XT1111.write_registers(1, 0)
            self.XT1111.write_registers(2, 0)
            self.XT1111.write_registers(3, 0)
        self.XT1111.close()

    def read_registers(self, start=0, num_channels=4):
        '''
        Reads what on/off signals that are written to the channels.
        row 0 corresponds to i/o 00 to 03; row 1: i/o 04 to 07; row 2: i/o 08 to 11; row 3: i/o 12 to 15 ; the last channel is heartbeat channel (xt1111 manual page 33-34)
        Inputs:
        -------
        start      - first row of channels to read from
        num_channels  - last row of channels to read from.
        '''
        if not isinstance(start, int) or not isinstance(num_channels, int):
            raise BaseException(
                "Start row should be within [0, 1, 2, 3], end: [1, 2, 3, 4]")
        # use read_input_registers intead of read_holding_registers to keep track of the i/o change
        out = self.XT1111.read_input_registers(start, num_channels)
        # self.port_status = out.registers
        return out.registers

    def print_register_states(self):
        '''
        print channel 00 to 15 in the same layout as in the windows client for XT1111:
        ch00 | ch01 | ch02 | ch03 
        ch04 | ch05 | ch06 | ch07
        ch08 | ch09 | ch10 | ch11
        ch12 | ch13 | ch14 | ch15
        '''
        states = self.read_registers()
        # states = self.XT1111.read_input_registers(0, 4).registers
        row = 0
        for state in states:
            state = bin(state)[2:]
            signals = '0' * (4 - len(state)) + state
            print('Row {0} (i/o {1: <2} - {2: <2}): {3} | {4} | {5} | {6}'.format(row+1,
                  row * 4, row * 4 + 3, signals[3], signals[2], signals[1], signals[0]))
            row += 1

    def turnon_channels(self, channels: list):
        '''
        Turns on the channels specified in the list.
        Inputs:
        -------
        channels - List of channels to turn on. E.g., [0, 1, 9] turns on i/o 00, 01, 09 on XT1111 
        '''
        pass

    def set_gains_and_filters(self, gains=None, filters=None, le=None):
        '''
        Sets the gains and filters of the channels.
        Inputs:
        -------
        gains        - 0 to 45dB in a step of 3
        filters      - List of filters state: 1 indicates on, 0 indicates off
        EN           - Set the LE/EN voltage to 1 (on) or 0 (off)
        '''
        if gains is None:
            self.gains = 0
        else:
            self.gains = gains
        if filters is None:
            self.filters = '000'
        else:
            self.filters = filters
        if le is None:
            self.le = 1
        else:
            self.le = le
        self.set_gains(self.gains)
        self.set_filters(self.filters, self.le)

    def set_gains(self, gains):
        '''
        Sets the gains for channel 00 to 03
        Inputs:
        -------
        gains: 0 to 45 in decimal number with a step of 3dB (Gains: i/o 00: 24dB; i/o 01: 12dB; i/o 02: 6dB; i/o 03: 3dB.)
        '''
        if not isinstance(gains, int) or gains % 3 != 0 or gains < 0 or gains > 45:
            raise BaseException(
                'Gains must be a multiple of 3 and between 0 and 45.')
        bins = bin(gains//3)[2:]
        bins = '0' * (4 - len(bins)) + bins
        first_four_ios = int(bins[::-1], 2)
        # 0 is the starting address for the first four i/o; 1 is the starting address for i/o 4 to 7; etc.
        self.XT1111.write_register(0, first_four_ios)
        sleep(self.dt)

    def set_gain_channels(self, row0_value):
        '''
        Sets channels from 00 to 03 using the decimal value
        Inputs:
        -------
        row0_value: value of the first row (row0) ranging from 0 to 15
        '''
        if not isinstance(row0_value, int) or row0_value < 0 or row0_value > 15:
            raise BaseException(
                'row 0 should have a value between 0 and 15 inclusive')
        self.XT1111.write_register(0, row0_value)

    def get_gains(self) -> int:
        '''
        return gains in decimal number
        e.g. bus.get_gains() returns 42, 3, ...
        '''
        gains_bin_value = bin(self.read_registers()[0])[2:][::-1]
        self.gains = int(gains_bin_value + '0' *
                         (4 - len(gains_bin_value)), 2) * 3
        return self.gains

    def get_gains_in_binary(self, channel) -> int:
        '''
        return the set signal of 1 or 0 corresponding to the channel:
        channel 00: 24dB; channel 01: 12dB; channel 02: 6dB; chennel 03: 3dB
        e.g. if the gain is 15dB (bus.get_gains() == 10/'0|1|0|1' ch00 to ch03), so bus.get_gains_in_binary(0) == 0, bus.get_gains_in_binary(1) == 1
        Input:
        channel: the channel index on row 0 ranging from 00 to 03
        '''
        if not isinstance(channel, int) or channel < 0 or channel > 3:
            raise BaseException('channel should be an integer between 0 and 3')
        gains_bin_value = bin(self.read_registers()[0])[2:][::-1]
        gains_in_binary = gains_bin_value + '0' * (4 - len(gains_bin_value))
        return int(gains_in_binary[channel])

    def set_filters(self, filters, le=1):
        '''
        i/o 04 controls zero pole filter 1: pz1; i/o 05 controls zero pole filter 2: pz2; i/o 06 controls zero pole filter 3: pz3
        '''
        if not isinstance(filters, str) or len(filters) != 3 or not all(x in '01' for x in filters):
            raise BaseException(
                'Filters must be a string of three elements (0 or 1). e.g, "001", "000", etc.')
        second_four_ios = int((filters+str(le))[::-1], 2)
        self.XT1111.write_register(1, second_four_ios)
        sleep(self.dt)

    def set_filter_channels(self, row1_value):
        '''
        Sets channels from 04 to 07 (including on/off for ch07) using the decimal value
        Inputs:
        -------
        row1_value: value of the second row (row1) ranging from 0 to 15
        '''
        if not isinstance(row1_value, int) or row1_value < 0 or row1_value > 15:
            raise BaseException(
                'row 1 should have a value between 0 and 15 inclusive')
        self.XT1111.write_register(1, row1_value)

    def set_device_on(self):
        '''
        Set channel 07 (on/off status channel) on whenever there's change on gains or filters
        '''
        row1_value = self.read_registers()[1]
        if row1_value < 8:
            row1_value += 8
        self.set_filter_channels(row1_value)

    def get_filters(self) -> str:
        '''
        return a str of length 3 to indicate status for filter 1 to 3, e.g., "001" means filter 1, 2 are off, and filter 3 is on.
        '''
        filters_le_bin_value = bin(self.read_registers()[1])[2:]
        # in case le is 0: off, add '0's in front
        self.filters = ('0' * (4 - len(filters_le_bin_value)) +
                        filters_le_bin_value)[::-1][:3]
        return self.filters
        # return int(''.join(map(str, self.filters)), 2)

    def get_filters_in_binary(self, channel) -> int:
        '''
        return the signal of 1 or 0 corresponding to channel:
        channel 04: filter 1; channel 05: filter 2; channel 06: filter3
        Input:
        -------
        channel: the channel index on row 1 from 04 to 06
        '''
        if not isinstance(channel, int) or channel < 4 or channel > 6:
            raise BaseException('filter channel should be 4, 5, or 6')
        filters_bin_value = bin(self.read_registers()[1])[2:][::-1]
        filters_in_binary = '0' * \
            (4 - len(filters_bin_value)) + filters_bin_value
        return int(filters_in_binary[channel - 4])

    def get_le(self) -> int:
        '''
        return the state of LE: 0 is off, 1 is on. Since LE is channel 07, so if it's on, the second register is greater of equal to 2**3.
        '''
        return 1 if self.read_registers()[1] >= 8 else 0

    def get_readbacks(self) -> str:
        '''
        return a string representing the decimal values for row 2 and row 3 joined by -
        e.g., 4-0 means channel 09 is on, others are off
        '''
        readbacks = self.read_registers()[2:]
        return '-'.join(map(str, readbacks))

    def get_readback(self, channel) -> int:
        '''
        return an on/off for channel 08 to 15
        Input:
        -------
        channel: the channel index, ranging from 08 to 15
        '''
        if not isinstance(channel, int) or channel < 8 or channel > 15:
            raise BaseException(
                'readback channel should be within 8 to 15 inclusive')
        row2_bin_value = bin(self.read_registers()[2])[2:][::-1]
        row3_bin_value = bin(self.read_registers()[3])[2:][::-1]
        row2_in_binary = row2_bin_value + '0' * (4 - len(row2_bin_value))
        row3_in_binary = row3_bin_value + '0' * (4 - len(row3_bin_value))
        if channel < 12:
            return int(row2_in_binary[channel - 8])
        else:
            return int(row3_in_binary[channel - 12])
