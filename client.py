#! /usr/bin/python

import random
import sys
import comm_channel
import DOTSClientMessage_pb2


class DOTSClient(object):

    def __init__(self, channel_handle):
        self.message = DOTSClientMessage_pb2.DOTSClientMessage()
        self.message.seqno = random.randint(0, 18446744073709551615)
        self.channel = comm_channel.CommChannel(channel_handle)

    def writebuf(self):
        self.message.seqno = self.message.seqno + 1

    def send(self):
        self.writebuf()

        self.channel.write(self.message.SerializeToString())

    def close_channel(self):
        self.channel.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "COMM_FILE"
        sys.exit(-1)

    client = DOTSClient(sys.argv[1])
    client.send()
    client.close_channel()
