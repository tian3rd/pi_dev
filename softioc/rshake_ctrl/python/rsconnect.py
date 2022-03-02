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
        self.host = host
        self.port = port
        # how often to record a signal
        self.interval = int(1/interval)
        # to convert count signals to metric units, refer to: https://manual.raspberryshake.org/developersCorner.html#converting-to-metric
        self.count = 0
        # to convert epoch seconds to human readable time, refer to: https://stackoverflow.com/questions/12400256/converting-epoch-time-into-the-datetime
        self.timestamp = 0
        self.channel = ''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        print("Waiting for connection from RShake on port {}".format(self.port))
        self.tid = threading.Thread(target=self.start)
        self.tid.start()

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
            self.channel = data_arr[0]
            timestamp_start = float(data_arr[1])
            for i in range(len(data_arr[2:])):
                q_counts.put(int(data_arr[i+2]))
                q_timestamps.put(timestamp_start + i * 0.01)
            while q_counts.qsize() >= self.interval:
                total_counts = q_counts.get()
                self.timestamp = q_timestamps.get() + (self.interval / 2 - 1) * 0.01 - 1
                for _ in range(self.interval - 1):
                    total_counts += q_counts.get()
                    q_timestamps.get()
                self.count = total_counts / self.interval
                # print('Time: {:.2f}, Channel: {}, Count: {}'.format(
                #     self.timestamp, self.channel, self.count))
            sleep(0.25)

    def get_count(self):
        '''
        Return the count signal
        '''
        return self.count

    def get_timestamp(self):
        '''
        Return the timestamp
        '''
        return self.timestamp

    def get_channel(self):
        '''
        Return the channel
        '''
        return self.channel

    # @property
    # def interval(self):
    #     return self.interval

    # @interval.setter
    # def set_interval(self, interval):
    #     self.interval = interval


if __name__ == "__main__":
    rshake = RShake(port=9988)
