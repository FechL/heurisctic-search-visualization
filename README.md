# Heuristic Search GUI with Tkinter

This program is a Python application with a graphical user interface (GUI) that demonstrates two heuristic-based search algorithms:

- Greedy Best First Search
- A* Search

The application uses `Tkinter` for the GUI, `NetworkX` for graph structure, and `Matplotlib` for graph visualization.

## Features

- Interactive graph visualization with edge weights and heuristic values for each node.
- Automatic heuristic value calculation using Dijkstra's algorithm.
- Search result comparison between Greedy and A* algorithms.
- Direct visualization of the search path on the graph.

## Graph Structure

The graph is static and defined as a Python dictionary like this:

```python
graph = {
    "A": {"B": 2, "C": 3},
    "B": {"A": 2, "D": 4, "E": 5},
    ...
}
```

Node positions for visualization are manually set using coordinates:

```python
node_positions = {
    "A": (0, 2),
    "B": (1, 3),
    ...
}
```

## How to Run

1. Make sure Python is installed (Python 3.8+ recommended).
2. Install the required dependencies:

```bash
pip install matplotlib networkx
```

3. Run the program (main.py):

```bash
python main.py
```

## Algorithms Used

### Greedy Best First Search
- Selects the node with the lowest heuristic value.
- Ignores the total travel cost (`g(n)`).

### A* Search
- Uses the formula: `f(n) = g(n) + h(n)`
  > `g(n)` = total cost so far, `h(n)` = estimated cost to the goal (heuristic)
- Balances between exploration and exploitation.

## Interface Preview

![demo](/assets/demo.png)

The interface displays:
- Dropdown menus to select the start and goal nodes
- A "Search Route" button to run the algorithms
- Graph visualization with color-coded paths: 🔴 A* Path, 🟢 Greedy Path
- Heuristic values and path results shown below the graph

## Dependencies

- `tkinter` (built-in with Python)
- `networkx`
- `matplotlib`
- `heapq` (built-in with Python)

## License

This project is free to use for educational and research purposes.