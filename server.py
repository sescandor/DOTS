#! /usr/bin/python

import signal
import sys
import threading
import time
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

        self.threads = []
        self.hb_interval = 15
        self.recv_msg_event = threading.Event()

    def writebuf(self):
        self.server_message.seqno = self.server_message.seqno + 1
        self.server_message.last_client_seqno = self.last_recv_seqno

    def send(self):
        self.writebuf()
        self.channel.write(self.server_message.SerializeToString())

    def readbuf(self):
        self.client_message.ParseFromString(self.channel.read())
        self.last_recv_seqno = self.client_message.seqno

        print "last_recv_seqno:", self.last_recv_seqno

    def read(self):
        while True:
            self.recv_msg_event.wait()
            try:
                self.readbuf()
            except Exception as e:
                print "Error reading channel."
                print "Error was:", str(e)
            finally:
                self.recv_msg_event.clear()

    def test_recv(self):
        self.read()
        print "Last client seq number server received:", self.last_recv_seqno

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

    def close_channel(self):
        print "closing channel"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Usage:", sys.argv[0], "LISTEN_PORT REMOTE_ADDR REMOTE_PORT"
        sys.exit(-1)

    channel = comm_channel.CommChannel(int(sys.argv[1]))
    channel.set_remote(sys.argv[2], int(sys.argv[3]))

    server = DOTSServer(channel)
    server.start()
