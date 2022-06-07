
from abc import ABC, abstractmethod
from typing import List, Iterator, Tuple
import random

from message import Message
from packet import Packet
from topology import Topology
from workload import Workload

class Node(ABC):
    '''
    Node class. Handles receiving and sending of messages for individual nodes.
        Extend this class to test forwarding algorithms.
    '''
    def __init__(self, self_id) -> None:
        # self.nodelist = nodelist
        self.inbox  = []     #  messages sent to node
        self.outbox = []    #  only put in outbox if "successful send"
        self.self_id = self_id      #  `self_id` is position of node in parent NetworkSimulator's nodelist. Used for identification  
        self.avg_num_packets_inbox = 0  # used to calculate the average inbox load
        self.steps = 0      # used to calculate the average inbox load (keeps track of number of timesteps)

    '''
    Function: set_workload
        Allows nodes to retreive information about the current workload running.
        For instance, nodes may wish to set different parameters based on the
        size of the current network
    '''
    def set_workload(self, workload: Workload):
        self.workload = workload

    '''
    Function: handle_packet
        Wrapper to handle node forwarding packets to other nodes.

        - Checks if self is destination (and terminates if so)
        - Uses topology of network to find who node can talk to (simulating node querying its reachable network)
        - Allows sending_algorithm handle routing and cost calculations
        - Places (next_packet, next_node) pairs into outbox

        Returns number of forwards (i.e. packet sending/ forwarding). 
            >0 if forwards occur. 
            0 if no forwards occur. 
            -1 if self is destination.
    '''
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


    '''
    Function: sending_algorithm
        Governs the packet forwarding algorithm between nodes. 
        Goals:
            # - Decide which node to send the message to
            # - Retry after failed sends
            # - Compute the cost of each send

        Yields (node, msg) pairs to send OR returns a list of (node, msg) pairs.
    '''
    @abstractmethod
    def sending_algorithm(self, packet, neighbors):
        pass


class NodeNaiveBFS(Node):
    '''
    NodeNaiveBFS class (extends Node class). Forwards a packet to every neighbor.
        - Has some optimizations with keeping a past history of messages the node has seen.
    '''
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
    '''
    RandomForwardNode class (extends Node class). Randomly forwards one packet to a single one of the node's
        neighbors.
    '''
    def __init__(self, self_id):
        super().__init__(self_id)

    def sending_algorithm(self, packet: Packet, neighbors: List[Node]) -> Iterator[Tuple[Node, Packet]]:
        if len(neighbors) == 0:
            return
        else:
            # TODO: Try forwarding the node to more than neighbor
            # i.e. k=2 or k=3
            forward_node = random.choice(neighbors)
            packet.message.total_cost += 1
            packet.nodes_visited.append(self.self_id)
            yield (packet, forward_node)
        return

class NodeBFSWithTTL(Node):
    '''
    NodeBFSWithTTL class (extends Node class). Copy of the NodeNaiveBFS algorithm but with a TTL added to each packet
        Every node decrements the TTL by 1. If the TTL reaches 0, the packet is dropped.
        This prevents packets from being routed forever.
    '''
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
    '''
    NodeBFSWithTTLEarlySplit class (extends Node class). Optimizes NodeBFSWithTTL by duplicating packets less
        often. Forwards packets it receives as a fraction of (current TTL of the packet / starting TTL of packets).
        Intuitively, this means that packets are duplicated more often towards the start of their journey.
    '''
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


class NodeBFSWithTTLLateSplit(Node):
    '''
    NodeBFSWithTTLLateSplit class (extends Node class). Optimizes NodeBFSWithTTL by duplicating packets less
        often. Forwards packets it receives as a fraction of (starting TTL of packets / current TTL of the packet).
        Intuitively, this means that packets are duplicated more often towards the start of their journey.
    '''
    def __init__(self,
                 self_id,
                 workload: Workload = None, # These nodes (and maybe all nodes) need info from the workload
                 inbox: List[Packet] = [],
                 outbox: List[Tuple[Packet, Node]] = []) -> None:
        super().__init__(self_id)
        self.inbox = inbox[:]  # messages sent to node
        self.outbox = outbox[:]  # only put in outbox if "successful send"
        self.seen_messages = set() # previously seen messages
        self.workload = workload # workload of messages to be delivered

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


class NodeBFSLoops(Node):
    '''
    NodeBFSLoops class (extends Node class). Nodes will not forward on packets containing messages that they
        have already seen. Allows for a message to be forwarded through the same node multiple times.
    '''
    def __init__(self, self_id, inbox: List[Packet] = [], outbox: List[Tuple[Packet, Node]] = []) -> None:
        super().__init__(self_id)
        self.inbox = inbox[:]  # messages sent to node
        self.outbox = outbox[:]  # only put in outbox if "successful send"

    def sending_algorithm(self, packet: Packet, neighbors: List[Node]) -> Iterator[Tuple[Node, Packet]]:
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