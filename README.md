A Python network simulator to design, benchmark, and visualize routing algorithms for dynamic geospatial networks.

<img src="https://user-images.githubusercontent.com/26047273/171828206-20ec5a01-0bc1-4352-867a-b6ea3c7ea8bc.gif" width="320" height="240" />

*Random Geospatial Topology Visualization*

<img src="https://user-images.githubusercontent.com/26047273/171829529-28e7b5af-034a-4f91-8af9-df20ae9d0d5d.gif" width="320" height="240" />

*Random Topology Visualization*

## Getting Started
To install the Python library dependencies, run:
```
pip3 install -r requirements.txt
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
| `graphics`   | Whether to display a visualization of the network topology.        |
| `heatmap`   | Whether to run multiple trials and construct a heatmap of density & the provided metric (i.e. `'fraction_delivered'`).        |
| `verbose`   | Whether to display more complex metrics.        |
