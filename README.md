
# Proof-of-Concept for DDoS Open Threat Signaling Protocol

Based on protocol specifications found in [the IETF DOTS document]
(https://datatracker.ietf.org/doc/draft-teague-dots-protocol/?include\_text=1)

Scope:
* Implement client-server heartbeat communication.
* Implement client to server mitigation request handling


Done:
* Initial client and server implementation.
* Client can consume server messages.
* Server can consume client messages.
* Client can now generate heartbeats
* Client can now process heartbeats from server.
* Client shuts down channel if it determines that
  communication channel is lossy.
* Server can now generate heartbeats 
* Server can now process heartbeats from client.


TODO:
* Implement "Mitigation Request Handling" 
* Fix SIGINT response issue

Methods for testing:
--------------------
Method 1)
Generate a binary file called "client\_messages\_file" with:
  * seqno
  * last\_client\_seqno
as data. We can use this file as input to the client for testing.
We can then start the DOTSClient to listen on port 9999.
We can send a udp packet to this client for testing in this way:

__cat client_messages_file | nc -4u -w1 localhost 9999__

Method 2)
Start a mock server using:

__ncat -e /bin/cat -k -u -l 1235__

This will echo back any data sent to it.
Then, start up the DOTSClient. This should receive its
own sequence number believing that it is the server's sequence number
