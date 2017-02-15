#! /usr/bin/python


class CommChannel(object):

        def __init__(self, handle):
            self.medium = open(handle, "wb")

        def write(self, message):
            self.medium.write(message)

        def close(self):
            self.medium.close()
