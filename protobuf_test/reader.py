#! /usr/bin/python

import person_pb2
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "PERSON_FILE"
        sys.exit(-1)

    human = person_pb2.Person()

    f = open(sys.argv[1], "rb")
    human.ParseFromString(f.read())
    f.close()

    print "Name: ", human.name
