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


class ClientMessage(object):

    def __init__(self):
        self.client_message = DOTSClientMessage_pb2.DOTSClientMessage()
        self.client_message.seqno = random.randint(0, MAX_UINT)

    def get_seqno(self):
        return self.client_message.seqno

    def prep_for_write(self):
        self.client_message.seqno = self.client_message.seqno + 1
        self.client_message.last_svr_seqno = self.last_recv_seqno

    def write(self):
        self.client_message.SerializeToString()

    def create_mitigation_req(self):
        mit_req = self.client_message.mitigations.add()
        mit_req.eventid = "666"  # test for now
        mit_req.requested = True
        mit_req.scope = "some scope"
        mit_req.lifetime = 15
        self.client_message.mitigations.extend([mit_req])

        return mit_req

    def set_last_svr_seqno(self, last_recv_seqno):
        self.client_message.last_svr_seqno = last_recv_seqno

    def clear_mitigation_req(self):
        self.client_message.mitigations.eventid.ClearField()
        self.client_message.mitigations.requested.ClearField()
        self.client_message.mitigations.scope.ClearField()
        self.client_message.mitigations.lifetime.ClearField()


class MitigationResponses(object):
    def __init__(self):
        # This is a hash of event_id and mitigation status from server
        self.req_mitigation_resp = {}

        self.lock_mitigation = Lock()

    def get_response_for(self, event_id):
        self.lock_mitigation.acquire()
        self.req_mitigation_resp[event_id]
        self.lock_mitigation.release()


class DOTSClient(object):

    def __init__(self, channel):
        self.client_message = ClientMessage()
        self.server_message = DOTSServerMessage_pb2.DOTSServerMessage()
        self.last_recv_seqno = 0
        self.hb_interval = 15
        self.req_interval = 5
        self.acceptable_lossiness = 9
        self.signal_lost = False
        self.client_message.set_last_svr_seqno(self.last_recv_seqno)
        self.channel = channel
        self.threads = []

        signal.signal(signal.SIGINT, self.close_channel)

        self.recv_msg_event = Event()

        self.mitigation_responses = MitigationResponses()

    def writebuf(self):
        self.client_message.prep_for_write()

    def send(self):
        self.writebuf()

        self.channel.write(self.client_message.write())

    def readbuf(self):
        self.server_message.ParseFromString(self.channel.read())
        self.last_recv_seqno = self.server_message.seqno

        lossiness = self.client_message.get_seqno() - self.last_recv_seqno
        if lossiness > self.acceptable_lossiness:
            self.signal_lost = True

        print "last_recv_seqno:", self.last_recv_seqno

    def handle_message(self):
        print "handling message"

        if len(self.server_message.mitigations) > 0:
            for resp in self.server_message.mitigations:
                if resp.enabled:
                    self.lock.acquire()
                    self.req_mitigation_resp[resp.eventid] = False
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
        print "client seq number sent:", self.client_message.get_seqno()

    def test_req_mitigation(self):
        print "### Starting test_req_mitigation ###"
        mit_req = self.client_message.create_mitigation_req()

        req_thread = Thread(name='self.req_mitigation',
                            target=self.req_mitigation,
                            args=[mit_req])

        req_thread.start()

    def req_mitigation(self, mit_req):
        # DOTS client may send repeated requests until it receives
        # a suitable response from the DOTS server, by which it may
        # interpret successful receipt.

        # TODO: Fix below to match handle_message, which pairs mitigation
        # status with eventid
        print "**** entering req mitigation ****"
        try:
            mitigation_resp = self.mitigation_responses.\
                                   get_response_for(mit_req.eventid)
        except Exception as e:
            print "Error matching mitigation response with event id"
            print "Error was:", str(e)
            return

        print "=== starting req mitigation ==="

        while not mitigation_resp:
            self.send()
            print "Sent mitigation request."
            time.sleep(self.req_interval)

        self.clear_mitigation_req()

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
    #client.start()
    client.test_req_mitigation()
