"""Exact conic arcs and affine transformations for verification and animation."""

from sage.all import AA, QQ, identity_matrix, matrix, vector


def canonical_point(category, parameter):
    parameter = AA(parameter)
    if category == "ellipse":
        return vector(AA, (
            2 * (1 - parameter * parameter) / (1 + parameter * parameter),
            2 * parameter / (1 + parameter * parameter),
        ))
    if category == "hyperbola":
        return vector(AA, (
            (1 + parameter * parameter) / (1 - parameter * parameter),
            2 * parameter / (1 - parameter * parameter),
        ))
    if category == "parabola":
        return vector(AA, (parameter, parameter * parameter))
    raise ValueError("unknown conic category")


def make_fixture(name, category, parameters, linear=None, translation=None):
    linear = identity_matrix(AA, 2) if linear is None else matrix(AA, linear)
    translation = vector(AA, translation or (0, 0))
    if linear.det() == 0:
        raise ValueError("the affine transformation must be invertible")
    points = [tuple(linear * canonical_point(category, t) + translation)
              for t in parameters]
    canonical_equations = {
        "ellipse": matrix(AA, [[QQ(1) / 4, 0, 0], [0, 1, 0], [0, 0, -1]]),
        "hyperbola": matrix(AA, [[1, 0, 0], [0, -1, 0], [0, 0, -1]]),
        "parabola": matrix(AA, [[1, 0, 0], [0, 0, -QQ(1) / 2],
                                 [0, -QQ(1) / 2, 0]]),
    }
    transform = matrix(AA, [
        [linear[0, 0], linear[0, 1], translation[0]],
        [linear[1, 0], linear[1, 1], translation[1]],
        [0, 0, 1],
    ])
    inverse = transform.inverse()
    equation = inverse.transpose() * canonical_equations[category] * inverse
    if category == "ellipse":
        quadratic = equation[:2, :2]
        if quadratic[0, 1] == 0 and quadratic[0, 0] == quadratic[1, 1]:
            raise ValueError("a circular ellipse is outside the project domain")
    return {
        "name": name,
        "category": category,
        "parameters": [AA(t) for t in parameters],
        "points": points,
        "linear": linear,
        "translation": translation,
        "equation": equation,
    }


def verification_fixtures():
    rational = QQ
    near = rational(1) / 10 ** 12
    fixtures = [
        make_fixture("ellipse_vertex_symmetric", "ellipse", [-2, -1, 0, 1, 2]),
        make_fixture("ellipse_long_arc", "ellipse", [-4, -1, 0, 1, 4]),
        make_fixture("ellipse_tiny_arc", "ellipse", [1 + k * near for k in range(5)]),
        make_fixture("ellipse_reflected_shear", "ellipse", [-2, -1, 0, 1, 2],
                     [[-1, 2], [0, 1]], [7, -3]),
        make_fixture("ellipse_algebraic", "ellipse", [-1, 0, rational(1) / 3, 1, 2],
                     [[AA(2).sqrt(), 0], [0, 1]], [AA(3).sqrt(), -2]),
        make_fixture("hyperbola_vertex_symmetric", "hyperbola",
                     [-rational(2) / 3, -rational(1) / 3, 0,
                      rational(1) / 3, rational(2) / 3]),
        make_fixture("hyperbola_left_branch", "hyperbola",
                     [-rational(2) / 3, -rational(1) / 3, 0,
                      rational(1) / 3, rational(2) / 3], [[-1, 0], [0, -1]]),
        make_fixture("hyperbola_tiny_arc", "hyperbola", [k * near for k in range(5)]),
        make_fixture("hyperbola_near_asymptote", "hyperbola",
                     [1 - rational(k) / 10000 for k in (5, 4, 3, 2, 1)]),
        make_fixture("hyperbola_rotated_translated", "hyperbola",
                     [-rational(2) / 3, -rational(1) / 3, 0,
                      rational(1) / 3, rational(2) / 3],
                     [[rational(3) / 5, -rational(4) / 5],
                      [rational(4) / 5, rational(3) / 5]], [3, -2]),
        make_fixture("parabola_vertex_symmetric", "parabola", [-2, -1, 0, 1, 2]),
        make_fixture("parabola_tiny_arc", "parabola", [1 + k * near for k in range(5)]),
        make_fixture("parabola_sheared", "parabola", [-2, -1, 0, 1, 2],
                     [[1, 2], [1, 1]], [-4, 3]),
        make_fixture("parabola_algebraic_point", "parabola",
                     [-1, 0, 1, AA(2).sqrt(), 2]),
    ]
    for epsilon in (rational(1) / 10 ** 30, -rational(1) / 10 ** 30):
        category = "ellipse" if epsilon > 0 else "hyperbola"
        parameters = [-2, -1, 0, 1, 2]
        fixtures.append({
            "name": f"{category}_near_parabola",
            "category": category,
            "parameters": parameters,
            "points": [
                (AA(t / (1 + epsilon * t * t)),
                 AA(t * t / (1 + epsilon * t * t))) for t in parameters
            ],
            "linear": identity_matrix(AA, 2),
            "translation": vector(AA, (0, 0)),
            "equation": matrix(AA, [[1, 0, 0], [0, epsilon, -rational(1) / 2],
                                      [0, -rational(1) / 2, 0]]),
        })
    return fixtures


def animation_fixtures():
    parameters = [-1, 1, 0, -QQ(1) / 2, QQ(1) / 2]
    return [
        make_fixture("ellipse", "ellipse", parameters),
        make_fixture("parabola", "parabola", parameters),
        make_fixture("hyperbola", "hyperbola",
                     [-QQ(1) / 2, QQ(1) / 2, 0, -QQ(1) / 4, QQ(1) / 4]),
    ]
