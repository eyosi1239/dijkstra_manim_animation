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
