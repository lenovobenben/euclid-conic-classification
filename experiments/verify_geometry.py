"""Exact verification of the geometric main solution and visible-arc oracle."""

from itertools import combinations, permutations

from sage.all import AA, QQ, PolynomialRing, vector

from fixtures import canonical_point, make_fixture
from geometric_classifier import classify_arc, tangent_from_five


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def visible_arc_oracle(fixture):
    inverse = fixture["linear"].inverse()
    low, high = min(fixture["parameters"]), max(fixture["parameters"])

    def parameter_of(raw):
        x, y = inverse * (raw - fixture["translation"])
        if fixture["name"].endswith("near_parabola"):
            if x != 0:
                return y / x
            return AA(0) if y == 0 else None
        if fixture["category"] == "parabola":
            return x
        denominator = 1 + x / 2 if fixture["category"] == "ellipse" else 1 + x
        return y / denominator if denominator != 0 else None

    def intersections(line):
        a, b, c = line
        origin = vector(AA, (0, -c / b)) if b != 0 else vector(AA, (-c / a, 0))
        direction = vector(AA, (b, -a))
        homogeneous_origin = vector(AA, (*origin, 1))
        homogeneous_direction = vector(AA, (*direction, 0))
        equation = fixture["equation"]
        ring = PolynomialRing(AA, "t")
        t = ring.gen()
        polynomial = (homogeneous_direction * equation * homogeneous_direction * t * t
                      + 2 * homogeneous_origin * equation * homogeneous_direction * t
                      + homogeneous_origin * equation * homogeneous_origin)
        selected = []
        for root in polynomial.roots(AA, multiplicities=False):
            candidate = origin + root * direction
            parameter = parameter_of(candidate)
            if parameter is not None and low <= parameter <= high:
                selected.append((parameter, candidate))
        return [value for parameter, value in sorted(selected, key=lambda item: item[0])]

    return intersections


def check_tangent(trace, equation):
    at = trace["at"]
    expected = equation * vector(AA, (*at, 1))
    require(trace["tangent"].cross_product(expected).is_zero(),
            "constructed tangent disagrees with the independent gradient")


def symbolic_geometry():
    ring = PolynomialRing(QQ, [f"{letter}{i}" for i in range(5) for letter in ("u", "v")])
    parameters = ring.gens()
    points = [vector(ring, (parameters[2 * i] ** 2,
                            parameters[2 * i] * parameters[2 * i + 1],
                            parameters[2 * i + 1] ** 2)) for i in range(5)]
    a, b, c, d, at = points
    tangent = vector(ring, (at[2], -2 * at[1], at[0]))
    first = a.cross_product(b).cross_product(d.cross_product(at))
    second = c.cross_product(d).cross_product(at.cross_product(a))
    third = b.cross_product(c).cross_product(tangent)
    require(first.cross_product(second).dot_product(third) == 0,
            "homogeneous degenerate Pascal identity fails")
    require(tangent.dot_product(at) == 0, "symbolic tangent misses its contact point")
    midpoint_ring = PolynomialRing(QQ, "a,b,c,d,e,m,n,u,v,h")
    a, b, c, d, e, m, n, u, v, h = midpoint_ring.gens()

    def equation(x, y):
        return a * x * x + b * x * y + c * y * y + d * x + e * y

    require(equation(m + h * u, n + h * v) - equation(m - h * u, n - h * v)
            - 2 * h * (u * (2 * a * m + b * n + d)
                       + v * (b * m + 2 * c * n + e)) == 0,
            "parallel-chord midpoint identity fails")
    require(u * u + v * v - 2 * u * v - (u - v) ** 2 == 0,
            "same-branch hyperbola tangent-side identity fails")
    return ["homogeneous degenerate Pascal identity", "contact point lies on constructed tangent",
            "general parallel-chord midpoint identity", "hyperbola tangent-side square identity"]


