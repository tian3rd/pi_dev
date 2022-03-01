import socket


class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class RShake(object):
    def __init__(self, host="", port=8888):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        print("Waiting for connection from RShake on port {}".format(self.port))

    def start(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            print(data)


if __name__ == "__main__":
    rshake = RShake(port=9988)
