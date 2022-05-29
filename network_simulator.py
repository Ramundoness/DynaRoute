
from typing import List, Type

from node import Node # choose your Node
from workload import Workload
from message import Message
from topology import Topology  # choose your topology


class NetworkSimulator:
    '''Implements as simple simulator for a network with changing topology.

    Example usage:
        simulator = NetworkSimulator(node_class, topology_class, num_nodes)
        workload = workload_class(num_messages, num_nodes)

        initialize_new_workload(workload)
        run_workload(max_steps)
        print(compute_workload_cost)
    
    '''
  
    def __init__(self, node_class: Type[Node], topology_class: Type[Topology], num_nodes) -> None:
        self.nodelist = [Node(id=i) for i in range(num_nodes)]
        self.topology = Topology(num_nodes)
        self.current_workload = None
    
    def initialize_new_workload(self, workload) -> None:
        '''Adds all messages to the inbox of their respective start nodes.'''
        for message in workload:
            self.nodelist[message.start].inbox.append(message)
        
    def run_workload(self, max_steps=100):
        for _ in range(max_steps):
            self.run_one_network_step()
            self.topology.step()
 
    def compute_workload_cost(self):
        workload_cost = 0
        for message in self.current_workload.messages:
            workload_cost += message.total_cost
        return workload_cost
    
    def run_one_network_step(self):
        for node in self.nodelist:
            self.run_one_node_step(node)
        for node in self.nodelist:
            self.outbox_all_messages(node)
    
    def run_one_node_step(self, node: Node):
        for message in node.inbox:
            # Node handles this logic, including:
            # - Deciding which node to send the message to
            # - Retries after failed sends
            # - Computing the cost of each send
            # - Marking messages as delivered
            node.handle_message(message, self.topology)
        # clear inbox after loop 
        node.inbox = []
        assert(len(node.inbox == 0))
        return

    def outbox_all_messages(self, node: Node):
        for message, next_hop_id in node.outbox:
            # place message to next hop's inbox
            self.nodelist[next_hop_id].inbox.append(message)
            # then remove from outbox
        node.outbox = []
        assert(len(node.outbox == 0))
        return 