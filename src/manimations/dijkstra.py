from manim import *


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

POSITIONS = {
    "A": [-4.6, -0.5, 0],
    "B": [-1.3, 1.35, 0],
    "C": [-1.3, -2.35, 0],
    "D": [2.0, 1.35, 0],
    "E": [2.0, -2.35, 0],
    "F": [5.0, -0.5, 0],
}

START_NODE = "A"


class DijkstraSetup(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        edges = VGroup()
        weights = VGroup()
        nodes = VGroup()
        queue = VGroup()

        # Draw the edges and put each weight beside its line.
        for node, neighbors in ADJACENCY_LIST.items():
            for neighbor, weight in neighbors.items():
                edge = Line(
                    POSITIONS[node], POSITIONS[neighbor],
                    buff=0.3, color=GRAY_D, stroke_width=2.5,
                )
                weight_text = Text(str(weight), font_size=16, color=GRAY)
                weight_text.move_to(edge.get_center())

                if POSITIONS[node][0] == POSITIONS[neighbor][0]:
                    weight_text.shift(LEFT * 0.18)
                else:
                    weight_text.shift(DOWN * 0.20)

                edges.add(edge)
                weights.add(weight_text)

        # Each node starts with a distance of infinity, except A.
        for node in ADJACENCY_LIST:
            circle = Circle(
                radius=0.3, color=BLUE_B, stroke_width=3,
                fill_color=BLACK, fill_opacity=1,
            )
            circle.move_to(POSITIONS[node])
            name_text = Text(node, font_size=22, color=BLUE_B)
            name_text.move_to(circle.get_center())

            distance = "0" if node == START_NODE else "∞"
            distance_text = Text(distance, font_size=16, color=BLUE_B)
            if POSITIONS[node][1] > 0:
                distance_text.next_to(circle, UP, buff=0.2)
            else:
                distance_text.next_to(circle, DOWN, buff=0.2)

            nodes.add(VGroup(circle, name_text, distance_text))

        # The queue starts with A highlighted. Other rows show infinity.
        title = Text("PRIORITY QUEUE", font_size=11, color=GRAY)
        title.move_to([-5.95, 3.05, 0])
        top_line = Line([-6.7, 2.9, 0], [-5.2, 2.9, 0], color=GRAY_E)
        queue.add(title, top_line)

        for index, node in enumerate(ADJACENCY_LIST):
            y = 2.65 - index * 0.3
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

        bottom_y = 2.65 - len(ADJACENCY_LIST) * 0.3 - 0.05
        bottom_line = Line(
            [-6.7, bottom_y, 0], [-5.2, bottom_y, 0], color=GRAY_E,
        )
        queue.add(bottom_line)

        # Populate the scene, then hold the starting state.
        self.play(FadeIn(queue), run_time=0.6)
        self.play(Create(edges), run_time=1.1)
        self.play(FadeIn(weights), FadeIn(nodes), run_time=1)
        self.wait(2)