def verify_geometric_solution(fixtures):
    symbolic = symbolic_geometry()
    construction_count = 0
    tangent_count = 0
    branches = set()
    records = []
    for fixture in fixtures:
        oracle = visible_arc_oracle(fixture)
        ordered = [value for parameter, value in sorted(zip(fixture["parameters"], fixture["points"]),
                                                        key=lambda item: item[0])]
        for selected in combinations(ordered, 4):
            for sequence in (selected, selected[::-1]):
                state = classify_arc(sequence, oracle)
                require(state["category"] == fixture["category"], "geometric classification is wrong")
                for family in state["families"]:
                    for raw in family["intersections"]:
                        homogeneous = vector(AA, (*raw, 1))
                        require(homogeneous * fixture["equation"] * homogeneous == 0,
                                "parallel chord has an invalid intersection")
                    if state["center"] is not None:
                        require(family["diameter"].dot_product(
                            vector(AA, (*state["center"], 1))) == 0, "diameter misses center")
                if state["tangent"] is not None:
                    check_tangent(state["tangent"], fixture["equation"])
                    # Independently check the constructed center against the source equation.
                    homogeneous_center = vector(AA, (*state["center"], 1))
                    gradient = fixture["equation"] * homogeneous_center
                    require(gradient[0] == gradient[1] == 0, "constructed center is wrong")
                construction_count += 1
        primary = classify_arc(ordered[:4], oracle)
        at = primary["points"][0]
        others = primary["points"][1:] + [primary["families"][0]["intersections"][0]]
        for ordering in permutations(others):
            tangent = tangent_from_five(at, ordering)
            check_tangent(tangent, fixture["equation"])
            tangent_count += 1
            branches.add(tangent["branch"])
        records.append({"name": fixture["name"], "category": primary["category"],
                        "ordered_quadruples_with_reversal": 10,
                        "tangent_orders": 24})

    # Dedicated exact positions exercise every parallel fallback of Pascal.
    height = AA(3).sqrt() / 2
    at = vector(AA, (2, 0))
    tangent_cases = [
        [(-1, height), (1, height), (1, -height), (-2, 0)],
        [(0, 1), (-2, 0), (QQ(6) / 5, QQ(4) / 5), (0, -1)],
        [(0, -1), (QQ(6) / 5, QQ(4) / 5), (-2, 0), (0, 1)],
        [(-QQ(6) / 5, QQ(4) / 5), (0, 1), (0, -1), (-QQ(6) / 5, -QQ(4) / 5)],
    ]
    ellipse = make_fixture("tangent_controls", "ellipse", [-1, 0, 1, 2, 3])
    for others in tangent_cases:
        tangent = tangent_from_five(at, others)
        check_tangent(tangent, ellipse["equation"])
        branches.add(tangent["branch"])
        tangent_count += 1
    require({"both_parallel", "first_parallel", "second_parallel",
             "finite_parallel_tangent", "finite"} <= branches,
            "some tangent-construction branches are untested")
    return {"symbolic_identities": symbolic,
            "construction_count": construction_count, "tangent_count": tangent_count,
            "tangent_branches": sorted(branches), "fixtures": records}


def geometric_animation_data():
    scenes = []
    fixtures = [
        make_fixture("ellipse_drawing", "ellipse", [-1, -QQ(1) / 3, QQ(1) / 3, 1]),
        make_fixture("parabola_drawing", "parabola", [-1, -QQ(1) / 3, QQ(1) / 3, 1]),
        make_fixture("hyperbola_drawing", "hyperbola", [-QQ(1) / 2, -QQ(1) / 6,
                                                         QQ(1) / 6, QQ(1) / 2], [[3, 0], [0, 1]]),
    ]

    def display(value):
        if value is None:
            return None
        return [float(coordinate) for coordinate in value]

    for fixture in fixtures:
        state = classify_arc(fixture["points"], visible_arc_oracle(fixture))
        require(state["category"] == fixture["category"], "animation decision is wrong")
        if state["tangent"] is not None:
            check_tangent(state["tangent"], fixture["equation"])
        low, high = min(fixture["parameters"]), max(fixture["parameters"])
        arc = [canonical_point(fixture["category"], low + (high - low) * QQ(i) / 240)
               for i in range(241)]
        arc = [fixture["linear"] * raw + fixture["translation"] for raw in arc]
        for raw in arc:
            homogeneous = vector(AA, (*raw, 1))
            require(homogeneous * fixture["equation"] * homogeneous == 0,
                    "animation arc sample is off the conic")
        families = [{key: [display(raw) for raw in value] if key == "intersections" else display(value)
                     for key, value in family.items()} for family in state["families"]]
        tangent = None
        if state["tangent"] is not None:
            tangent = {key: [display(raw) for raw in value] if key == "others"
                       else value if key == "branch" else display(value)
                       for key, value in state["tangent"].items()}
        scenes.append({"category": state["category"], "points": [display(raw) for raw in state["points"]],
                       "arc": [display(raw) for raw in arc], "families": families,
                       "center": display(state["center"]), "tangent": tangent})
    return {"schema_version": 2, "producer": "experiments/verify.py", "scenes": scenes}
