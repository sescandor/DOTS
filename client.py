#! /usr/bin/python

import random
import signal
import sys
import threading
import time
import comm_channel
import DOTSClientMessage_pb2
import DOTSServerMessage_pb2


class DOTSClient(object):

    def __init__(self, channel):
        self.client_message = DOTSClientMessage_pb2.DOTSClientMessage()
        self.server_message = DOTSServerMessage_pb2.DOTSServerMessage()
        self.client_message.seqno = random.randint(0, 18446744073709551615)
        self.last_recv_seqno = 0
        self.hb_interval = 15
        self.client_message.last_svr_seqno = self.last_recv_seqno
        self.channel = channel
        self.threads = []

        signal.signal(signal.SIGINT, self.close_channel)

        self.recv_msg_event = threading.Event()

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

    def start(self):
        heartbeat_d = threading.Thread(name='self.heartbeat_daemon',
                                       target=self.heartbeat_daemon)
        heartbeat_d.setDaemon(True)
        heartbeat_d.start()
        listener_thread = threading.Thread(name='self.listener_thread',
                                           target=self.listener_thread,
                                           args=(self, self.recv_msg_event,))
        listener_thread.start()
        self.threads.append(heartbeat_d)
        self.threads.append(listener_thread)
        signal.pause()

    def wait_for_message(e):
        while True:
            recv_message_event = e.wait()
            print "received message!"

    def listener_thread(self):
        self.wait_for_message()


    def heartbeat_daemon(self):
        while True:
            self.send()
            time.sleep(self.hb_interval)

    def close_channel(self, signal, frame):
        print "closing down channel"
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "COMM_FILE"
        sys.exit(-1)

    channel = comm_channel.CommChannel(sys.argv[1])

    client = DOTSClient(channel)
    client.start()

