"""Check the actual animation's construction dependencies and screen geometry."""

import json
import unittest
from pathlib import Path

import numpy as np
from manim import Dot, Line, LEFT, RIGHT

from classification import ConicClassification


def through(first, second):
    return np.cross([*first, 1.0], [*second, 1.0])


def same_line(first, second):
    first, second = np.array(first, dtype=float), np.array(second, dtype=float)
    first /= np.linalg.norm(first)
    second /= np.linalg.norm(second)
    return min(np.linalg.norm(first - second), np.linalg.norm(first + second)) < 1e-8


class TangentProbe(ConicClassification):
    """Run draw_tangent itself while recording the objects available at each step."""

    def __init__(self, trace):
        self.trace = trace
        self.drawn_lines = []
        self.construction_lines = []
        self.markers = {}
        self.captions = []

    def caption(self, content):
        self.captions.append(content)

    def has_line(self, coefficients):
        return any(same_line(coefficients, line) for line in self.drawn_lines)

    def draw_line(self, coefficients, caption):
        self.caption(caption)
        self.drawn_lines.append(np.array(coefficients, dtype=float))
        line = Line(LEFT, RIGHT)
        self.construction_lines.append(line)
        return line

    def mark(self, name, position, *args, **kwargs):
        if len(self.drawn_lines) < 5:
            raise AssertionError("All five auxiliary lines must be drawn before labeling their intersections")
        a, b, c, d = self.trace["others"]
        at = self.trace["at"]
        parents = {
            "S": (through(a, b), through(d, at)),
            "T": (through(c, d), through(at, a)),
            "Q": (self.trace["pascal_line"], through(b, c)),
        }
        for parent in parents[name]:
            if parent is None or not self.has_line(parent):
                raise AssertionError(f"{name} appeared before its parent line was drawn")
            if abs(np.dot(parent, [*position, 1])) / np.linalg.norm(parent[:2]) > 1e-8:
                raise AssertionError(f"{name} is off its parent line")
        self.markers[name] = (Dot(), Dot())

    def drawable_line(self, coefficients, color=None):
        a, b, c, d = self.trace["others"]
        at = self.trace["at"]
        expected = [through(a, b), through(d, at), through(c, d), through(at, a), through(b, c)]
        if len(self.drawn_lines) < 5 or not all(same_line(actual, required)
                                               for actual, required in zip(self.drawn_lines[:5], expected)):
            raise AssertionError("The five auxiliary lines must be drawn first, in the documented order")
        if not same_line(coefficients, self.trace["tangent"]):
            raise AssertionError("The drawn tangent differs from the verified tangent")
        return Line(LEFT, RIGHT)

    def text(self, *args, **kwargs):
        return Dot(radius=0.01)

    def play(self, *args, **kwargs):
        pass

    def wait(self, *args, **kwargs):
        pass


class AnimationLogicTests(unittest.TestCase):
    def test_movie_tangent_dependencies(self):
        data = json.loads(Path(__file__).with_name("geometry.json").read_text("utf-8"))
        for scene in data["scenes"]:
            if scene["tangent"] is None:
                continue
            with self.subTest(category=scene["category"]):
                TangentProbe(scene["tangent"]).draw_tangent(scene["tangent"])

    def test_all_tangent_branches(self):
        common = {"at": [2, 0], "tangent": [1, 0, -2]}
        controls = [
            {"branch": "finite", "others": [[0, 1], [-2, 0], [0, -1], [1.2, -0.8]],
             "first": [6, 4], "second": [3, -0.5],
             "pascal_line": [3, -2, -10], "auxiliary": [2, -2]},
            {"branch": "first_parallel", "others": [[0, 1], [-2, 0], [1.2, 0.8], [0, -1]],
             "first": None, "second": [1, 0.5],
             "pascal_line": [1, -2, 0], "auxiliary": [2, 1]},
            {"branch": "second_parallel", "others": [[0, -1], [1.2, 0.8], [-2, 0], [0, 1]],
             "first": [1, 0.5], "second": None,
             "pascal_line": [1, -2, 0], "auxiliary": [2, 1]},
            {"branch": "both_parallel", "others": [[-1.2, 0.8], [1.2, 0.8], [1.2, -0.8], [-2, 0]],
             "first": None, "second": None, "pascal_line": None, "auxiliary": None},
            {"branch": "finite_parallel_tangent",
             "others": [[-1.2, 0.8], [0, 1], [0, -1], [-1.2, -0.8]],
             "first": [18, 4], "second": [18, -4],
             "pascal_line": [1, 0, -18], "auxiliary": None},
        ]
        for control in controls:
            with self.subTest(branch=control["branch"]):
                trace = dict(common, **control)
                TangentProbe(trace).draw_tangent(trace)

    def test_screen_line_incidence(self):
        scene = object.__new__(ConicClassification)
        scene.middle = np.array([2.0, -3.0, 0.0])
        lines = ([1, 0, -2], [0, 1, 3], [2, -3, -13])
        for scale in (0.5, 1.75, 3.0):
            scene.scale = scale
            for coefficients in lines:
                with self.subTest(scale=scale, coefficients=coefficients):
                    line = scene.drawable_line(coefficients)
                    screen_coefficients = through(line.get_start()[:2], line.get_end()[:2])
                    direction = np.array([coefficients[1], -coefficients[0], 0.0])
                    for raw in (scene.middle, scene.middle + direction * 0.2):
                        mapped = scene.at(raw[:2])
                        residual = abs(np.dot(screen_coefficients, [*mapped[:2], 1]))
                        residual /= np.linalg.norm(screen_coefficients[:2])
                        self.assertLess(residual, 1e-8)


if __name__ == "__main__":
    unittest.main()
