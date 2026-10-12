# Dijkstra animation — iteration one

This scene draws the storyboard's graph and initial priority queue on a black
background. A starts at distance 0, and B–F start at infinity. The algorithm
steps will be added in a later iteration.

Run the scene with:

```sh
uv run manim -ql src/manimations/dijkstra.py DijkstraSetup
```

The video is saved under `media/videos/dijkstra/480p15/`.

All the scene code is in `src/manimations/dijkstra.py`:

- `ADJACENCY_LIST` contains the graph's connections and weights. List each edge once.
- `POSITIONS` sets each node's location to match the storyboard.
- `START_NODE` is A for this iteration.
- `DijkstraSetup.construct()` draws the edges, nodes, distances, and queue.

To change the graph, edit the adjacency list and positions directly. Include
an entry in both dictionaries for each node, even if its neighbor dictionary
is empty. This iteration uses an adjacency list only.
