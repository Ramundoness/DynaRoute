'''Main script to run network simulator.

You can override any arguments in SimpleArgumentParser like this:
    python3 main.py --num_nodes=200 --density=0.5
'''


import random

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from textwrap import wrap

from network_simulator import NetworkSimulator
import node
from topology import RandomTopology, RandomGeoTopology
from workload import Workload

from tap import Tap

TOPOLOGY_CLASS_DICT = {
    'random': RandomTopology,
    'geo': RandomGeoTopology
}

NODE_ALGORITHM_CLASS_DICT = {
    'random': node.RandomForwardNode,
    'bfs': node.NodeNaiveBFS,
    'bfs-ttl': node.NodeBFSWithTTL,
    'bfs-ttl-early-split': node.NodeBFSWithTTLEarlySplit,
    'bfs-ttl-late-split': node.NodeBFSWithTTLLateSplit,
    'bfs-loops': node.NodeBFSLoops
}

def run_one_trial(args):
    '''
    Function: run_one_trial
        Runs one trial (i.e. simulation) with the provided args (helpful when trying to quickly modify
        args and seeing their results)

    Returns: dictionary mapping of stats for printing
    '''
    # Set seeds for debugging
    # random.seed(a=43)
    # np.random.seed(seed=43)

    num_nodes = args.num_nodes
    num_messages = args.num_messages
    max_steps = args.num_steps
    ttl = args.ttl

    node_class = NODE_ALGORITHM_CLASS_DICT[args.alg]
    workload_class = Workload

    topology_class = TOPOLOGY_CLASS_DICT[args.topology]
    topology = topology_class(num_nodes, args.density, args.volatility)

    simulator = NetworkSimulator(node_class, topology, num_nodes)
    workload = workload_class(num_messages, num_nodes, ttl)

    simulator.initialize_new_workload(workload)
    simulator.run_workload(max_steps, args.graphics)
    simulator.print_workload_cost_stats(args.verbose)
    return simulator.compute_workload_stats()


class SimpleArgumentParser(Tap):
    '''
    SimpleArgumentParser class. Helpful Python argument parser.
    '''
    num_nodes: int = 100  # Number of nodes in the network
    num_messages: int = 1000  # Number of messages in the workload
    num_steps: int = 250  # Number of steps to run the simulation for
    ttl: int = None # Number to set the TTL for messages. Has no effect on some routing algorithms

    # Currently this is overwritten
    density: float = 0.5  # Density of the network topology. Higher = more connectivity.
    volatility: float = 0.5  # Volatility of the network topology. Higher = changes more frequently.

    topology: str = 'random'  # The topology class to be use (key in TOPOLOGY_CLASS_DICT)
    alg: str = 'random'  # The routing algorithm for each node

    metric: list = ['fraction_delivered']  # Which metric to use for the heatmap

    graphics: bool = False # whether to display a visualization of the network topology

    heatmap: bool = False # whether to run multiple trials and construct a heatmap
    verbose: bool = False # whether to display more complex metrics


if __name__ == "__main__":
    args = SimpleArgumentParser().parse_args()

    if not args.heatmap:
       run_one_trial(args)
       quit()

    results = []
    n = 10
    b = 1.8
    for density in b ** np.arange(-n, 1):
        print(f"Density: {density}")
        for volatility in b ** np.arange(-n, 1):
            args.density = density
            args.volatility = volatility
            stats = run_one_trial(args)
            stats['density'] = round(density, 4)
            stats['volatility'] = round(volatility, 4)
            results.append(stats)

    for metric in args.metric:
        df = pd.DataFrame(results)
        plt.figure(figsize=(10, 8))
        sns.set_context("notebook")
        pivot = df.pivot("density", "volatility", metric)
        if metric == 'fraction_delivered':
            # Lock these to [0, 1] for ease of comparison
            sns.heatmap(pivot, vmin=0, vmax=1)
        else:
            sns.heatmap(pivot)
        plt.legend()
        title = f'metric={metric}, steps={args.num_steps}, alg={args.alg}, num_nodes={args.num_nodes}, num_messages={args.num_messages}, topology={args.topology}, n={n}, b={b}'
        plt.title("\n".join(wrap(title, 60)))
        plt.savefig(f'{title}.png')
        plt.show()
