#! /usr/bin/python

import DOTSServerMessage_pb2
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "COMM_FILE"
        sys.exit(-1)

    server = DOTSServerMessage_pb2.DOTSServerMessage()

    f = open(sys.argv[1], "rb")
    server.ParseFromString(f.read())
    f.close()

    print "Last client sequence number server received:", server.last_client_seqno
