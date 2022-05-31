'''Main script to run network simulator.

You can override any arguments in SimpleArgumentParser like this:
    python3 main.py --num_nodes=200 --density=0.5
'''


import random
import numpy as np
from network_simulator import NetworkSimulator
from node import NodeNaiveBFS, RandomForwardNode
from topology import RandomTopology, RandomGeoTopology
from workload import Workload

from tap import Tap

TOPOLOGY_CLASS_DICT = {
    'random': RandomTopology,
    'geo': RandomGeoTopology
}

def main(args):
    # TODO: remove for final
    # set random seeds for deterministic outputs
    random.seed(a=43)
    np.random.seed(seed=43)

    num_nodes = args.num_nodes
    num_messages = args.num_messages
    max_steps = args.num_steps

    node_class = NodeNaiveBFS
    workload_class = Workload

    topology_class = TOPOLOGY_CLASS_DICT[args.topology]
    topology = topology_class(num_nodes, args.density, args.volatility)
    
    simulator = NetworkSimulator(node_class, topology, num_nodes)
    workload = workload_class(num_messages, num_nodes)

    simulator.initialize_new_workload(workload)
    simulator.run_workload(max_steps)
    simulator.print_workload_cost_stats()



class SimpleArgumentParser(Tap):
    num_nodes: int = 100  # Number of nodes in the network
    num_messages: int = 1000  # Number of messages in the workload
    num_steps: int = 1000  # Number of steps to run the simulation for

    density: float = 0.5  # Density of the network topology. Higher = more connectivity.
    volatility: float = 0.5  # Volatility of the network topology. Higher = changes more frequently.

    topology: str = 'random'  # Which topology class to use (key in TOPOLOGY_CLASS_DICT)


if __name__ == "__main__":
    args = SimpleArgumentParser().parse_args()
    main(args)
