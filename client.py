#! /usr/bin/python

import DOTSClientMessage_pb2 
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "COMM_FILE"
        sys.exit(-1)

    client = DOTSClientMessage_pb2.DOTSClientMessage()

    client.seqno = 1

    f = open(sys.argv[1], "wb")
    f.write(client.SerializeToString())
    f.close()
