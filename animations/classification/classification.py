"""A complete conic-type decision, illustrated with certified exact cases."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from manim import (
    Create, DashedLine, Dot, FadeIn, FadeOut, Line, MathTex,
    NumberLine, Scene, Text, VGroup, VMobject, Write,
    DOWN, LEFT, RIGHT, UP, config,
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


def tex_number(value):
    number = Fraction(value)
    if number.denominator == 1:
        return str(number.numerator)
    sign = "-" if number < 0 else ""
    return rf"{sign}\frac{{{abs(number.numerator)}}}{{{number.denominator}}}"


def tex_pair(point):
    return rf"\left({tex_number(point[0])},{tex_number(point[1])}\right)"


class ConicClassification(Scene):
    def text(self, content, size=26, color=FOREGROUND):
        return Text(content, font=FONT, font_size=size, color=color, line_spacing=1.1)

    def formula(self, content, location, size=32, color=FOREGROUND):
        return MathTex(content, font_size=size, color=color).move_to(location)

    def heading(self, title, subtitle):
        title_object = self.text(title, 34).move_to([-6.6, 3.45, 0], aligned_edge=LEFT)
        subtitle_object = self.text(subtitle, 20, MUTED).move_to(
            [-6.6, -3.55, 0], aligned_edge=LEFT,
        )
        divider = Line([-6.6, 3.03, 0], [6.6, 3.03, 0], color=MUTED, stroke_width=0.6)
        self.play(FadeIn(title_object), Create(divider), FadeIn(subtitle_object), run_time=0.6)

    def clear_page(self):
        self.play(*[FadeOut(item) for item in list(self.mobjects)], run_time=0.5)

    def construct(self):
        config.background_color = BACKGROUND
        geometry_bytes = (HERE / "geometry.json").read_bytes()
        report = json.loads((HERE.parents[1] / "experiments/results/verification.json").read_text("utf-8"))
        if not report["valid"] or hashlib.sha256(geometry_bytes).hexdigest() != report["animation_geometry_sha256"]:
            raise ValueError("animation geometry does not match its verification report")
        data = json.loads(geometry_bytes)
        self.introduction()
        self.show_case(data["scenes"][0], detailed=True)
        self.show_multiplication()
        self.show_decision(data["scenes"][0])
        self.show_case(data["scenes"][1])
        self.show_decision(data["scenes"][1])
        self.show_case(data["scenes"][2])
        self.show_decision(data["scenes"][2])
        self.finish()

    def introduction(self):
        title = self.text("由一段弧，判定圆锥曲线类型", 43).move_to(UP * 2.35)
        problem = self.text(
            "给定一段非零长度的可见弧\n"
            "已知所属曲线为非圆椭圆、抛物线或双曲线",
            28,
        ).move_to(UP * 0.9)
        tools = self.text("无刻度直尺与圆规 · 允许在弧上选点", 26, CURRENT).move_to(DOWN * 0.45)
        goal = self.text("构造判别信息，得到曲线类别", 32, RESULT).move_to(DOWN * 1.5)
        scope = self.text("长弧、短弧、顶点与对称情形均在题面范围内", 23, MUTED).move_to(DOWN * 2.6)
        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(problem), FadeIn(tools), run_time=0.8)
        self.play(FadeIn(goal), FadeIn(scope), run_time=0.7)
        self.wait(3.4)
        self.clear_page()

    def show_case(self, data, detailed=False):
        self.heading(
            "五个点，提取一个完整的判别量" if detailed else "同一流程，处理另一段可见弧",
            "洋红为输入 · 金色为当前操作 · 淡蓝为辅助 · 绿色为判定结果",
        )
        points = [np.array([*point, 0.0]) for point in data["points"]]
        origin, unit_x, unit_y = points[:3]
        basis_x, basis_y = unit_x - origin, unit_y - origin
        all_points = list(points)
        projections = []
        for point, local in zip(points[3:], data["local_points"][3:]):
            x, y = map(lambda value: float(Fraction(value)), local)
            foot_x, foot_y = origin + x * basis_x, origin + y * basis_y
            encoded_y = origin + y * basis_x
            projections.append((point, foot_x, foot_y, encoded_y))
            all_points.extend((foot_x, foot_y, encoded_y))
        low = np.min(all_points, axis=0)
        high = np.max(all_points, axis=0)
        middle = (low + high) / 2
        scale = min(5.2 / max(high[0] - low[0], 0.1),
                    4.4 / max(high[1] - low[1], 0.1))

        def at(point):
            return (point - middle) * scale + np.array([-3.7, 0.1, 0.0])

        arc = VMobject(color=INPUT, stroke_width=2.1)
        arc.set_points_as_corners([at(np.array([*point, 0.0])) for point in data["arc"]])
        self.play(Create(arc), run_time=1.1)
        offsets = [LEFT + DOWN * 0.4, LEFT + UP * 0.5, RIGHT,
                   LEFT + DOWN * 0.3, RIGHT + UP * 0.4]
        for name, point, offset in zip(("A", "B", "C", "D", "E"), points, offsets):
            dot = Dot(at(point), radius=0.045, color=INPUT)
            label = self.text("C₀" if name == "C" else name, 23, INPUT)
            label.next_to(dot, offset, buff=0.12)
            self.play(FadeIn(dot), FadeIn(label), run_time=0.25)
        note = self.text("在可见弧上选取五个不同点", 24, CURRENT).move_to([3.1, 2.3, 0])
        self.play(FadeIn(note), run_time=0.4)
        self.wait(0.6)
        axis_x = Line(at(origin), at(unit_x), color=AUXILIARY, stroke_width=1.3)
        axis_y = Line(at(origin), at(unit_y), color=AUXILIARY, stroke_width=1.3)
        self.play(Create(axis_x), Create(axis_y), run_time=0.8)
        frame = self.formula(r"A=(0,0),\ B=(1,0),\ C_0=(0,1)", [3.1, 1.55, 0], 30)
        frame_note = self.text("由三个输入点自建斜标架", 22, AUXILIARY).move_to([3.1, 0.9, 0])
        self.play(Write(frame), FadeIn(frame_note), run_time=0.8)
        if detailed:
            self.wait(1.3)
        for index, (point, foot_x, foot_y, encoded_y) in enumerate(projections):
            lines = VGroup(
                DashedLine(at(point), at(foot_x), color=CURRENT, stroke_width=1.5),
                DashedLine(at(point), at(foot_y), color=CURRENT, stroke_width=1.5),
                DashedLine(at(foot_y), at(encoded_y), color=CURRENT, stroke_width=1.5),
            )
            if detailed:
                for line in lines:
                    self.play(Create(line), run_time=0.45)
            else:
                self.play(Create(lines), run_time=0.6)
            markers = VGroup(*[Dot(at(foot), radius=0.035, color=CURRENT)
                               for foot in (foot_x, foot_y, encoded_y)])
            self.play(FadeIn(markers), run_time=0.2)
            name = "D" if index == 0 else "E"
            coordinate = self.formula(
                f"{name}={tex_pair(data['local_points'][3 + index])}",
                [3.1, 0.1 - 0.8 * index, 0], 34, CURRENT,
            )
            self.play(Write(coordinate), run_time=0.6)
            self.wait(0.7 if detailed else 0.3)
            self.play(lines.animate.set_color(AUXILIARY), markers.animate.set_color(AUXILIARY),
                      run_time=0.2)
        self.wait(0.8)
        self.clear_page()
        self.heading("由长度运算，构造二次项", "所有坐标和系数都表示为同一条定向直线上的点")
        equation = self.formula(r"ax^2+bxy+cy^2-ax-cy=0", [0, 2.2, 0], 38)
        definitions = self.formula(
            r"r_1=(u^2-u,uv,v^2-v),\quad r_2=(w^2-w,wz,z^2-z)",
            [0, 1.2, 0], 32,
        )
        coordinates = self.formula(
            rf"D={tex_pair(data['local_points'][3])},\quad E={tex_pair(data['local_points'][4])}",
            [0, 0.25, 0], 32, AUXILIARY,
        )
        cross = self.formula(r"(a,b,c)=r_1\times r_2", [0, -0.75, 0], 40, CURRENT)
        coefficient_values = ",".join(data["normalized_coefficients"])
        result = self.formula(rf"(a,b,c)\sim({coefficient_values})", [0, -1.75, 0], 43, RESULT)
        explanation = self.text("共同非零倍数保持判别量符号", 24, MUTED).move_to([0, -2.7, 0])
        self.play(Write(equation), run_time=0.7)
        self.play(Write(definitions), FadeIn(coordinates), run_time=0.9)
        self.play(Write(cross), run_time=0.7)
        self.wait(1.0 if detailed else 0.4)
        self.play(Write(result), FadeIn(explanation), run_time=0.8)
        self.wait(2.0 if detailed else 1.1)
        self.clear_page()

    def show_multiplication(self):
        self.heading("相似三角形，把乘积构造成长度", "平行线、垂线和长度转移均采用经典尺规宏")
        scale = 0.88

        def at(x, y):
            return np.array([-5.6 + scale * x, -2 + scale * y, 0.0])

        axis = VGroup(Line(at(-0.5, 0), at(4.6, 0), color=AUXILIARY, stroke_width=1.2),
                      Line(at(0, -0.4), at(0, 4.7), color=AUXILIARY, stroke_width=1.2))
        labels = VGroup()
        for x, y, name, direction in ((0, 0, "O", LEFT + DOWN), (1, 0, "I", DOWN),
                                       (0, 1, "H", LEFT), (2, 0, "X", DOWN),
                                       (0, 2, "Y", LEFT)):
            dot = Dot(at(x, y), radius=0.045, color=AUXILIARY)
            label = self.text(name, 23, AUXILIARY).next_to(dot, direction, buff=0.12)
            labels.add(dot, label)
        equation = self.formula(r"x=2,\quad y=2", [3.1, 1.6, 0], 40)
        relation = self.formula(r"XZ\parallel IY", [3.1, 0.5, 0], 42, CURRENT)
        product = self.formula(r"OZ=xy=4", [3.1, -0.7, 0], 43, RESULT)
        self.play(Create(axis), FadeIn(labels), Write(equation), run_time=0.9)
        diagonal = Line(at(1, 0), at(0, 2), color=AUXILIARY, stroke_width=1.7)
        parallel = Line(at(2, 0), at(0, 4), color=CURRENT, stroke_width=1.8)
        self.play(Create(diagonal), run_time=0.7)
        self.play(Create(parallel), Write(relation), run_time=1.0)
        point = Dot(at(0, 4), radius=0.055, color=RESULT)
        label = self.text("Z", 25, RESULT).next_to(point, LEFT, buff=0.15)
        self.play(FadeIn(point), FadeIn(label), Write(product), run_time=0.8)
        self.wait(2.3)
        transfer = self.text("将有向长度转回参考数轴，即得到乘积点", 24, MUTED)
        transfer.move_to([0, -2.9, 0])
        self.play(FadeIn(transfer), run_time=0.6)
        self.wait(1.7)
        self.clear_page()

    def show_decision(self, data):
        self.heading("构造判别量，读取最终类别", "结果由精确的正、零、负关系决定")
        a, b, c = data["normalized_coefficients"]
        expression = self.formula(r"\Delta=b^2-4ac", [0, 2.0, 0], 48, CURRENT)
        values = self.formula(
            rf"\Delta={b}^2-4\cdot{a}\cdot{c}={data['normalized_delta']}",
            [0, 0.95, 0], 40,
        )
        sign = data["sign"]
        symbol = {-1: "<", 0: "=", 1: ">"}[sign]
        exact_value = Fraction(data["normalized_delta"])
        tick_range = [-80, 80, 20] if abs(exact_value) > 5 else [-5, 5, 1]
        line = NumberLine(x_range=tick_range, length=10.0, include_numbers=True,
                          font_size=24, color=AUXILIARY, stroke_width=1.2,
                          include_tip=True).move_to([0, -0.7, 0])
        marker = Dot(line.n2p(float(exact_value)), radius=0.075, color=RESULT)
        marker_label = self.formula(rf"\Delta {symbol} 0", [0, -1.65, 0], 42, RESULT)
        output = self.text(f"判定结果 · {NAMES[data['category']]}", 39, RESULT).move_to([0, -2.65, 0])
        line_note = self.text("以 AB 为有向单位", 19, MUTED)
        line_note.next_to(line, UP, buff=0.2).align_to(line, RIGHT)
        self.play(Write(expression), run_time=0.7)
        self.play(Write(values), run_time=0.8)
        self.play(Create(line), FadeIn(line_note), run_time=0.6)
        self.play(FadeIn(marker), Write(marker_label), run_time=0.6)
        self.play(FadeIn(output), run_time=0.6)
        self.wait(2.3)
        self.clear_page()

    def finish(self):
        self.heading("为什么这是一条覆盖全部输入的通解", "一般证明见 docs/PROOF.md · 精确核验见 experiments/results/verification.json")
        statements = [
            ("任意五个不同点", "非退化圆锥曲线上，任意三点不共线"),
            ("五点确定唯一方程", "两行辅助量始终独立，叉积始终非零"),
            ("判别量符号保持不变", "更换标架，只乘以严格为正的平方因子"),
        ]
        for index, (title, detail) in enumerate(statements):
            y = 2.0 - index * 1.25
            heading = self.text(title, 29, CURRENT).move_to([-5.9, y, 0], aligned_edge=LEFT)
            body = self.text(detail, 24).move_to([-5.9, y - 0.5, 0], aligned_edge=LEFT)
            self.play(FadeIn(heading), FadeIn(body), run_time=0.65)
        result = self.formula(
            r"\Delta<0\quad\vert\quad\Delta=0\quad\vert\quad\Delta>0",
            [0, -2.05, 0], 40, RESULT,
        )
        categories = self.text("椭圆                 抛物线                 双曲线", 27, RESULT)
        categories.move_to([0, -2.8, 0])
        self.play(Write(result), FadeIn(categories), run_time=0.8)
        self.wait(4.0)
