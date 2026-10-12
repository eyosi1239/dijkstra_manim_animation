"""Dijkstra's algorithm and independent snapshots for animation consumers."""

from collections.abc import Mapping
from heapq import heappop, heappush
from itertools import count
from math import inf, isfinite
from typing import TypedDict


# Functional syntax allows the required key "from", a Python keyword.
DistanceUpdate = TypedDict(
    "DistanceUpdate",
    {"node": str, "old_distance": float, "new_distance": float, "from": str},
)


class DijkstraStep(TypedDict):
    current: str
    distances: dict[str, float]
    queue: list[tuple[float, str]]
    visited: set[str]
    updates: list[DistanceUpdate]


def dijkstra(
    graph: Mapping[str, Mapping[str, float]], start: str
) -> tuple[dict[str, float], dict[str, str | None], list[DijkstraStep]]:
    """Return shortest distances, predecessors, and post-processing steps.

    ``graph[node][neighbor]`` is a directed edge's nonnegative finite weight.
    For an undirected graph, supply both directions. Nodes appearing only as
    neighbors are included; isolated nodes must have an empty neighbor mapping.
    The start must occur in the graph, either as a key or as a neighbor.

    Each reachable node produces one step after its outgoing edges are relaxed.
    The snapshot queue is the logical queue: all unvisited nodes once, ordered
    by tentative distance (ties follow graph insertion order), including nodes
    at infinity. It omits the internal heap's stale entries. Unreachable nodes
    keep distance infinity and predecessor None and do not produce steps.
    Every step owns its mutable containers so later steps cannot change it.

    Raises ValueError for an unknown start or a negative/nonfinite edge weight.
    """
    nodes = dict.fromkeys(graph)
    for neighbors in graph.values():
        for neighbor, weight in neighbors.items():
            if not isfinite(weight) or weight < 0:
                raise ValueError("Dijkstra requires finite, nonnegative edge weights")
            nodes.setdefault(neighbor, None)
    if start not in nodes:
        raise ValueError(f"Start node {start!r} is not in the graph")

    distances = {node: inf for node in nodes}
    previous: dict[str, str | None] = {node: None for node in nodes}
    steps: list[DijkstraStep] = []
    visited: set[str] = set()
    distances[start] = 0
    sequence = count()
    heap = [(0, next(sequence), start)]

    while heap:
        distance, _, current = heappop(heap)
        if current in visited:
            continue
        visited.add(current)
        updates: list[DistanceUpdate] = []
        for neighbor, weight in graph.get(current, {}).items():
            if neighbor in visited:
                continue
            candidate = distance + weight
            if candidate < distances[neighbor]:
                updates.append({
                    "node": neighbor,
                    "old_distance": distances[neighbor],
                    "new_distance": candidate,
                    "from": current,
                })
                distances[neighbor] = candidate
                previous[neighbor] = current
                heappush(heap, (candidate, next(sequence), neighbor))

        steps.append({
            "current": current,
            "distances": distances.copy(),
            "queue": sorted(
                [(distances[node], node) for node in nodes if node not in visited],
                key=lambda entry: entry[0],
            ),
            "visited": visited.copy(),
            "updates": updates,
        })

    return distances, previous, steps
from manim import *
import networkx as nx
import numpy as np


# Each edge is listed once because the graph is undirected.
# For example, A connects to B with weight 4 and C with weight 2.
ADJACENCY_LIST = {
    "A": {"B": 4, "C": 2},
    "B": {"C": 1, "D": 5, "E": 3},
    "C": {"E": 8},
    "D": {"E": 2, "F": 6},
    "E": {"F": 3},
    "F": {},
}

# Graph 2: comment this out and uncomment the graph above to switch.
# ADJACENCY_LIST = {
#     "A": {"B": 7, "C": 3},
#     "B": {"D": 2},
#     "C": {"E": 4},
#     "D": {"F": 5},
#     "E": {"F": 1},
#     "F": {},
# }

START_NODE = "A"
GRAPH_WIDTH = 9.7
GRAPH_HEIGHT = 5.7


