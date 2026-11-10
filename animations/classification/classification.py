"""A one-page principle followed exclusively by ruler-and-compass diagrams."""

import hashlib
import json
from pathlib import Path

import numpy as np
from manim import (
    Create, DashedLine, Dot, FadeIn, FadeOut, Line, Rectangle, Scene, Text,
    VDict, VGroup, VMobject, Write, DOWN, LEFT, RIGHT, UP, config,
)


HERE = Path(__file__).resolve().parent
FONT = "Noto Sans CJK SC"
BACKGROUND = "#07101F"
FOREGROUND = "#E8F0F7"
MUTED = "#8397A8"
INPUT = "#F45BFF"
CURRENT = "#FFC857"
AUXILIARY = "#8AC6D9"
RESULT = "#5DE2A5"
NAMES = {"ellipse": "椭圆", "parabola": "抛物线", "hyperbola": "双曲线"}


def clipped_line(coefficients, bounds, color):
    a, b, c = coefficients
    left, right, bottom, top = bounds
    candidates = []
    if abs(b) > 1e-12:
        for x in (left, right):
            y = -(a * x + c) / b
            if bottom <= y <= top:
                candidates.append(np.array([x, y, 0]))
    if abs(a) > 1e-12:
        for y in (bottom, top):
            x = -(b * y + c) / a
            if left <= x <= right:
                candidates.append(np.array([x, y, 0]))
    if len(candidates) < 2:
        raise ValueError("a displayed construction line is outside the viewport")
    first, second = max(((p, q) for p in candidates for q in candidates),
                        key=lambda pair: np.linalg.norm(pair[0] - pair[1]))
    return Line(first, second, color=color, stroke_width=1.5)


