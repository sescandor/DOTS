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

        def write(self, message):
            # self.sock.sendto(message, address)
            print "stub for response to server"

        def read(self):
            return self.data

        def wait_for_message(self, e_msg_recvd):
            self.e_msg_recvd = e_msg_recvd
            while True:
                print "Waiting for a message..."
                data, address = self.sock.recvfrom(4096)
                print "Received ", len(data), " bytes from ", address
                self.data = data
                self.e_msg_recvd.set()

if __name__ == "__main__":
    channel = CommChannel(9999)
    e_msg = threading.Event()
    channel.wait_for_message(e_msg)
