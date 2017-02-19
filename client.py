#! /usr/bin/python

import random
import signal
import sys
from threading import Thread, Lock, Event
import time
import comm_channel
import DOTSClientMessage_pb2
import DOTSServerMessage_pb2

MAX_UINT = 18446744073709551615


class DOTSClient(object):

    def __init__(self, channel):
        self.client_message = DOTSClientMessage_pb2.DOTSClientMessage()
        self.server_message = DOTSServerMessage_pb2.DOTSServerMessage()
        self.client_message.seqno = random.randint(0, MAX_UINT)
        self.last_recv_seqno = 0
        self.hb_interval = 15
        self.req_interval = 5
        self.acceptable_lossiness = 9
        self.signal_lost = False
        self.client_message.last_svr_seqno = self.last_recv_seqno
        self.channel = channel
        self.threads = []

        signal.signal(signal.SIGINT, self.close_channel)

        self.recv_msg_event = Event()

    def writebuf(self):
        self.client_message.seqno = self.client_message.seqno + 1
        self.client_message.last_svr_seqno = self.last_recv_seqno

    def send(self):
        self.writebuf()

        self.channel.write(self.client_message.SerializeToString())

    def readbuf(self):
        self.server_message.ParseFromString(self.channel.read())
        self.last_recv_seqno = self.server_message.seqno

        lossiness = self.client_message.seqno - self.last_recv_seqno
        if lossiness > self.acceptable_lossiness:
            self.signal_lost = True

        print "last_recv_seqno:", self.last_recv_seqno

    def handle_message(self):
        print "handling message"

        if self.server_message.mitigations.enabled:
            self.lock.acquire()
            self.req_mitigation_resp = False
            self.lock.release()

    def read(self):
        while not self.signal_lost:
            self.recv_msg_event.wait()
            try:
                self.readbuf()
                self.handle_message()
            except Exception as e:
                print "Error reading channel"
                print "Error was:", str(e)
            finally:
                self.recv_msg_event.clear()

    def test_send(self):
        self.send()
        print "client seq number sent:", self.client_message.seqno

    def test_req_mitigation(self):
        req_thread = Thread(name='self.req_mitigation',
                            target=self.req_mitigation)

        req_thread.start()

    def req_mitigation(self):
        # DOTS client may send repeated requests until it receives
        # a suitable response from the DOTS server, by which it may
        # interpret successful receipt.

        self.lock.acquire()
        mitigation_resp = self.req_mitigation_resp
        self.lock.release()

        while not mitigation_resp:
            self.client_message.mitigations.eventid = 666  # test for now
            self.client_message.mitigations.requested = True
            self.client_message.mitigations.scope = "some scope"
            self.client_message.mitigations.lifetime = 15
            self.send()
            print "Sent mitigation request."
            time.sleep(self.req_interval)

        self.clear_mitigation_req()

    def clear_mitigation_req(self):
        self.client_message.mitigations.eventid.ClearField()
        self.client_message.mitigations.requested.ClearField()
        self.client_message.mitigations.scope.ClearField()
        self.client_message.mitigations.lifetime.ClearField()

    def start(self):
        heartbeat_d = Thread(name='self.heartbeat_daemon',
                             target=self.heartbeat_daemon)
        heartbeat_d.setDaemon(True)
        heartbeat_d.start()

        listener_thread = Thread(name='self.listener_thread',
                                 target=self.listener_thread)
        listener_thread.start()

        reader_thread = Thread(name='self.read',
                               target=self.read)

        reader_thread.start()

        self.threads.append(heartbeat_d)
        self.threads.append(listener_thread)
        self.threads.append(reader_thread)
        signal.pause()

    def listener_thread(self):
        self.channel.wait_for_message(self.recv_msg_event)

    def heartbeat_daemon(self):
        while not self.signal_lost:
            self.send()
            time.sleep(self.hb_interval)

    def close_channel(self, signal, frame):
        print "closing down channel"
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Usage:", sys.argv[0], "LISTEN_PORT REMOTE_ADDR REMOTE_PORT"
        sys.exit(-1)

    channel = comm_channel.CommChannel(int(sys.argv[1]))
    channel.set_remote(sys.argv[2], int(sys.argv[3]))

    client = DOTSClient(channel)
    client.start()
