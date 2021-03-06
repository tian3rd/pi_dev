import socket
from subprocess import check_output
from queue import Queue
from time import sleep
import threading

# global variables
# number of data points in {'HDF', 14203459.345, 1600, 2991, 3409, -781, -78, ...}
SIZE = 25


class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class RShake(object):
    def __init__(self, host="", port=8888, interval=0.125):
        '''
        RShake connection class
        Default port is localhost:8888
        Default interval is 0.125s (8Hz)
        '''
        self._host = host
        self._port = port
        self._interval = interval
        self._freq = int(1/interval)
        # to convert count signals to metric units, refer to: https://manual.raspberryshake.org/developersCorner.html#converting-to-metric
        self._count = 0
        # to convert epoch seconds to human readable time, refer to: https://stackoverflow.com/questions/12400256/converting-epoch-time-into-the-datetime
        self._timestamp = 0
        self._channel = ''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self._host, self._port))
        print("Waiting for connection from RShake on port {}".format(self._port))
        self.tid = threading.Thread(target=self.start)
        self.tid.start()

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, new_host):
        if isinstance(new_host, str):
            try:
                socket.inet_aton(new_host)
                self._host = new_host
            except OSError:
                raise BaseException("Illegal address")
        else:
            raise BaseException("Host should be a string, e.g., 20.155.9.218")

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, new_port):
        if isinstance(new_port, int):
            if new_port > 0 and new_port < 65535:
                self._port = new_port
            else:
                raise BaseException("Port should be between 1 and 65535")
        else:
            raise BaseException("Port should be an integer")

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        if isinstance(value, float) and 0.01 <= value and value <= 0.5:
            self._interval = value
            # how often to record a signal
            self._freq = int(1/value)
        else:
            raise BaseException(
                "Please provide a float within range (0.01, 0.5) inclusive")

    @property
    def count(self):
        '''
        Return the count signal
        '''
        return self._count

    @property
    def timestamp(self):
        '''
        Return the timestamp
        '''
        return self._timestamp

    @property
    def channel(self):
        '''
        Return the channel
        '''
        return self._channel

    # refer to https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-from-a-nic-network-interface-controller-in-python

    def get_ip_address(self):
        addrs = check_output(
            ["hostname", '--all-ip-addresses']).decode('utf-8').strip('\n ').split('\n')
        return addrs

    def start(self):
        '''
        Start recording timestamps and count signals corresponding to a certain interval/frequency
        '''
        q_counts = Queue(maxsize=2*SIZE)
        q_timestamps = Queue(maxsize=2*SIZE)
        while True:
            data, addr = self.sock.recvfrom(1024)
            data_arr = data.decode('utf-8').strip('{}').split(',')
            self._channel = data_arr[0]
            timestamp_start = float(data_arr[1])
            for i in range(len(data_arr[2:])):
                q_counts.put(int(data_arr[i+2]))
                q_timestamps.put(timestamp_start + i * 0.01)
            while q_counts.qsize() >= self._freq:
                total_counts = q_counts.get()
                self._timestamp = q_timestamps.get() + (self._freq / 2 - 1) * 0.01 - 1
                for _ in range(self._freq - 1):
                    total_counts += q_counts.get()
                    q_timestamps.get()
                self._count = total_counts / self._freq
                # print('Time: {:.2f}, Channel: {}, Count: {}'.format(
                #     self._timestamp, self._channel, self._count))
            sleep(0.25)


if __name__ == "__main__":
    rshake = RShake(port=9988)
