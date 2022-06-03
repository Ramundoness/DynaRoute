
from abc import ABC, abstractmethod
from typing import List, Iterator, Tuple
import random

from message import Message
from packet import Packet
from topology import Topology
from workload import Workload

import copy

class Node(ABC):
    '''Node class. Handles receiving and sending of messages for individual nodes.
        Extend this class to test forwarding algorithms

    '''
    def __init__(self, self_id) -> None:
        # self.nodelist = nodelist
        self.inbox  = []     #  messages sent to node
        self.outbox = []    #  only put in outbox if "successful send"
        self.self_id = self_id  #  `self_id` is position of node in parent NetworkSimulator's nodelist. Used for identification  
        self.avg_num_packets_inbox = 0
        self.steps = 0

    """
    Function: set_workload
        Allows Nodes to retreive information about the current workload running
        For instance, nodes may wish to set different parameters based on the
        size of the current network
    """
    def set_workload(self, workload: Workload):
        self.workload = workload

    """
    Function: handle_packet
        Wrapper to handle node forwarding packets to other nodes.

        - checks if self is destination
            - returns -1
        - Uses topology of network to find who node can talk to (simulating node querying its reachable network)
        - Let's sending_algorithm handle routing and cost calculations
        - places (msg, next_node) pairs into outbox

        returns number of forwards. >0 if forwards occur. 0 if no forwards occur. -1 if self is destination
    """
    def handle_packet(self, packet: Packet, topology: Topology) -> int:
        # prevent packets from looping
        packet.nodes_visited.append(self)
        msg = packet.message
        # check if self is destination
        destination = msg.destination_id
        if destination == self.self_id:
            msg.delivered = True
            return -1
        # search topology for self's connections. 
        neighbors = topology.topology[self.self_id].nonzero()
        neighbors = neighbors[0] # Unpack.

        forwards = 0 # count of how many nodes self forwards msg to
        # DO ALGORITHM to send messages according to logic 
            # who to send to
            # increment cost
        for forward_packet, forward_node in self.sending_algorithm(packet, neighbors):
            self.outbox.append((forward_packet, forward_node))
            forwards += 1

        return forwards
        # let network_simulator handle message deletion from inbox & outbox


    """
    Function: sending_algorithm
        - this functionality should be modified in classes that extend Node to test different sending algorithms

        yields (node, msg) pairs to send
        OR returns a list of (node, msg) pairs

        goal:
            # - Deciding which node to send the message to
            # - Retries after failed sends
            # - Computing the cost of each send
    """
    @abstractmethod
    def sending_algorithm(self, message, neighbors):
        pass


class NodeNaiveBFS(Node):
    def __init__(self, self_id, inbox: List[Packet] = [], outbox: List[Tuple[Packet, Node]] = []) -> None:
        super().__init__(self_id)
        self.inbox = inbox[:]  # messages sent to node
        self.outbox = outbox[:]  # only put in outbox if "successful send"
        self.seen_messages = set() # previously seen messages

    def sending_algorithm(self, packet: Packet, neighbors: List[Node]) -> Iterator[Tuple[Node, Packet]]:
        # maintain a memory of past messages the node has seen to prevent a packet from going to 
        # i.e. A -> B; A -> C -> B
        if packet.message in self.seen_messages:
            return
        self.seen_messages.add(packet.message)

        for forward_node in neighbors:
            # don't forward packets to nodes that we've already visited
            if forward_node in packet.nodes_visited:
                continue
            # construct a new copy of a packet
            # forward_packet = copy.copy(packet)
            forward_packet = Packet(packet.message)
            forward_packet.nodes_visited = packet.nodes_visited
            forward_packet.message.total_cost += 1
            forward_packet.nodes_visited.append(self.self_id)
            yield (forward_packet, forward_node)
        return


class RandomForwardNode(Node):
    def __init__(self, self_id):
        super().__init__(self_id)

    def sending_algorithm(self, packet: Packet, neighbors: List[Node]) -> Iterator[Tuple[Node, Packet]]:
        if len(neighbors) == 0:
            return
        else:
            # TODO: try forwarding the node to more than neighbor
            # i.e. k=2 or k=3
            forward_node = random.choice(neighbors)
            packet.message.total_cost += 1
            packet.nodes_visited.append(self.self_id)
            yield (packet, forward_node)
        return

