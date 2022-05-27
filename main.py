'''
NEXT STEPS
- create simple "Hello world" version of app
- ways to generate networks (i.e. clustered of locality) -> 
- metrics/ analytics to gauge effectiveness of network/ node config
- visualization of packets going through nodes, nodes dropping, etc


Cool ideas
- nodes are moving, have a velocity
- when tick is called, goes to new position -> if going towards wall, bounces at an angle


Generating a network
- Under particular params (i.e. specify locations of nodes)
- generate a random network
-> geo-clustered together i.e. randomly pick 10 points, nodes are gaussian-ally distributed at those points


Methods to implement
- for the originator of the message (aka the sender)
    -> sender node calls 'receive_message'

- tick method (global/ network)
    global (network) calls tick -> propagates to the nodes themselves, which then call their own versions of tick
    - network first needs to update nodes that die/ are added/ edges are dropped
        - note that nodes can fail *at any time* (gracefully or unexpectedly)
        -> because we need to support messages passing through nodes simultaneously, rather than chronologically
        -> looks through data structure, picks appropriate ones, then sends message

- tick method (individual nodes)
    1. tick called on me, fetch current timestamp from a global variable in network and store as var
    2. examine msgs in my data structure -> ignore timestamps >= current timestamp, and call the next node's
    receive_message method (think about whether more than one call is allowed)
    3. that node stores message in their data structure until their their tick is called (heeding the timestamp stuff)

- receive_message (returns boolean of success/ failure)
  nodes call receive_message themselves (because this is essentially "sending the message")
    -> put msg in individual node's data structure

Message class
- variants of control message (tell nodes about state of network)/ data message (actual message that 
  needs to be transmitted)...
i.e. "This is the state of the current network: nodes A and B are connected, etc"

Network class
- owns nodes (dictionary mapping node id to node object?)
- tick method (calls tick on all nodes)

Node class
- nodes should have list of everyone it's connected to (directed/ undirected edges)
- nodes send control messages between one another to know the internal state of other nodes
    - recipients of control messages are up to the nodes themselves, and are dependent on each implementation of this class
    (i.e. may be broadcasted or sent to destination...we decide)
- has a position/ coordinate

'''