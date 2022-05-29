from network_simulator import NetworkSimulator
from node import NodeNaiveBFS, RandomForwardNode
from topology import RandomTopology
from workload import Workload

def main():

    node_class = RandomForwardNode
    topology_class = RandomTopology
    workload_class = Workload
    
    num_nodes = 100
    num_messages = 1000
    max_steps = 1000

    # TODO: Make topology arguments (density / volatility) accessible via command-line flag.
    simulator = NetworkSimulator(node_class, topology_class, num_nodes)
    workload = workload_class(num_messages, num_nodes)

    simulator.initialize_new_workload(workload)
    simulator.run_workload(max_steps)
    simulator.print_workload_cost_stats()


if __name__ == "__main__":
    main()
