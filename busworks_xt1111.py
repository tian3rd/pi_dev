from pymodbus.client.sync import ModbusTcpClient

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
            
    @property
    def address(self):
        '''
        The IP-address of the device. Must be a string.
        '''
        return self._address
    @address.setter
    def address(self, value):
        if not isinstance(value, str):
            raise BaseException(('Address must be a string. Input is of type {}').format(type(value)))
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
            raise BaseException('Port must be an int. Input is of type {}'.format(type(value)))
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
            raise BaseException('num_chns must be an integer, not {}'.format(type(value)))
        self._num_chns = value
        
    def start(self):
        '''
        Establishes the TCP connection between the computer and the device.
        '''
        self.XT1111 = ModbusTcpClient(self.address, port=self.port)
        
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
        
    def read_registers(self, start_ch=1, num_channels=4):
        '''
        Reads what integers that are written to the channels.
        Inputs:
        -------
        start_ch      - Lowest channel to read from
        num_channels  - Number of channels to read. 
        '''
        out = self.XT1111.read_holding_registers(start_ch, num_channels)
        return out.registers

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
        if filters is None:
            self.filters = [0, 0, 0]
        if le is None:
            self.le = 1
        self.set_gains(gains)
        self.set_filters(filters)
        
    def set_gains(self, gains):
        '''
        Gains: i/o 00: 24dB; i/o 01: 12dB; i/o 02: 6dB; i/o 03: 3dB.
        '''
        if gains % 3 != 0 or gains < 0 or gains > 45:
            raise BaseException('Gains must be a multiple of 3 and between 0 and 45.')
        first_four_ios = int(bin(gains//3)[-4:][::-1], 2)
        # 0 is the starting address for the first four i/o; 1 is the starting address for i/o 4 to 7; etc.
        self.XT1111.write_register(0, first_four_ios)

    def set_filters(self, filters):
        '''
        i/o 04 controls zero pole filter 1: pz1; i/o 05 controls zero pole filter 2: pz2; i/o 06 controls zero pole filter 3: pz3
        '''
        if type(filters) != list or len(filters) != 3 or not all(x in [0, 1] for x in filters):
            raise BaseException('Filters must be a list of three elements (0 or 1).')
        second_four_ios = int("".join(map(str, filters))+str(self.le), 2)
        self.XT1111.write_register(1, second_four_ios)
        