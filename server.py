#! /usr/bin/python

import DOTSServerMessage_pb2
import DOTSClientMessage_pb2
import sys

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