class DijkstraSetup(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        # Graph needs a list of node names and a list of connected pairs.
        vertices = list(ADJACENCY_LIST)
        edges = []
        edge_weights = {}
        for node, neighbors in ADJACENCY_LIST.items():
            for neighbor, weight in neighbors.items():
                if neighbor not in vertices:
                    vertices.append(neighbor)
                # Avoid drawing an undirected edge twice if both ends list it.
                if (neighbor, node) not in edge_weights:
                    edges.append((node, neighbor))
                    edge_weights[(node, neighbor)] = weight


        # Give NetworkX the weights so the layout uses weighted path distances.
        weighted_graph = nx.Graph()
        weighted_graph.add_nodes_from(vertices)
        for (node, neighbor), weight in edge_weights.items():
            weighted_graph.add_edge(node, neighbor, weight=weight)
        path_distances = dict(nx.all_pairs_dijkstra_path_length(weighted_graph))

        # Soften the distances used for positioning to give short paths room.
        # Actual edge weights stay unchanged; only the drawing uses square roots.
        for distances_from_node in path_distances.values():
            for neighbor, distance in distances_from_node.items():
                distances_from_node[neighbor] = distance ** 0.5

        # Kamada-Kawai positions nodes using those distances; it needs no seed.
        graph = Graph(
            vertices, edges,
            layout="kamada_kawai", layout_scale=2.5,
            layout_config={"dist": path_distances},
            vertex_type=Circle,
            vertex_config={
                "radius": 0.3, "color": BLUE_B, "stroke_width": 3,
                "fill_color": BLACK, "fill_opacity": 1,
            },
            edge_config={"color": GRAY_D, "stroke_width": 2.5},
        )
        # Spread the generated positions across the space beside the queue.
        # Move the nodes rather than scaling the circles or their labels.
        center = graph.get_center()
        width = max(graph.width - 0.6, 0.01)  # Subtract the circle diameter.
        height = max(graph.height - 0.6, 0.01)
        layout = {}
        for node in vertices:
            position = graph.vertices[node].get_center() - center
            position[0] *= GRAPH_WIDTH / width
            position[1] *= GRAPH_HEIGHT / height
            layout[node] = position
        graph.change_layout(layout)
        graph.move_to(RIGHT + DOWN * 0.1)
        graph.update()  # Update the edges before placing their weight labels.
        # Positions are fixed for this scene, so stop the automatic edge redraw.
        graph.clear_updaters()

        # Curve an edge if its straight path would run through another node.
        for (node, neighbor), edge in graph.edges.items():
            start = edge.get_start()
            direction = edge.get_unit_vector()
            length = edge.get_length()
            for other in vertices:
                if other in (node, neighbor):
                    continue
                point = graph.vertices[other].get_center()
                along = np.dot(point - start, direction)
                closest = start + along * direction
                if 0 < along < length and np.linalg.norm(point - closest) < 0.4:
                    edge.set_path_arc(PI / 3)
                    break

        weights = VGroup()
        node_labels = VGroup()
        distances = VGroup()
        queue = VGroup()

        # Circles cover the ends of the lines, and names sit above the circles.
        for node in vertices:
            circle = graph.vertices[node]
            circle.set_z_index(1)
            name_text = Text(node, font_size=22, color=BLUE_B)
            name_text.move_to(circle.get_center())
            name_text.set_z_index(2)
            node_labels.add(name_text)

            distance = "0" if node == START_NODE else "∞"
            distance_text = Text(distance, font_size=16, color=BLUE_B)
            if circle.get_center()[1] > graph.get_center()[1]:
                distance_text.next_to(circle, UP, buff=0.2)
            else:
                distance_text.next_to(circle, DOWN, buff=0.2)
            distances.add(distance_text)

        # Place each weight beside its edge, using the generated positions.
        for pair, weight in edge_weights.items():
            edge = graph.edges[pair]
            weight_text = Text(str(weight), font_size=16, color=GRAY)
            weight_text.move_to(edge.point_from_proportion(0.5))
            angle = -PI / 2 if edge.path_arc else PI / 2
            offset = rotate_vector(edge.get_unit_vector(), angle) * 0.2
            weight_text.shift(offset)
            weights.add(weight_text)

        # The starting node is highlighted. Other rows show infinity.
        title = Text("PRIORITY QUEUE", font_size=11, color=GRAY)
        title.move_to([-5.95, 3.05, 0])
        top_line = Line([-6.7, 2.9, 0], [-5.2, 2.9, 0], color=GRAY_E)
        queue.add(title, top_line)

        row_spacing = min(0.3, 5.4 / len(vertices))
        for index, node in enumerate(vertices):
            y = 2.65 - index * row_spacing
            distance = "0" if node == START_NODE else "∞"
            color = GOLD if node == START_NODE else GRAY

            name_text = Text(node, font_size=17, color=color)
            name_text.move_to([-6.5, y, 0])
            distance_text = Text(distance, font_size=17, color=color)
            distance_text.move_to([-5.3, y, 0])
            queue.add(name_text, distance_text)

            if node == START_NODE:
                marker = Dot([-6.68, y, 0], radius=0.025, color=GOLD)
                queue.add(marker)

        bottom_y = 2.65 - len(vertices) * row_spacing - 0.05
        bottom_line = Line(
            [-6.7, bottom_y, 0], [-5.2, bottom_y, 0], color=GRAY_E,
        )
        queue.add(bottom_line)

        # Populate the scene, then hold the starting state.
        self.play(FadeIn(queue), run_time=0.6)
        self.play(Create(graph), run_time=1.1)
        self.play(FadeIn(weights), FadeIn(node_labels), FadeIn(distances), run_time=1)
        self.wait(2)