class ConicClassification(Scene):
    def text(self, content, size=26, color=FOREGROUND):
        return Text(content, font=FONT, font_size=size, color=color, line_spacing=1.1)

    def clear_page(self):
        self.play(*[FadeOut(item) for item in list(self.mobjects)], run_time=0.5)

    def caption(self, content):
        replacement = self.text(content, 25, CURRENT).move_to([0, -3.4, 0])
        if hasattr(self, "caption_object"):
            self.remove(self.caption_object)
        self.caption_object = replacement
        self.add(replacement)

    def construct(self):
        config.background_color = BACKGROUND
        raw = (HERE / "geometry.json").read_bytes()
        report = json.loads((HERE.parents[1] / "experiments/results/verification.json").read_text("utf-8"))
        if not report["valid"] or hashlib.sha256(raw).hexdigest() != report["animation_geometry_sha256"]:
            raise ValueError("animation geometry does not match its verification report")
        self.principle_page()
        for index, data in enumerate(json.loads(raw)["scenes"], 1):
            self.draw_case(data, index)

    def principle_page(self):
        title = self.text("圆锥曲线弧的尺规判定", 43).move_to([0, 2.6, 0])
        lines = [
            ("两组不同方向的平行弦，各组中点连线为直径", 1.45, AUXILIARY),
            ("两条直径平行 → 抛物线", 0.65, FOREGROUND),
            ("两条直径相交 → 取得中心 O，作 A 处切线 t", -0.15, FOREGROUND),
            ("中心 O 与弧上点 B 位于切线 t 同侧 → 椭圆", -1.05, RESULT),
            ("中心 O 与弧上点 B 位于切线 t 异侧 → 双曲线", -1.85, RESULT),
        ]
        self.play(Write(title), run_time=0.8)
        content = VGroup(*[self.text(label, 27, color).move_to([0, y, 0])
                           for label, y, color in lines])
        self.play(FadeIn(content), run_time=0.7)
        self.wait(4)
        self.clear_page()

    def at(self, point):
        raw = np.array([*point, 0.0])
        return (raw - self.middle) * self.scale + np.array([0, -0.15, 0])

    def drawable_line(self, coefficients, color=CURRENT):
        a, b, c = coefficients
        # Transform the exact-exported line into screen coordinates for clipping.
        a, b, c = a / self.scale, b / self.scale, c + a * self.middle[0] + b * self.middle[1]
        c += b * 0.15
        return clipped_line((a, b, c), (-6.1, 6.1, -2.65, 2.25), color)

    def mark(self, name, point, direction=RIGHT, color=AUXILIARY):
        position = self.at(point)
        for old_name, (dot, label) in list(self.markers.items()):
            if np.linalg.norm(dot.get_center() - position) < 1e-6:
                self.remove(label)
                self.markers.pop(old_name)
                dot.set_color(color)
                break
        else:
            dot = Dot(position, radius=0.043, color=color)
        for old_dot, old_label in self.markers.values():
            distance = np.linalg.norm(old_dot.get_center() - position)
            radius = distance / 3
            if distance > 1e-6 and distance < (dot.width + old_dot.width) / 2 + 0.02:
                dot.scale_to_fit_width(min(dot.width, 2 * radius))
                old_dot.scale_to_fit_width(min(old_dot.width, 2 * radius))
        label = self.text(name, 23, color)
        directions = [direction, UP, DOWN, LEFT, RIGHT, UP + LEFT, DOWN + RIGHT, UP + RIGHT, DOWN + LEFT]
        placed = False
        for gap in (0.11, 0.25, 0.4):
            for candidate in directions:
                label.next_to(dot, candidate, buff=gap)
                box = [label.get_corner(DOWN + LEFT), label.get_center(), label.get_corner(UP + RIGHT)]
                overlaps = False
                for old_dot, old_label in self.markers.values():
                    if old_label not in self.mobjects:
                        continue
                    old_box = [old_label.get_corner(DOWN + LEFT), old_label.get_center(),
                               old_label.get_corner(UP + RIGHT)]
                    closer_to_other = (np.linalg.norm(label.get_center() - old_dot.get_center())
                                       <= np.linalg.norm(label.get_center() - position))
                    if closer_to_other or (box[0][0] < old_box[2][0] + 0.08
                            and box[2][0] > old_box[0][0] - 0.08
                            and box[0][1] < old_box[2][1] + 0.06 and box[2][1] > old_box[0][1] - 0.06):
                        overlaps = True
                        break
                if not overlaps:
                    placed = True
                    break
            if placed:
                break
        self.markers[name] = (dot, label)
        self.play(FadeIn(dot), FadeIn(label), run_time=0.28)

    def draw_line(self, coefficients, caption):
        self.caption(caption)
        line = self.drawable_line(coefficients)
        self.play(Create(line), run_time=0.65)
        self.play(line.animate.set_color(AUXILIARY), run_time=0.15)
        self.construction_lines.append(line)
        return line

    def draw_case(self, data, index):
        points = list(data["points"])
        points.extend(raw for family in data["families"] for raw in family["intersections"])
        points.extend(family[key] for family in data["families"]
                      for key in ("guide", "first_midpoint", "second_midpoint"))
        if data["center"] is not None:
            points.append(data["center"])
            points.extend(data["tangent"][key] for key in ("first", "second", "auxiliary")
                          if data["tangent"][key] is not None)
        low, high = np.min(points, axis=0), np.max(points, axis=0)
        self.middle = np.array([*((low + high) / 2), 0])
        self.scale = min(9.8 / max(high[0] - low[0], 0.5),
                         4.1 / max(high[1] - low[1], 0.5))
        self.markers = {}
        self.construction_lines = []
        heading = self.text(f"第{'一二三'[index - 1]}段可见弧", 34)
        heading.move_to([-6.3, 3.4, 0], aligned_edge=LEFT)
        rule = Line([-6.3, 3.02, 0], [6.3, 3.02, 0], color=MUTED, stroke_width=0.6)
        self.play(FadeIn(heading), Create(rule), run_time=0.4)
        self.caption("沿可见弧依次选取 A、B、C、D")
        arc = VMobject(color=INPUT, stroke_width=2)
        arc.set_points_as_corners([self.at(raw) for raw in data["arc"]])
        self.play(Create(arc), run_time=1.0)
        for name, raw, direction in zip("ABCD", data["points"],
                                        [DOWN + LEFT, DOWN + RIGHT, UP + RIGHT, UP + LEFT]):
            self.mark(name, raw, direction, INPUT)
        self.wait(0.6)
        diameters = []
        for family_index, family in enumerate(data["families"], 1):
            suffix = "₁" if family_index == 1 else "₂"
            endpoint = "C" if family_index == 1 else "D"
            self.draw_line(family["chord"], f"连接 A{endpoint}")
            if family_index == 1:
                segment = DashedLine(self.at(data["points"][0]), self.at(data["points"][1]),
                                     color=AUXILIARY, stroke_width=1)
                self.caption("连接 AB，作中点 K₁")
                self.play(Create(segment), run_time=0.4)
                self.mark("K₁", family["guide"], LEFT)
            self.draw_line(family["parallel"],
                           "过 K₁ 作 AC 的平行线" if family_index == 1
                           else "复用 AC 的中点 M₁，作 AD 的平行线")
            names = ("U", "V") if family_index == 1 else ("W", "X")
            self.caption(f"与可见弧相交，得到 {names[0]}、{names[1]}")
            for name, raw, direction in zip(names, family["intersections"], [LEFT + DOWN, RIGHT + UP]):
                self.mark(name, raw, direction)
            self.caption(f"分别作这两条平行弦的中点 M{suffix}、N{suffix}")
            self.mark(f"M{suffix}", family["first_midpoint"], LEFT + UP)
            self.mark(f"N{suffix}", family["second_midpoint"], RIGHT + DOWN)
            diameter = self.draw_line(family["diameter"], f"连接两个中点，得到直径 d{suffix}")
            diameters.append(diameter)
            diameter_label = self.text(f"d{suffix}", 23, AUXILIARY)
            diameter_label.next_to(diameter.point_from_proportion(0.82), UP, buff=0.12)
            self.play(FadeIn(diameter_label), run_time=0.2)
            self.wait(0.6)
            if family_index == 1:
                labels = [self.markers[name][1] for name in ("K₁", "U", "V", "N₁")
                          if name in self.markers]
                self.play(*[FadeOut(label) for label in labels], run_time=0.3)
        if data["center"] is None:
            self.caption("两条直径平行")
            self.play(*[line.animate.set_color(RESULT).set_stroke(width=2) for line in diameters], run_time=0.6)
            self.show_result("抛物线")
        else:
            center_position = self.at(data["center"])
            existing_name = next((name for name, (dot, label) in self.markers.items()
                                  if np.linalg.norm(dot.get_center() - center_position) < 1e-6), None)
            self.caption(f"两条直径交于已有点 {existing_name}，记为中心 O" if existing_name
                         else "两条直径相交，取得中心 O")
            self.mark("O", data["center"], LEFT, RESULT)
            self.wait(0.8)
            keep = {"A", "B", "C", "D", "U", "O"}
            fading = [item for name, items in self.markers.items() if name not in keep for item in items]
            self.play(*[FadeOut(item) for item in fading],
                      *[line.animate.set_opacity(0.13) for line in self.construction_lines], run_time=0.5)
            for name in list(self.markers):
                if name not in keep:
                    self.markers.pop(name)
            self.add(self.markers["U"][1])
            self.draw_tangent(data["tangent"])
            self.caption("连接 OB，观察它与切线 t 的位置")
            comparison = Line(self.at(data["center"]), self.at(data["points"][1]),
                              color=RESULT, stroke_width=2.2)
            self.play(Create(comparison), run_time=0.8)
            for name in ("O", "B"):
                self.markers[name][0].set_color(RESULT)
                self.markers[name][1].set_color(RESULT)
            self.caption("O、B 位于切线 t 的同侧" if data["category"] == "ellipse"
                         else "O、B 位于切线 t 的异侧，线段 OB 穿过 t")
            self.show_result(NAMES[data["category"]])
        if index < 3:
            self.clear_page()

    def draw_tangent(self, trace):
        a, b, c, d = trace["others"]
        at = trace["at"]

        def through(first, second):
            return np.cross([*first, 1], [*second, 1])

        if trace["auxiliary"] is not None:
            away_from_q = self.at(c) - self.at(trace["auxiliary"])
            dot, label = self.markers["U"]
            label.next_to(dot, away_from_q, buff=0.16)

        self.draw_line(through(a, b), "连接 BC，开始五点切线构造")
        self.draw_line(through(d, at), "连接 DA")
        self.draw_line(through(c, d), "连接 UD")
        self.draw_line(through(at, a), "连接 AB")
        self.draw_line(through(b, c), "连接 CU")
        if trace["first"] is not None:
            self.mark("S", trace["first"], RIGHT)
        if trace["second"] is not None:
            self.mark("T", trace["second"], LEFT)
        if trace["pascal_line"] is not None:
            caption = "连接 S、T" if trace["first"] is not None and trace["second"] is not None else (
                "BC 与 DA 平行，过 T 作其平行线" if trace["first"] is None
                else "UD 与 AB 平行，过 S 作其平行线")
            self.draw_line(trace["pascal_line"], caption)
        if trace["auxiliary"] is not None:
            self.mark("Q", trace["auxiliary"], self.at(trace["auxiliary"]) - self.at(c), CURRENT)
        self.caption("连接 AQ，得到 A 处切线 t" if trace["auxiliary"] is not None
                     else "过 A 作 CU 的平行线，得到切线 t")
        tangent = self.drawable_line(trace["tangent"], RESULT)
        tangent_label = self.text("t", 28, RESULT)
        tangent_label.next_to(tangent.point_from_proportion(0.18), UP, buff=0.12)
        self.play(Create(tangent), FadeIn(tangent_label), run_time=0.9)
        self.wait(0.8)
        if trace["auxiliary"] is not None:
            detail = self.tangent_detail(trace)
            self.play(FadeIn(detail), run_time=0.4)
            self.wait(1.4)
            self.play(FadeOut(detail), run_time=0.3)
        for line in self.construction_lines:
            line.set_opacity(0.1)
        for name in ("S", "T", "Q", "C", "D", "U"):
            if name in self.markers:
                for item in self.markers[name]:
                    item.set_opacity(0.2)

    def tangent_detail(self, trace):
        """Magnify the constructed U/Q neighborhood with the same affine map for every object."""
        nearby_name = "T" if trace["second"] is not None else "S"
        raw_points = {"U": np.array(trace["others"][2]),
                      nearby_name: np.array(trace["second"] if nearby_name == "T" else trace["first"]),
                      "Q": np.array(trace["auxiliary"])}
        low, high = np.min(list(raw_points.values()), axis=0), np.max(list(raw_points.values()), axis=0)
        focus = (low + high) / 2
        scale = min(2.3 / max(high[0] - low[0], 1e-12), 1.1 / max(high[1] - low[1], 1e-12))
        offset = np.array([-4.2, 1.1])
        background = Rectangle(width=3.5, height=2.6, color=MUTED, stroke_width=1,
                               fill_color=BACKGROUND, fill_opacity=1).move_to([-4.2, 1.35, 0])
        detail = VDict({"background": background,
                        "title": self.text("局部放大", 22).move_to([-4.2, 2.3, 0])})
        a, b, c, d = trace["others"]
        nearby_parents = [(c, d), (trace["at"], a)] if nearby_name == "T" else [(a, b), (d, trace["at"])]
        parents = [np.cross([*first, 1], [*second, 1]) for first, second in nearby_parents]
        parents.extend([np.cross([*b, 1], [*c, 1]), trace["pascal_line"], trace["tangent"]])
        lines = VGroup()
        for index, coefficients in enumerate(parents):
            normal = np.array(coefficients[:2]) / scale
            constant = coefficients[2] + np.dot(coefficients[:2], focus) - np.dot(normal, offset)
            lines.add(clipped_line((*normal, constant), (-5.8, -2.6, 0.35, 1.95),
                                   RESULT if index == len(parents) - 1 else AUXILIARY))
        detail.add([("lines", lines)])
        for name, raw in raw_points.items():
            position = np.array([*((raw - focus) * scale + offset), 0])
            color = CURRENT if name == "Q" else AUXILIARY
            dot = Dot(position, radius=0.035, color=color)
            direction = RIGHT if name == "U" else DOWN + LEFT if name == "Q" else UP + LEFT
            label = self.text(name, 23, color).next_to(dot, direction, buff=0.16)
            leader = Line(dot.get_center(), label.get_edge_center(-direction), color=color,
                          stroke_width=0.8, buff=0.05)
            detail.add([(name, VGroup(dot, label, leader))])
        return detail

    def show_result(self, category):
        result = self.text(f"判定结果 · {category}", 34, RESULT).move_to([3.6, 2.65, 0])
        self.play(FadeIn(result), run_time=0.5)
        self.wait(3)
