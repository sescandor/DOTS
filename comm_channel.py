#! /usr/bin/python

import socket
import threading


class CommChannel(object):

        def __init__(self, handle):
            self.handle = handle
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_address = ('localhost', handle)
            print "Listening on port:", handle
            self.sock.bind(self.server_address)

            self.send_to_address = ''

            self.data = None

        def set_remote(self, address, port):
            self.send_to_address = (address, port)

        def write(self, message):
            try:
                self.sock.sendto(message, self.send_to_address)
            except Exception as e:
                print "CommChannel Error writing to remote agent."
                print "Error was:", str(e)

        def read(self):
            return self.data

        def wait_for_message(self, e_msg_recvd):
            self.e_msg_recvd = e_msg_recvd
            while True:
                data, address = self.sock.recvfrom(4096)
                print "Received ", len(data), " bytes from ", address
                self.data = data
                self.e_msg_recvd.set()

if __name__ == "__main__":
    channel = CommChannel(9999)
    e_msg = threading.Event()
    channel.wait_for_message(e_msg)
