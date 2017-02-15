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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "COMM_FILE"
        sys.exit(-1)

    server = DOTSServerMessage_pb2.DOTSServerMessage()
    client = DOTSClientMessage_pb2.DOTSClientMessage()

    f = open(sys.argv[1], "rb")
    client.ParseFromString(f.read())
    f.close()

    print "Last client sequence number server received:", client.seqno 
