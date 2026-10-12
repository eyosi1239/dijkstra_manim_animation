# Dijkstra animation

The algorithm lives in `src/manimations/dijkstra.py` and has no Manim imports.

```python
from manimations.dijkstra import dijkstra

graph = {
    "A": {"B": 7, "C": 3},
    "B": {},
    "C": {"B": 1},
    "D": {},
}
distances, previous, steps = dijkstra(graph, "A")
```

Use adjacency dictionaries with finite, nonnegative weights. Edges are directed;
add both directions for an undirected graph. Include isolated nodes with `{}`.
Nodes appearing only as neighbors are also included.

The result contains:

- `distances`: final shortest distances; unreachable nodes remain `float("inf")`.
- `previous`: shortest-path predecessors; the start and unreachable nodes have `None`.
- `steps`: independent snapshots after each reachable node is processed.

Each step includes `current`, a full `distances` dictionary, a `visited` set,
and `updates` with `node`, `old_distance`, `new_distance`, and `from` keys.
The `queue` is a sorted list of `(distance, node)` pairs for all unvisited nodes,
including those at infinity, without stale heap entries. Queue ties follow graph
insertion order; processing ties follow discovery order. Equal-length alternatives
keep the first predecessor found. Unreachable nodes do not generate steps.

The scene can iterate through `steps`, highlight `current`, animate the edges
identified by each update's `from` and `node`, and show the snapshot distances,
queue, and visited nodes. Follow `previous` backward from a reachable target to
reconstruct its final path.

Run the algorithm tests without installing Manim (PowerShell):

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```
