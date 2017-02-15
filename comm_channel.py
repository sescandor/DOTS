#! /usr/bin/python


class CommChannel(object):

        def __init__(self, send_handle, recv_handle):
            self.medium_send = open(send_handle, "wb")
            self.medium_recv = open(recv_handle, "w+")

        def write(self, message):
            self.medium_send.write(message)

        def read(self):
            return self.medium_recv.read()

        def close(self):
            self.medium_send.close()
            self.medium_recv.close()
