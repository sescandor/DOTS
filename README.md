
Proof-of-Concept for DDoS Open Threat Signaling Protocol
--------------------------------------------------------

Based on protocol specifications found in:
[https://datatracker.ietf.org/doc/draft-teague-dots-protocol/?include_text=1]

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
