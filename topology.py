from abc import ABC, abstractmethod
from random import random

import numpy as np

class Topology(ABC):
    '''Abstract network topology class.'''

    def __init__(self, num_nodes, density=0.1, volatility=0.05) -> None:
        '''Initializes Topology class. 
        
        Represents the ground-truth topology of the network.

        self.topology[i] is a 2D boolean numpy array holding whether
        This class is responsible for maintaining the symmetry of the array.
        
        Args:
            num_nodes: number of nodes in the network
            density: probability any two nodes are connected.
            volatility: probability the connection changes between any two nodes.
        '''
        self.num_nodes = num_nodes
        self.density = density
        self.volatility = volatility
        self.topology = self.initialize()
    
    @abstractmethod
    def initialize():
        '''Generate the initial network topology.'''
        pass    

    @abstractmethod
    def step():
        '''Update the network based on self.volatility.'''
        pass


class RandomTopology(Topology):
    def __init__(self, num_nodes, density=0.1, volatility=0.05) -> None:
        super().__init__(num_nodes, density, volatility)
    
    def initialize(self):
        # Initializes network as an Erdős–Rényi random graph
        # https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model

        # NOTE: because we are doing the logical or, the edge probability is greater than self.density
        # (In particular, it is 1 - (1-density)^2)
        self.topology = self.random_topology(self.density)
    
    def random_topology(self, p):
        topology = np.random.rand(self.num_nodes, self.num_nodes) < p
        topology = np.logical_or(topology, topology.T)
        return topology

    
    def step(self):
        alternate_topology = self.random_topology(self.density)
        use_alternate = self.random_topology(self.volatility)

        # Replace the existing topology with an alternate random topology
        # some fraction of the time (dependent on network volatility)
        self.topology = np.where(use_alternate, alternate_topology, self.topology)
    
