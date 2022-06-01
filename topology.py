from abc import ABC, abstractmethod
from random import random
import networkx as nx
import numpy as np

class Topology(ABC):
    '''Abstract network topology class.'''

    def __init__(self, num_nodes, density, volatility) -> None:
        '''Initializes Topology class. 
        
        Represents the ground-truth topology of the network.

        self.topology[i] is a 2D boolean numpy array holding whether
        This class is responsible for maintaining the symmetry of the array.
        
        Args:
            num_nodes: number of nodes in the network
            density: float in [0,1] that controls how many nodes are connected. 
                0 = none, 1 = all.
            volatility: float in [0,1] that controls how often the connection changes 
                between any two nodes. 0 = no change, 1 = maximum change
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

    def display(self):
        G = nx.Graph()
        G.add_nodes_from(self.topology[0])
        edges = []
        for i,row in enumerate(self.topology):
            for j,val in enumerate(row):
                if i>j: break
                if val: edges.append((i,j))
        G.add_edges_from(edges)
        nx.multipartite_layout(G)
        return


class RandomTopology(Topology):
    def __init__(self, num_nodes, density, volatility) -> None:
        super().__init__(num_nodes, density, volatility)
    
    def initialize(self):
        # Initializes network as an Erdős–Rényi-like random graph
        # https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model

        # NOTE: because we are doing the logical or, the edge probability is greater than self.density
        # (In particular, it is 1 - (1-density)^2)
        return self.random_topology(self.density)
    
    def random_topology(self, p):
        topology = np.random.rand(self.num_nodes, self.num_nodes) < p
        topology = topology | topology.T

        # This is a bit of a hack to ensure nodes always have one neighbor (themselves)
        # TODO: make nodes not connected to themselves + modify node algorithm
        # to place messages in the node's inbox iff they have no neighbors.
        topology = topology | np.eye(self.num_nodes, self.num_nodes).astype(np.bool)
        return topology

    
    def step(self):
        alternate_topology = self.random_topology(self.density)
        use_alternate = self.random_topology(self.volatility)

        # Replace the existing topology with an alternate random topology
        # some fraction of the time (dependent on network volatility)
        self.topology = np.where(use_alternate, alternate_topology, self.topology)
    
class RandomGeoTopology(Topology):
    '''Connect users based on their location on a grid.
    
    Args:
        - density: controls connectivity based on distance
        - volatility: controls how quickly the nodes move (influencing their connectivity)

    TODO: visualize this to make sure it's implemented correctly
    '''
    
    def __init__(self, num_nodes, density, volatility) -> None:
        super().__init__(num_nodes, density, volatility)
    
    def topology_from_grid_locations(self, grid_locations):
        '''Connects nodes if their distance is within self.density * max_distance.'''

        # Returns ndarray of size [self.num_nodes, self.num_nodes]
        node_distances = self.get_2d_distances(self.grid_locations)
        max_distance = np.sqrt(2)  # Max distance on 1x1 grid is sqrt(2)
        normalized_distances = node_distances / max_distance
        return normalized_distances < self.density
    
    def random_2d_grid_locations(self, num_nodes):
        return np.random.uniform(0, 1, size=(num_nodes, 2))

    def get_2d_distances(self, grid_locations):
        # This works because None adds an extra dimension, which numpy broadcasts across
        return np.linalg.norm(grid_locations[:, None, :] - grid_locations[None, :, :], axis=-1)

    def initialize(self):
        ''' Place users uniformly on a 2D grid, then connects them if they are within a certain distance'''

        # Returns ndarray of size [self.num_nodes, 2]
        self.grid_locations = self.random_2d_grid_locations(self.num_nodes)
        return self.topology_from_grid_locations(self.grid_locations)

    def step(self):
        # Mix grid locations with alternate random grid locations with weight based on self.volatility.
        alternate_grid_locations = self.random_2d_grid_locations(self.num_nodes)
        self.grid_locations = (1 - self.volatility) * self.grid_locations + self.volatility * alternate_grid_locations
        self.topology = self.topology_from_grid_locations(self.grid_locations)
