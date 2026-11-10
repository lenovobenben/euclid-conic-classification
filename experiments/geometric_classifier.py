"""Midpoint diameters and a constructed tangent classify a visible conic arc.

The classifier receives four points in arc order and an intersection oracle
for the visible arc. It never receives a conic equation or numerical lengths.
Coordinates in this replay encode exact point/line constructions only.
"""

from sage.all import AA, vector


def point(value):
    return vector(AA, value)


def join(first, second):
    first, second = point(first), point(second)
    result = vector(AA, (*first, 1)).cross_product(vector(AA, (*second, 1)))
    if result[0] == result[1] == 0:
        raise ValueError("two distinct finite points are needed for a line")
    return result


def meet(first, second):
    intersection = point(first).cross_product(point(second))
    if intersection.is_zero():
        raise ValueError("coincident lines do not determine an intersection")
    if intersection[2] == 0:
        return None
    return vector(AA, [intersection[0] / intersection[2], intersection[1] / intersection[2]])


def parallel_through(at, line):
    return vector(AA, [line[0], line[1], -line[0] * at[0] - line[1] * at[1]])


def midpoint(first, second):
    return (point(first) + point(second)) / 2


def tangent_from_five(at, others):
    """Degenerate Pascal construction, including all parallel-line branches."""
    a, b, c, d = map(point, others)
    at = point(at)
    ab, dp, cd, pa, bc = join(a, b), join(d, at), join(c, d), join(at, a), join(b, c)
    first = meet(ab, dp)
    second = meet(cd, pa)
    pascal_line = None
    auxiliary = None
    if first is None and second is None:
        branch = "both_parallel"
        tangent = parallel_through(at, bc)
    else:
        if first is None:
            branch = "first_parallel"
            pascal_line = parallel_through(second, ab)
        elif second is None:
            branch = "second_parallel"
            pascal_line = parallel_through(first, cd)
        else:
            branch = "finite"
            pascal_line = join(first, second)
        auxiliary = meet(pascal_line, bc)
        if auxiliary is None:
            branch += "_parallel_tangent"
            tangent = parallel_through(at, bc)
        else:
            tangent = join(at, auxiliary)
    return {
        "at": at, "others": [a, b, c, d], "first": first, "second": second,
        "pascal_line": pascal_line, "auxiliary": auxiliary,
        "tangent": tangent, "branch": branch,
    }


def chord_family(start, middle, end, intersect_visible_arc):
    chord = join(start, end)
    guide = midpoint(start, middle)
    parallel = parallel_through(guide, chord)
    intersections = [point(value) for value in intersect_visible_arc(parallel)]
    if len(intersections) != 2 or intersections[0] == intersections[1]:
        raise ValueError("the selected parallel must have two visible intersections")
    first_midpoint = midpoint(start, end)
    second_midpoint = midpoint(*intersections)
    return {
        "chord": chord, "guide": guide, "parallel": parallel,
        "intersections": intersections, "first_midpoint": first_midpoint,
        "second_midpoint": second_midpoint,
        "diameter": join(first_midpoint, second_midpoint),
    }


def classify_arc(ordered_points, intersect_visible_arc):
    if len(ordered_points) != 4:
        raise ValueError("four points in arc order are required")
    a, b, c, d = map(point, ordered_points)
    families = [chord_family(a, b, c, intersect_visible_arc),
                chord_family(a, c, d, intersect_visible_arc)]
    center = meet(families[0]["diameter"], families[1]["diameter"])
    tangent = None
    if center is None:
        category = "parabola"
    else:
        extra = families[0]["intersections"][0]
        tangent = tangent_from_five(a, [b, c, extra, d])
        line = tangent["tangent"]
        center_side = line.dot_product(vector(AA, (*center, 1)))
        point_side = line.dot_product(vector(AA, (*b, 1)))
        if center_side == 0 or point_side == 0:
            raise ArithmeticError("a legal center or second conic point lies on the tangent")
        category = "ellipse" if center_side * point_side > 0 else "hyperbola"
    return {"points": [a, b, c, d], "families": families, "center": center,
            "tangent": tangent, "category": category}
