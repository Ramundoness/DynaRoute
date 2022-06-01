
from time import sleep
from typing import List, Type

from node import Node # choose your Node
from workload import Workload
from message import Message
from packet import Packet
from topology import Topology  # choose your topology

GRAPHICS_PAUSE = 1

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
        
    def run_workload(self, max_steps=100, graphics: bool=False):
        print(f'Running workload for {max_steps} steps.')
        for _ in range(max_steps):
            # perform one step on network 
            self.run_one_network_step()
            if graphics: 
                self.display() 
                sleep(GRAPHICS_PAUSE)
            # topology update
            self.topology.step()
            if graphics: 
                self.topology.display()
                self.display() # redo display after topology display
                print("UH OH I SHOULD NOT BE RUNNING! ALEX FIX THIS")
                sleep(GRAPHICS_PAUSE)

    def display(self): 
        pass

    def compute_inbox_stats(self):
        inbox_stats_per_node = [node.avg_num_packets_inbox / node.steps for node in self.nodelist]
        average_num_packets_inbox = sum(inbox_stats_per_node) / len(self.nodelist)
        low_num_packets_inbox = min(inbox_stats_per_node)
        high_num_packets_inbox = max(inbox_stats_per_node)
        inbox_stats = {
            'average_num_packets_inbox': average_num_packets_inbox,
            'low_num_packets_inbox': low_num_packets_inbox,
            'high_num_packets_inbox': high_num_packets_inbox
        }
        return inbox_stats
 
    def compute_workload_cost(self):
        workload_cost = 0
        for message in self.current_workload.messages:
            workload_cost += message.total_cost
        return workload_cost

    def compute_packets_per_message(self):
        average_packets_per_message = 0
        for message in self.current_workload.messages:
            average_packets_per_message += message.num_packets
        average_packets_per_message /= len(self.current_workload.messages)
        return average_packets_per_message
    
    def compute_workload_stats(self):
        workload_cost = self.compute_workload_cost()
        cost_per_message = workload_cost / self.current_workload.num_messages
        fraction_delivered = self.current_workload.num_delivered() / self.current_workload.num_messages
        inbox_stats = self.compute_inbox_stats()
        average_packets_per_message = self.compute_packets_per_message()
        stats = {
            'workload_cost': workload_cost,
            'cost_per_message': cost_per_message,
            'fraction_delivered': fraction_delivered,
            'inbox_stats': inbox_stats,
            'average_packets_per_message': average_packets_per_message
            }
        return stats
    
    def print_workload_cost_stats(self, verbose: bool=False):
        stats = self.compute_workload_stats()
        print("Total cost:", stats['workload_cost'])
        print(f"Cost per message:", stats['cost_per_message'])
        print(f"Fraction delivered:", stats['fraction_delivered'])
        if verbose:
            print(f"Average number of packets across nodes:", stats['inbox_stats']['average_num_packets_inbox'])
            print(f"Minimum number of packets across nodes:", stats['inbox_stats']['low_num_packets_inbox'])
            print(f"Peak number of packets across nodes:", stats['inbox_stats']['high_num_packets_inbox'])
            print(f"Average number of packets per message:", stats['average_packets_per_message'])
        print('-'*25)
    
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
            # increment the number of packets per message in the workload
            message_index = packet.message.id
            self.current_workload.messages[message_index].num_packets += 1
        # calculate average number of packets in the inbox of each node
        node.avg_num_packets_inbox += len(node.inbox)
        node.steps += 1
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
