"""Symbolic identities, independent exact recovery, and branch coverage fixtures.

sage -python experiments/verify.py
sage -python experiments/verify.py --write
"""

import argparse
import hashlib
import json
from itertools import permutations
from pathlib import Path

from sage.all import AA, QQ, ZZ, PolynomialRing, gcd, lcm, matrix, vector
from sage.env import SAGE_VERSION

from conic_classifier import classify_five_points, exact_record, independent_conic
from fixtures import animation_fixtures, canonical_point, verification_fixtures
from geometry_macros import add, divide, multiply, replay, subtract


ROOT = Path(__file__).resolve().parents[1]


def require(condition, description):
    if not condition:
        raise ArithmeticError(description)


def symbolic_verification():
    ring = PolynomialRing(QQ, "a,b,c,p,q,r,s,h,k,u,v,w,z")
    a, b, c, p, q, r, s, h, k, u, v, w, z = ring.gens()
    checks = []

    def check(expression, description):
        require(expression == 0, description)
        checks.append(description)

    quadratic = matrix(ring, [[a, b / 2], [b / 2, c]])
    linear = matrix(ring, [[p, q], [r, s]])
    transformed = linear.transpose() * quadratic * linear
    check(4 * transformed[0, 1] ** 2 - 4 * transformed[0, 0] * transformed[1, 1]
          - linear.det() ** 2 * (b * b - 4 * a * c),
          "discriminant changes by the positive squared frame determinant")
    scaled = h * quadratic
    check(4 * scaled[0, 1] ** 2 - 4 * scaled[0, 0] * scaled[1, 1]
          - h * h * (b * b - 4 * a * c),
          "rescaling a conic equation changes the discriminant by a square")
    homogeneous = matrix(ring, [
        [a, b / 2, -a / 2], [b / 2, c, -c / 2], [-a / 2, -c / 2, 0],
    ])
    check(4 * homogeneous.det() - a * c * (b - a - c),
          "normalized homogeneous determinant")
    first = vector(ring, [u * u - u, u * v, v * v - v])
    second = vector(ring, [w * w - w, w * z, z * z - z])
    cross = first.cross_product(second)
    check(first.dot_product(cross), "cross product annihilates the fourth-point row")
    check(second.dot_product(cross), "cross product annihilates the fifth-point row")
    for x, y in ((0, 0), (1, 0), (0, 1)):
        check(a * x * x + b * x * y + c * y * y - a * x - c * y,
              f"normalized equation passes through ({x},{y})")
    offset_x, offset_y = u - h, v - k
    denominator = linear.det()
    numerator_x = s * offset_x - q * offset_y
    numerator_y = p * offset_y - r * offset_x
    check(p * numerator_x + q * numerator_y - denominator * offset_x,
          "parallel projection recovers the first affine coordinate")
    check(r * numerator_x + s * numerator_y - denominator * offset_y,
          "parallel projection recovers the second affine coordinate")
    check((-u) * v - (u * v) * (-1), "multiplication intercept lies on the prescribed parallel")
    check((u / v) * (-v) - (-u), "division intercept lies on the prescribed parallel")
    check((u + v - v) * (-1) - (-u), "addition intercept lies on the prescribed parallel")

    interpolation_ring = PolynomialRing(QQ, [f"{axis}{i}" for i in range(5)
                                               for axis in ("x", "y")])
    coordinates = list(interpolation_ring.gens())
    selected = [(coordinates[2 * i], coordinates[2 * i + 1]) for i in range(5)]

    def line_value(first_point, second_point, at):
        return ((second_point[0] - first_point[0]) * (at[1] - first_point[1])
                - (second_point[1] - first_point[1]) * (at[0] - first_point[0]))

    for index in range(5):
        others = [point for position, point in enumerate(selected) if position != index]
        diagonal = (line_value(others[0], others[1], selected[index])
                    * line_value(others[2], others[3], selected[index]))
        require(diagonal != 0, "interpolation diagonal must be a nonzero polynomial")
        for point in others:
            require(line_value(others[0], others[1], point)
                    * line_value(others[2], others[3], point) == 0,
                    "interpolation quadratic must vanish at the other four points")
        checks.append(f"quadratic interpolation witness for point {index + 1}")
    return checks


def verify_fixture(fixture):
    points = fixture["points"]
    state = classify_five_points(points)
    require(state["category"] == fixture["category"], "classification disagrees with source")
    a, b, c = state["coefficients"]
    for x, y in state["local_points"]:
        require(a * x * x + b * x * y + c * y * y - a * x - c * y == 0,
                "constructed equation misses a selected point")
    recovered, independent = independent_conic(points)
    source = fixture["equation"]
    require(source.det() != 0, "source conic is degenerate")
    source_scale = next(known / computed for known, computed in
                        zip(source.list(), independent.list()) if computed != 0)
    require(source == source_scale * independent, "independent recovery disagrees with source")
    for point in points:
        homogeneous_point = vector(AA, (*point, 1))
        require(homogeneous_point * source * homogeneous_point == 0,
                "source point is off the source conic")
    origin, unit_x, unit_y = points[:3]
    frame = matrix(AA, [
        [unit_x[0] - origin[0], unit_y[0] - origin[0], origin[0]],
        [unit_x[1] - origin[1], unit_y[1] - origin[1], origin[1]],
        [0, 0, 1],
    ])
    pulled_back = frame.transpose() * independent * frame
    constructed = matrix(AA, [
        [a, b / 2, -a / 2], [b / 2, c, -c / 2], [-a / 2, -c / 2, 0],
    ])
    scale = next(left / right for left, right in zip(constructed.list(), pulled_back.list())
                 if right != 0)
    require(constructed == scale * pulled_back, "constructed coefficients are inconsistent")
    independent_delta = recovered[1] ** 2 - 4 * recovered[0] * recovered[2]
    require(state["delta"] == scale ** 2 * frame.det() ** 2 * independent_delta,
            "exact discriminant congruence fails")
    require(state["delta"].sign() == independent_delta.sign(), "independent sign check fails")
    geometric = replay(state)
    for field in ("local_points", "rows", "coefficients", "delta"):
        require(geometric[field] == state[field], f"geometric macro replay differs in {field}")
    for reordered in permutations(points):
        reordered_state = classify_five_points(reordered)
        require(reordered_state["category"] == fixture["category"],
                "a point permutation changes the decision")
    return {
        "name": fixture["name"],
        "category": state["category"],
        "points": [[exact_record(value) for value in point] for point in points],
        "local_points": [[exact_record(value) for value in point]
                         for point in state["local_points"]],
        "coefficients": [exact_record(value) for value in state["coefficients"]],
        "delta": exact_record(state["delta"]),
        "sign": int(state["delta"].sign()),
        "point_permutations": 120,
        "independent_recovery": True,
        "geometric_macro_replay": True,
    }


