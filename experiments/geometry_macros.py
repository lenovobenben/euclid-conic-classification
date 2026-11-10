"""Independent exact line-intersection replay of signed-length arithmetic.

The reference line has O=(0,0), U=(1,0), V=(0,1). Each scalar is
represented by its signed point on OU. Parallels and perpendiculars are
the classical ruler-and-compass macros described in docs/CONSTRUCTION.md.
"""

from sage.all import AA, matrix, vector


def intersection(first, second, third, fourth):
    direction_one = vector(AA, second) - vector(AA, first)
    direction_two = vector(AA, fourth) - vector(AA, third)
    system = matrix(AA, [direction_one, -direction_two]).transpose()
    if system.det() == 0:
        raise ValueError("the two lines have no unique intersection")
    parameter = system.solve_right(vector(AA, third) - vector(AA, first))[0]
    return vector(AA, first) + parameter * direction_one


def add(left, right):
    # Lift (right,0) to (right,1), then draw a parallel to V--(left,0).
    lifted = intersection((right, 0), (right, 1), (0, 1), (1, 1))
    return intersection(lifted, lifted + vector(AA, (left, -1)), (0, 0), (1, 0))[0]


def subtract(left, right):
    return add(left, -right)


def multiply(left, right):
    # Through (left,0), parallel to U--(0,right); intersect the vertical axis.
    return intersection((left, 0), (left - 1, right), (0, 0), (0, 1))[1]


def divide(numerator, denominator):
    if denominator == 0:
        raise ValueError("division requires a nonzero denominator")
    # Through V, parallel to (0,denominator)--(numerator,0).
    return intersection((0, 1), (numerator, 1 - denominator), (0, 0), (1, 0))[0]


def replay(state):
    """Recompute every scalar row, coefficient and discriminant geometrically."""
    points = state["points"]
    origin, unit_x, unit_y = map(lambda point: vector(AA, point), points[:3])
    basis_x, basis_y = unit_x - origin, unit_y - origin
    local_points = []
    for point in map(lambda point: vector(AA, point), points):
        foot_x = intersection(origin, unit_x, point, point + basis_y)
        foot_y = intersection(origin, unit_y, point, point + basis_x)
        # Transfer the oblique y unit onto OU by a parallel to C--B.
        encoded_y = intersection(origin, unit_x, foot_y, foot_y + unit_x - unit_y)
        reference_squared = basis_x.dot_product(basis_x)
        local_points.append((
            (foot_x - origin).dot_product(basis_x) / reference_squared,
            (encoded_y - origin).dot_product(basis_x) / reference_squared,
        ))
    rows = []
    for x, y in local_points[3:]:
        rows.append((subtract(multiply(x, x), x), multiply(x, y),
                     subtract(multiply(y, y), y)))
    first, second = rows
    a = subtract(multiply(first[1], second[2]), multiply(first[2], second[1]))
    b = subtract(multiply(first[2], second[0]), multiply(first[0], second[2]))
    c = subtract(multiply(first[0], second[1]), multiply(first[1], second[0]))
    delta = subtract(multiply(b, b), multiply(4, multiply(a, c)))
    return {"local_points": local_points, "rows": rows,
            "coefficients": (a, b, c), "delta": delta}
