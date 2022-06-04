from abc import ABC, abstractmethod
from datetime import datetime
from random import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import numpy as np

# plt.rcParams["figure.figsize"] = [1, 1]
# plt.rcParams["figure.autolayout"] = True

DISPLAY_DEBUG = False

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

        # consistent layout for non-geographic based topologys
        G = nx.Graph() 
        G.add_nodes_from(self.topology[0]) 
        for i in range(self.num_nodes):
            for j in range(self.num_nodes):
                G.add_edge(i,j)
        self.layout_pos = nx.spring_layout(G)
        # print(self.layout_pos)
        # self.fig = plt.figure() 
        self.display_number = 0
        self.display_id = datetime.now()

    @abstractmethod
    def initialize():
        '''
        Function: initialize
            Generate the initial network topology.
        '''
        pass    

    @abstractmethod
    def step():
        '''
        Function: step
            Update the network based on self.volatility.
        '''
        pass

    def display(self):
        '''
        Function: display
            Visualize the network (nodes and connections).
        '''
        G = nx.Graph()
        # add nodes
        G.add_nodes_from(range(self.num_nodes))
        # add all edges
        edges = []
        for i,row in enumerate(self.topology):
            for j,val in enumerate(row):
                # if i>j: break
                if i==j: continue
                if val: edges.append((i,j))
        G.add_edges_from(edges)
        # save
        nx.draw_networkx(G, self.layout_pos)
        
        ax = plt.gca()
        ax.set_xlim([-1.1,1.1])
        ax.set_ylim([-1.1,1.1])
        plt.savefig(f"plots/{self.display_id}-{self.display_number}.png")
        self.display_number += 1
        if DISPLAY_DEBUG:
            print(self.topology)
            print(f"Number of nodes: {self.num_nodes}")
            print(f"Edges: {edges}")
            plt.show()
        plt.clf()
        return


class RandomTopology(Topology):
    '''
    RandomTopology class. Creates connections between nodes with a fixed probability,
        as determined by the density and volatility.
    '''
    def __init__(self, num_nodes, density, volatility) -> None:
        super().__init__(num_nodes, density, volatility)
    
    def initialize(self):
        '''
        Function: initialize
            Initializes network as an Erdős–Rényi-like random graph.
            https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model
        
            Note: because we are doing the logical or, the edge probability is greater than self.density
                (In particular, it is 1 - (1-density)^2).
        '''
        return self.random_topology(self.density)
    
    def random_topology(self, p):
        '''
        Function: random_topology
            Constructs a random topology based on an Erdős–Rényi graph.
        '''
        topology = np.random.rand(self.num_nodes, self.num_nodes) < p
        topology = topology | topology.T

        # This is a bit of a hack to ensure nodes always have one neighbor (themselves)
        # TODO: make nodes not connected to themselves + modify node algorithm
        # to place messages in the node's inbox iff they have no neighbors.
        topology = topology | np.eye(self.num_nodes, self.num_nodes).astype(np.bool)
        return topology

    
    def step(self):
        '''
        Function: step
            Replaces the existing topology with an alternate topology, according to the volatility 
                and density values.
        '''
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

    '''
    
    def __init__(self, num_nodes, density, volatility) -> None:
        super().__init__(num_nodes, density, volatility)
    
    def topology_from_grid_locations(self, grid_locations):
        '''
        Function: topology_from_grid_locations
            Connects nodes if their distance is within self.density * max_distance.
        '''

        # Returns ndarray of size [self.num_nodes, self.num_nodes]
        node_distances = self.get_2d_distances(self.grid_locations)
        max_distance = np.sqrt(2)  # Max distance on 1x1 grid is sqrt(2)
        normalized_distances = node_distances / max_distance
        return normalized_distances < self.density
    
    def random_2d_grid_locations(self, num_nodes):
        '''
        Function: random_2d_grid_locations
            Generates a random 2D grid to represent locations in a coordinate space.
        '''
        return np.random.uniform(0, 1, size=(num_nodes, 2))

    def get_2d_distances(self, grid_locations):
        '''
        Function: get_2d_distances
            Computes the L2 norm between locations in the grid.
        '''
        # This works because None adds an extra dimension, which numpy broadcasts across
        return np.linalg.norm(grid_locations[:, None, :] - grid_locations[None, :, :], axis=-1)

    def initialize(self):
        '''
        Function: initialize
            Place users uniformly on a 2D grid, then connects them if they are within a certain distance.
        '''
        # Returns ndarray of size [self.num_nodes, 2]
        self.grid_locations = self.random_2d_grid_locations(self.num_nodes)
        return self.topology_from_grid_locations(self.grid_locations)

    def step(self):
        '''
        Function: step
            Replaces the existing topology with an alternate topology, according to the volatility 
                and density values. Accounts for the grid locations in the 2D space.
        '''
        # Mix grid locations with alternate random grid locations with weight based on self.volatility.
        alternate_grid_locations = self.random_2d_grid_locations(self.num_nodes)
        # self.grid_locations = (1) * self.grid_locations + self.volatility * alternate_grid_locations
        alternate_grid_locations -= 0.5
        self.grid_locations = self.grid_locations + self.volatility * (alternate_grid_locations / np.linalg.norm(alternate_grid_locations, ord=2, axis=-1, keepdims=True))
        # reflecting across 0 & 1 boundaries to prevent nodes escaping the 
        self.grid_locations -= 2 * np.maximum(self.grid_locations-1, 0)
        self.grid_locations -= 2 * np.minimum(self.grid_locations, 0)
        
        self.topology = self.topology_from_grid_locations(self.grid_locations)

    def display(self):
        '''
        Function: Visualize the network (nodes and connections).
        '''
        G = nx.Graph()
        # add nodes
        G.add_nodes_from(range(self.num_nodes))
        # add all edges
        edges = []
        for i,row in enumerate(self.topology):
            for j,val in enumerate(row):
                # if i>j: break
                if i==j: continue
                if val: edges.append((i,j))
        G.add_edges_from(edges)
        # positions

        pos = {}
        for i,val in enumerate(self.grid_locations):
            pos[i] = val
        
        # set scale
        ax = plt.gca()
        ax.set_xlim([0,1])
        ax.set_ylim([0,1])
        # plt.grid(True)

        # save
        nx.draw_networkx(G, pos)
        plt.savefig(f"plots/{self.display_id}-{self.display_number}.png")
        self.display_number += 1
        if DISPLAY_DEBUG:
            print(f"Grid Location: {self.grid_locations}")
            print(f"Topology: {self.topology}")
            print(f"Number of nodes: {self.num_nodes}")
            print(f"Edges: {edges}")
            plt.show()
        plt.clf()
        return
