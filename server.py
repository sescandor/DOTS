#! /usr/bin/python

import random
import sys
import comm_channel
import DOTSServerMessage_pb2
import DOTSClientMessage_pb2


class DOTSServer(object):

    def __init__(self, channel):
        self.client_message = DOTSClientMessage_pb2.DOTSClientMessage()
        self.server_message = DOTSServerMessage_pb2.DOTSServerMessage()
        self.server_message.seqno = 8
        self.last_recv_seqno = 0
        self.server_message.last_client_seqno = self.last_recv_seqno
        self.channel = channel

    def writebuf(self):
        self.server_message.seqno = self.server_message.seqno + 1
        self.server_message.last_client_seqno = self.last_recv_seqno

    def send(self):
        self.writebuf()
        self.channel.write(self.server_message.SerializeToString())

    def readbuf(self):
        self.client_message.ParseFromString(self.channel.read())
        self.last_recv_seqno = self.client_message.seqno

    def read(self):
        self.readbuf()

    def test_recv(self):
        self.read()
        print "Last client seq number server received:", self.last_recv_seqno

    def close_channel(self):
        print "closing channel"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "COMM_FILE"
        sys.exit(-1)

    channel = comm_channel.CommChannel(sys.argv[1])

    server = DOTSServer(channel)
    server.test_recv()
    server.close_channel()
