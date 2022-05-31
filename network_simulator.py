
from typing import List, Type

from node import Node # choose your Node
from workload import Workload
from message import Message
from packet import Packet
from topology import Topology  # choose your topology


class NetworkSimulator:
    '''Implements as simple simulator for a network with changing topology.

    Example usage:
        simulator = NetworkSimulator(node_class, topology_class, num_nodes)
        workload = workload_class(num_messages, num_nodes)

        simulator.initialize_new_workload(workload)
        simulator.run_workload(max_steps)
        print(simulator.compute_workload_cost())
    
    '''
  
    def __init__(self, node_class: Type[Node], topology: Topology, num_nodes) -> None:
        self.nodelist = [node_class(i) for i in range(num_nodes)]
        self.topology = topology
        self.current_workload = None
    
    def initialize_new_workload(self, workload) -> None:
        '''Adds all messages to the inbox of their respective start nodes.'''
        print(f'Initializing workload with {len(workload.messages)} messages.')
        self.current_workload = workload
        for message in workload.messages:
            packet = Packet(message)
            self.nodelist[message.start].inbox.append(packet)
        
    def run_workload(self, max_steps=100):
        print(f'Running workload for {max_steps} steps.')
        for _ in range(max_steps):
            self.run_one_network_step()
            self.topology.step()
 
    def compute_workload_cost(self):
        print("Computing workload cost.")
        workload_cost = 0
        # TODO: calculate cost with packets
        for message in self.current_workload.messages:
            workload_cost += message.total_cost
        return workload_cost
    
    def print_workload_cost_stats(self):
        workload_cost = self.compute_workload_cost()
        print("Total cost:", workload_cost)
        print(f"Cost per message:", workload_cost / self.current_workload.num_messages)
        print(f"Fraction delivered: {self.current_workload.num_delivered() / self.current_workload.num_messages}")
    
    def run_one_network_step(self):
        for node in self.nodelist:
            self.run_one_node_step(node)
        for node in self.nodelist:
            self.outbox_all_messages(node)
    
    def run_one_node_step(self, node: Node):
        for packet in node.inbox:
            # Node handles this logic, including:
            # - Deciding which node to send the message to
            # - Retries after failed sends
            # - Computing the cost of each send
            # - Marking messages as delivered
            node.handle_packet(packet, self.topology)
        # Clear inbox after loop 
        node.inbox = []
        return

    def outbox_all_messages(self, node: Node):
        for packet, next_hop_id in node.outbox:
            # Place message to next hop's inbox
            self.nodelist[next_hop_id].inbox.append(packet)
        # Then remove from outbox
        node.outbox = []
        return 