def negative_controls():
    valid = verification_fixtures()[0]["points"]
    invalid = {
        "four_points": valid[:4],
        "six_points": valid + [(3, 7)],
        "duplicate_point": valid[:4] + [valid[0]],
        "collinear_triple": [(0, 0), (1, 0), (2, 0), (1, 2), (3, 4)],
        "malformed_point": valid[:4] + [(1, 2, 3)],
    }
    for name, points in invalid.items():
        try:
            classify_five_points(points)
        except ValueError:
            continue
        raise ArithmeticError(f"invalid input was accepted: {name}")
    return list(invalid)


def verify_arithmetic_macros():
    operands = [QQ(-3) / 2, QQ(-1), QQ(0), QQ(1), QQ(5) / 3]
    count = 0
    for left in operands:
        for right in operands:
            require(add(left, right) == left + right, "geometric addition fails")
            require(subtract(left, right) == left - right, "geometric subtraction fails")
            require(multiply(left, right) == left * right, "geometric multiplication fails")
            count += 3
            if right != 0:
                require(divide(left, right) == left / right, "geometric division fails")
                count += 1
    try:
        divide(1, 0)
    except ValueError:
        return {"exact_operation_checks": count, "zero_divisor_rejected": True}
    raise ArithmeticError("geometric division accepted a zero denominator")


def animation_data():
    scenes = []
    for fixture in animation_fixtures():
        state = classify_five_points(fixture["points"])
        require(state["category"] == fixture["category"], "animation classification is wrong")
        parameters = fixture["parameters"]
        low, high = min(parameters), max(parameters)
        curve = [canonical_point(fixture["category"], low + (high - low) * QQ(i) / 240)
                 for i in range(241)]
        curve = [fixture["linear"] * point + fixture["translation"] for point in curve]
        for point in curve:
            homogeneous_point = vector(AA, (*point, 1))
            require(homogeneous_point * fixture["equation"] * homogeneous_point == 0,
                    "animation arc sample lies off its conic")
        coefficients = [QQ(value) for value in state["coefficients"]]
        denominator = lcm([value.denominator() for value in coefficients])
        integers = [ZZ(value * denominator) for value in coefficients]
        common = gcd(integers)
        if next(value for value in integers if value != 0) < 0:
            common = -common
        normalized = [value / common for value in integers]
        normalized_delta = normalized[1] ** 2 - 4 * normalized[0] * normalized[2]
        require(normalized_delta.sign() == state["delta"].sign(), "display normalization fails")
        scenes.append({
            "category": state["category"],
            "points": [[float(value) for value in point] for point in fixture["points"]],
            "arc": [[float(value) for value in point] for point in curve],
            "local_points": [[exact_record(value) for value in point]
                             for point in state["local_points"]],
            "rows": [[exact_record(value) for value in row] for row in state["rows"]],
            "coefficients": [exact_record(value) for value in state["coefficients"]],
            "delta": exact_record(state["delta"]),
            "sign": int(state["delta"].sign()),
            "normalized_coefficients": [str(value) for value in normalized],
            "normalized_delta": str(normalized_delta),
        })
    return {"schema_version": 1, "producer": "experiments/verify.py", "scenes": scenes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="save reports and animation geometry")
    args = parser.parse_args()
    identities = symbolic_verification()
    fixtures = [verify_fixture(fixture) for fixture in verification_fixtures()]
    controls = negative_controls()
    arithmetic = verify_arithmetic_macros()
    geometry = animation_data()
    geometry_bytes = (json.dumps(geometry, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    source_files = [Path(__file__), Path(__file__).with_name("conic_classifier.py"),
                    Path(__file__).with_name("fixtures.py"),
                    Path(__file__).with_name("geometry_macros.py")]
    report = {
        "valid": True,
        "sage_version": SAGE_VERSION,
        "arithmetic": "QQ and AA, exact equality and exact order",
        "symbolic_identity_count": len(identities),
        "symbolic_identities": identities,
        "fixture_count": len(fixtures),
        "point_permutation_count": sum(fixture["point_permutations"] for fixture in fixtures),
        "negative_controls": controls,
        "arithmetic_macro_checks": arithmetic,
        "fixtures": fixtures,
        "animation_geometry_sha256": hashlib.sha256(geometry_bytes).hexdigest(),
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in source_files},
    }
    report_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        report_path = ROOT / "experiments/results/verification.json"
        geometry_path = ROOT / "animations/classification/geometry.json"
        for path, content in ((report_path, report_text.encode("utf-8")),
                              (geometry_path, geometry_bytes)):
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_bytes(content)
            temporary.replace(path)
    print(report_text, end="")


if __name__ == "__main__":
    main()
