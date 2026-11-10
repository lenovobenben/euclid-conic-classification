"""Exact replay of the five-point ruler-and-compass decision procedure.

Run with SageMath. Only the five selected points enter the classifier.
All decisions use QQ/AA equality and order, with no numerical tolerance.
"""

from itertools import combinations

from sage.all import AA, QQ, matrix


def determinant(left, right):
    return left[0] * right[1] - left[1] * right[0]


def difference(left, right):
    return (left[0] - right[0], left[1] - right[1])


def classify_five_points(points):
    """Return the exact construction state for five noncollinear conic points.

    The geometric problem promises a connected arc of a nondegenerate real
    conic, with circles excluded. The executable accepts real algebraic
    coordinates, while the accompanying proof covers arbitrary real inputs.
    """
    if len(points) != 5:
        raise ValueError("exactly five points are required")
    if any(len(point) != 2 for point in points):
        raise ValueError("each point must have two coordinates")
    points = [tuple(AA(coordinate) for coordinate in point) for point in points]
    if len(set(points)) != 5:
        raise ValueError("the five points must be distinct")
    for first, second, third in combinations(points, 3):
        if determinant(difference(second, first), difference(third, first)) == 0:
            raise ValueError("three selected points are collinear")

    origin, unit_x, unit_y, fourth, fifth = points
    basis_x = difference(unit_x, origin)
    basis_y = difference(unit_y, origin)
    frame_determinant = determinant(basis_x, basis_y)
    local_points = []
    for point in points:
        offset = difference(point, origin)
        local_points.append((
            determinant(offset, basis_y) / frame_determinant,
            determinant(basis_x, offset) / frame_determinant,
        ))

    rows = []
    for x, y in local_points[3:]:
        rows.append((x * x - x, x * y, y * y - y))
    first, second = rows
    a = first[1] * second[2] - first[2] * second[1]
    b = first[2] * second[0] - first[0] * second[2]
    c = first[0] * second[1] - first[1] * second[0]
    if a == b == c == 0:
        raise ArithmeticError("the interpolation rows have lost rank")
    delta = b * b - 4 * a * c
    category = {-1: "ellipse", 0: "parabola", 1: "hyperbola"}[delta.sign()]
    return {
        "points": points,
        "frame_determinant": frame_determinant,
        "local_points": local_points,
        "rows": rows,
        "coefficients": (a, b, c),
        "delta": delta,
        "category": category,
    }


def independent_conic(points):
    """Recover the full equation with an independent 5 by 6 nullspace solve."""
    evaluation = matrix(AA, [
        [x * x, x * y, y * y, x, y, 1] for x, y in points
    ])
    kernel = evaluation.right_kernel()
    if kernel.dimension() != 1:
        raise ValueError("the five points do not determine a unique conic")
    coefficients = tuple(kernel.basis()[0])
    a, b, c, d, e, f = coefficients
    homogeneous = matrix(AA, [
        [a, b / 2, d / 2],
        [b / 2, c, e / 2],
        [d / 2, e / 2, f],
    ])
    if homogeneous.det() == 0:
        raise ValueError("the recovered conic is degenerate")
    return coefficients, homogeneous


def exact_record(value):
    """Serialize an algebraic number by a rational or an isolating interval."""
    value = AA(value)
    if value in QQ:
        return str(QQ(value))
    polynomial = value.minpoly()
    roots = polynomial.roots(AA, multiplicities=False)
    bits = 64
    while True:
        denominator = 2 ** bits
        lower = QQ((value * denominator).floor()) / denominator
        upper = lower + QQ(1) / denominator
        if sum(lower < root < upper for root in roots) == 1:
            return {
                "minimal_polynomial": str(polynomial),
                "lower": str(lower),
                "upper": str(upper),
            }
        bits *= 2
