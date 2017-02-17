
Proof-of-Concept for DDoS Open Threat Signaling Protocol
--------------------------------------------------------

Based on protocol specifications found in:
[https://datatracker.ietf.org/doc/draft-teague-dots-protocol/]

Done:
* Initial client and server implementation.
* Client can consume server messages.
* Server can consume client messages.
* (Needs to be merged to HEAD) Client can now generate heartbeats
* (Needs to be merged to HEAD) Client can now process heartbeats from server.
* (Needs to be merged to HEAD) Client shuts down channel if it determines that
  communication channel is lossy.


TODO:
* Server to generate heartbeats
* Implement "Mitigation Request Handling" 


# Methods for testing:
Method 1)
Generate a binary file called "client_messages_file" with:
* seqno
* last_client_seqno
as data. We can use this file as input to the client for testing.
We can then start the DOTSClient to listen on port 9999.
We can send a udp packet to this client for testing in this way:
cat client_messages_file | nc -4u -w1 localhost 9999

Method 2)
Start a mock server using:
ncat -e /bin/cat -k -u -l 1235
This will echo back any data sent to it.
Then, start up the DOTSClient. This should receive its
own sequence number believing that it is the server's sequence number
