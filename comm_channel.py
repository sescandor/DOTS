#! /usr/bin/python


class CommChannel(object):

        def __init__(self, handle):
            self.handle = handle

        def write(self, message):
            f = open(self.handle, "wb")
            f.write(message)
            f.close()

        def read(self):
            f = open(self.handle, "rb")
            message = f.read()
            f.close()
            return message
