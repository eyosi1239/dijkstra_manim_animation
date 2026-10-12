import unittest
from math import inf

from manimations.dijkstra import dijkstra


class DijkstraTests(unittest.TestCase):
    def test_intermediate_updates_and_final_paths(self):
        graph = {"A": {"B": 7, "C": 3}, "B": {}, "C": {"B": 1}, "D": {}}
        distances, previous, steps = dijkstra(graph, "A")
        self.assertEqual(distances, {"A": 0, "B": 4, "C": 3, "D": inf})
        self.assertEqual(previous, {"A": None, "B": "C", "C": "A", "D": None})
        self.assertEqual([s["current"] for s in steps], ["A", "C", "B"])
        self.assertEqual(steps[0]["queue"], [(3, "C"), (7, "B"), (inf, "D")])
        self.assertEqual(steps[0]["distances"]["B"], 7)
        self.assertEqual(steps[0]["visited"], {"A"})
        self.assertEqual(steps[1]["updates"], [
            {"node": "B", "old_distance": 7, "new_distance": 4, "from": "C"}
        ])
        self.assertEqual(steps[-1]["queue"], [(inf, "D")])
        self.assertEqual(steps[-1]["updates"], [])
        distances["B"] = 99
        steps[-1]["distances"]["B"] = 100
        steps[-1]["visited"].clear()
        self.assertEqual(steps[0]["distances"]["B"], 7)
        self.assertEqual(steps[1]["distances"]["B"], 4)
        self.assertEqual(steps[0]["visited"], {"A"})

    def test_zero_weight_cycles_ties_and_neighbor_only_nodes(self):
        graph = {"A": {"C": 0, "B": 0}, "B": {"A": 0, "D": 2}, "C": {"D": 2}}
        distances, previous, steps = dijkstra(graph, "A")
        self.assertEqual(distances, {"A": 0, "B": 0, "C": 0, "D": 2})
        self.assertEqual(previous["A"], None)
        self.assertEqual(previous["D"], "C")
        self.assertEqual(len(steps), 4)
        self.assertEqual(steps[0]["queue"], [(0, "B"), (0, "C"), (inf, "D")])
        self.assertEqual(graph["A"], {"C": 0, "B": 0})

    def test_isolated_start(self):
        distances, previous, steps = dijkstra({"A": {}}, "A")
        self.assertEqual(distances, {"A": 0})
        self.assertEqual(previous, {"A": None})
        self.assertEqual(steps[0]["queue"], [])

    def test_checked_edges_include_unsuccessful_relaxations(self):
        graph = {"A": {"B": 1, "C": 2}, "B": {"A": 1, "C": 5}, "C": {}}
        _, _, steps = dijkstra(graph, "A")
        self.assertEqual(steps[0]["checked_edges"], [("A", "B"), ("A", "C")])
        self.assertEqual(steps[1]["checked_edges"], [("B", "C")])
        self.assertEqual(steps[1]["updates"], [])
        self.assertEqual(steps[2]["checked_edges"], [])

    def test_invalid_inputs(self):
        for weight in (-1, inf, -inf, float("nan")):
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                dijkstra({"A": {}, "B": {"C": weight}}, "A")
        with self.assertRaises(ValueError):
            dijkstra({"A": {}}, "missing")
        with self.assertRaises(ValueError):
            dijkstra({}, "A")


if __name__ == "__main__":
    unittest.main()
