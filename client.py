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
        self.recv_msg_event.wait()
        try:
            self.readbuf()
        except:
            print "Error reading channel"
        finally:
            self.recv_msg_event.clear()

    def test_send(self):
        self.send()
        print "client seq number sent:", self.client_message.seqno

    def start(self):
        heartbeat_d = threading.Thread(name='self.heartbeat_daemon',
                                       target=self.heartbeat_daemon)
        heartbeat_d.setDaemon(True)
        heartbeat_d.start()

        listener_thread = threading.Thread(name='self.listener_thread',
                                           target=self.listener_thread)
        listener_thread.start()

        reader_thread = threading.Thread(name='self.read',
                                         target=self.read)

        reader_thread.start()

        self.threads.append(heartbeat_d)
        self.threads.append(listener_thread)
        self.threads.append(reader_thread)
        signal.pause()

    def listener_thread(self):
        self.channel.wait_for_message(self.recv_msg_event)

    def heartbeat_daemon(self):
        while True:
            self.send()
            time.sleep(self.hb_interval)

    def close_channel(self, signal, frame):
        print "closing down channel"
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "LISTEN_PORT"
        sys.exit(-1)

    # We can send a udp packet to this client for testing in this way: echo -n "hello" | nc -4u -w1 localhost 9999
    channel = comm_channel.CommChannel(int(sys.argv[1]))

    client = DOTSClient(channel)
    client.start()