"""
This is a copy of the NodeNaiveBFS algorithm but with a TTL added to each packet
Every node decrements the TTL by 1. If the TTL reaches 0, the packet is dropped
This prevents packets from being routed forever.
"""
class NodeBFSWithTTL(Node):
    def __init__(self, self_id, inbox: List[Packet] = [], outbox: List[Tuple[Packet, Node]] = []) -> None:
        super().__init__(self_id)
        self.inbox = inbox[:]  # messages sent to node
        self.outbox = outbox[:]  # only put in outbox if "successful send"
        self.seen_messages = set() # previously seen messages

    def sending_algorithm(self, packet: Packet, neighbors: List[Node]) -> Iterator[Tuple[Node, Packet]]:
        # maintain a memory of past messages the node has seen to prevent a packet from going to 
        # i.e. A -> B; A -> C -> B
        if packet.message in self.seen_messages:
            return
        self.seen_messages.add(packet.message)

        # drop packets that have been routed too often
        packet.ttl -= 1
        if packet.ttl <= 0:
            return

        for forward_node in neighbors:
            # don't forward packets to nodes that we've already visited
            if forward_node in packet.nodes_visited:
                continue
            # construct a new copy of a packet
            # forward_packet = copy.copy(packet)
            forward_packet = Packet(packet.message, packet.ttl)
            forward_packet.nodes_visited = packet.nodes_visited
            forward_packet.message.total_cost += 1
            forward_packet.nodes_visited.append(self.self_id)
            yield (forward_packet, forward_node)
        return


class NodeBFSWithTTLEarlySplit(Node):
    def __init__(self,
                 self_id,
                 workload: Workload = None, # These nodes (and maybe all nodes) need info from the workload
                 inbox: List[Packet] = [],
                 outbox: List[Tuple[Packet, Node]] = []) -> None:
        super().__init__(self_id)
        self.inbox = inbox[:]  # messages sent to node
        self.outbox = outbox[:]  # only put in outbox if "successful send"
        self.seen_messages = set() # previously seen messages
        self.workload = workload

    def sending_algorithm(self, packet: Packet, neighbors: List[Node]) -> Iterator[Tuple[Node, Packet]]:
        # maintain a memory of past messages the node has seen to prevent a packet from going to 
        # i.e. A -> B; A -> C -> B
        if packet.message in self.seen_messages:
            return
        self.seen_messages.add(packet.message)

        # drop packets that have been routed too often
        packet.ttl -= 1
        if packet.ttl <= 0:
            return

        nodes_sent = 0
        random.shuffle(neighbors) # randomly choose which fraction to send to
        for forward_node in neighbors:
            # don't forward packets to nodes that we've already visited
            if forward_node in packet.nodes_visited:
                continue

            # If the packet has been out for a while, send it to fewer neighbors
            if packet.ttl / self.workload.num_messages >= nodes_sent / len(neighbors):
                # construct a new copy of a packet
                # forward_packet = copy.copy(packet)
                forward_packet = Packet(packet.message, packet.ttl)
                forward_packet.nodes_visited = packet.nodes_visited
                forward_packet.message.total_cost += 1
                forward_packet.nodes_visited.append(self.self_id)
                yield (forward_packet, forward_node)
                nodes_sent += 1
        return


# TODO BFS with ttl and splitting late
class NodeBFSWithTTLLateSplit(Node):
    def __init__(self,
                 self_id,
                 workload: Workload = None, # These nodes (and maybe all nodes) need info from the workload
                 inbox: List[Packet] = [],
                 outbox: List[Tuple[Packet, Node]] = []) -> None:
        super().__init__(self_id)
        self.inbox = inbox[:]  # messages sent to node
        self.outbox = outbox[:]  # only put in outbox if "successful send"
        self.seen_messages = set() # previously seen messages
        self.workload = workload

    def sending_algorithm(self, packet: Packet, neighbors: List[Node]) -> Iterator[Tuple[Node, Packet]]:
        # maintain a memory of past messages the node has seen to prevent a packet from going to 
        # i.e. A -> B; A -> C -> B
        if packet.message in self.seen_messages:
            return
        self.seen_messages.add(packet.message)

        # drop packets that have been routed too often
        packet.ttl -= 1
        if packet.ttl <= 0:
            return

        nodes_sent = 0
        random.shuffle(neighbors)
        for forward_node in neighbors:
            # don't forward packets to nodes that we've already visited
            if forward_node in packet.nodes_visited:
                continue

            # If the packet has been out for a while, send it to fewer neighbors
            if nodes_sent ==0 or packet.ttl / self.workload.num_messages <= nodes_sent / len(neighbors):
                # construct a new copy of a packet
                # forward_packet = copy.copy(packet)
                forward_packet = Packet(packet.message, packet.ttl)
                forward_packet.nodes_visited = packet.nodes_visited
                forward_packet.message.total_cost += 1
                forward_packet.nodes_visited.append(self.self_id)
                yield (forward_packet, forward_node)
                nodes_sent += 1
        return

# TODO distance routing
# TODO distance routing with some splitting threshold

# TODO nodes try to build routing table?
