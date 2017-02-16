#! /usr/bin/python

import random
import sys
import comm_channel
import DOTSClientMessage_pb2
import DOTSServerMessage_pb2


class DOTSClient(object):

    def __init__(self, channel):
        self.client_message = DOTSClientMessage_pb2.DOTSClientMessage()
        self.server_message = DOTSServerMessage_pb2.DOTSServerMessage()
        self.client_message.seqno = random.randint(0, 18446744073709551615)
        self.last_recv_seqno = 0
        self.client_message.last_svr_seqno = self.last_recv_seqno
        self.channel = channel

    def writebuf(self):
        self.client_message.seqno = self.client_message.seqno + 1
        self.client_message.last_svr_seqno = self.last_recv_seqno

    def send(self):
        self.writebuf()

        self.channel.write(self.client_message.SerializeToString())

    def readbuf(self):
        self.server_message.ParseFromString(self.channel.read())

        self.last_recv_seqno = self.server_message.seqno

    def read(self):
        self.readbuf()

    def test_send(self):
        self.send()
        print "client seq number sent:", self.client_message.seqno

    def close_channel(self):
        print "closing down channel"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "COMM_FILE"
        sys.exit(-1)

    channel = comm_channel.CommChannel(sys.argv[1])

    client = DOTSClient(channel)
    client.test_send()
    client.close_channel()
