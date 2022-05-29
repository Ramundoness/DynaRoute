
from abc import ABC, abstractmethod
from typing import List, Iterator, Tuple
import random

from message import Message
from topology import Topology

class Node(ABC):
    '''Node class. Handles receiving and sending of messages for individual nodes.
        Extend this class to test forwarding algorithms

    '''
    def __init__(self, self_id) -> None:
        # self.nodelist = nodelist
        self.inbox  = []     #  messages sent to node
        self.outbox = []    #  only put in outbox if "successful send"
        self.self_id = self_id  #  `self_id` is position of node in parent NetworkSimulator's nodelist. Used for identification  

    
    """
    Function: handle_message
        Wrapper to handle node forwarding messages to other nodes.

        - checks if self is destination
            - returns -1
        - Uses topology of network to find who node can talk to (simulating node querying its reachable network)
        - Let's sending_algorithm handle routing and cost calculations
        - places (msg, next_node) pairs into outbox 
    
        returns number of forwards. >0 if forwards occur. 0 if no forwards occur. -1 if self is destination
    """
    def handle_message(self, msg: Message, topology: Topology) -> int: 
        
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
        for forward_msg, forward_node in self.sending_algorithm(msg, neighbors):
            self.outbox.append((forward_msg, forward_node))
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
    def __init__(self, self_id, inbox: List[Message] = [], outbox: List[Tuple[Message, Node]] = []) -> None:
        super().__init__(self_id)
        self.inbox = inbox  # messages sent to node
        self.outbox = outbox  # only put in outbox if "successful send"

    def sending_algorithm(self, message: Message, neighbors: List[Node]) -> Iterator[Tuple[Node, Message]]: 
        for forward_node in neighbors: 
            forward_msg = message
            forward_msg.total_cost += 1
            forward_msg.nodes_visited.append(self.self_id)
            yield (forward_msg, forward_node)
        return


class RandomForwardNode(Node):
    def __init__(self, self_id):
        super().__init__(self_id)

    def sending_algorithm(self, message: Message, neighbors: List[Node]) -> Iterator[Tuple[Node, Message]]:
        if len(neighbors) == 0:
            return
        else:
            forward_node = random.choice(neighbors)
            forward_msg = message
            forward_msg.total_cost += 1
            forward_msg.nodes_visited.append(self.self_id)
            yield (forward_msg, forward_node)
        return
