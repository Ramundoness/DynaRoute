A Python network simulator to design, benchmark, and visualize routing algorithms for dynamic geospatial networks.

## Getting Started
To install the Python library dependencies, run:
```
pip3 install requirements.txt
```
Note that we are using Python v3.9 (other versions may be unsupported).

## Usage
Use the below command to run the network routing simulator under default conditions:
```
python3 main.py
```

This uses the default args of:
- `num_nodes = 100`
- `num_messages = 1000`
- `num_steps = 250`
- `ttl = None`
- `density = 0.5`
- `volatility = 0.5`
- `topology = 'random'`
- `alg = 'random'`
- `metric = ['fraction_delivered']`
- `graphics = False`
- `heatmap = False`
- `verbose = False`

You can override any args like this:
```
python3 main.py --num_nodes=50 --density=0.1 --volatility=0.2
```

### Description of args
| Arg      | Description |
| ----------- | ----------- |
| `num_nodes`      | The number of nodes in the network.       |
| `num_messages`   | The number of messages to be sent in the workload. Note that messages may end up never being delivered (i.e. in the case of disconnected networks).        |
| `num_steps`   | The number of steps to run the simulation for.        |
| `ttl`   | The number to set the TTL for messages. Has no effect on some routing algorithms.        |
| `density`   | Density of the network topology (a float between 0 and 1, inclusive). Higher = more connectivity.        |
| `volatility`   | Volatility of the network topology (a float between 0 and 1, inclusive). Higher = changes more frequently.        |
| `topology`   | The topology class to be used. One of `'random'` (Random) or `'geo'` (Random Geospatial).        |
| `alg`   | The routing algorithm for each node. One of `'random'` (Random), `'bfs'` (Naive BFS), `'bfs-ttl'` (BFS with TTL), `'bfs-ttl-early-split'` (BFS with TTL and Early Split), `'bfs-ttl-late-split'` (BFS with TTL and Late Split), '`bfs-loops'` (BFS with Looping).        |
| `metric`   | The metric to use for plotting the network topology.        |
| `graphics`   | Whether to display graphics.        |
| `heatmap`   | Whether to run multiple trials and construct a heatmap.        |
| `verbose`   | To display more complex metrics.        |