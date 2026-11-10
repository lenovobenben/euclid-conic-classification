# Euclid-Conic-Classification

[简体中文](README.md) · **English**

**Classify a visible conic arc through constructed diameters, a tangent and point-side relations.**

The input is a nonzero connected arc of a nondegenerate real conic, promised to be a noncircular ellipse, a parabola or a hyperbola. Point selection in arc order and intersections of constructed lines with the visible arc are allowed. The method covers arbitrary short and long arcs, vertices and symmetry.

[4K60 construction animation](animations/classification/media/ConicClassification_4k60.mp4) · [Construction, Chinese](docs/ANSWER.md) · [Full-domain proof, Chinese](docs/PROOF.md)

## Geometric procedure

Choose four distinct points $A,B,C,D$ in arc order.

1. Through the midpoint of $AB$, draw a parallel to $AC$. Its two visible intersections determine a second parallel chord. Joining the chord midpoints gives the first diameter.
2. Through the midpoint of $AC$, draw a parallel to $AD$. Repeat to obtain the second diameter.
3. Parallel diameters identify a parabola.
4. Otherwise their intersection is the center $O$. Construct the tangent $t$ at $A$ from five already available points using the degenerate Pascal construction.
5. The points $O,B$ lie on the same side of $t$ for an ellipse, and on opposite sides of $t$ for a hyperbola.

The construction uses classical midpoint and parallel macros. Its final output comes from incidence and side relations. All parallel cases in the tangent construction have explicit finite fallback steps.

## Full-domain guarantee

Every ordered quadruple of distinct arc points works. Continuity guarantees both intersections of each auxiliary parallel lie on the visible arc. The two chord directions differ automatically. The midpoint-diameter theorem separates parabolas from central conics, and the tangent-side test separates ellipses from hyperbolas. All construction branches and exclusions are proved in [PROOF](docs/PROOF.md).

Step minimization is deferred. Algebraic five-point interpolation and discriminant calculations are preserved as a separate theoretical and verification reference in [ALGEBRA](docs/ALGEBRA.md).

## Exact verification

SageMath 10.7 verifies four general geometric identities, 160 geometric construction replays and 388 tangent constructions including every parallel fallback. Independent algebraic checks retain 18 identities and interpolation witnesses, 16 exact fixtures, all 1,920 point permutations, 95 signed-arithmetic checks and five invalid-input controls.

All mathematical decisions use rational numbers, symbolic polynomials and the exact real algebraic field `AA`. Tiny-arc and near-parabolic cases are included. The general coverage guarantee is supplied by the proof.

```sh
docker run --rm --network none \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD:/workspace:ro" -w /workspace \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/verify.py
```

Run from the project root. The expected exit status is zero and `valid` is `true`. Windows, regeneration and rendering commands are in [REPRODUCING](docs/REPRODUCING.md).

## Animation and sources

The 75.35-second 4K60 Manim video opens with one brief principle page, followed by the actual construction flow and final classifications. Some standard midpoint and parallel auxiliary circles are omitted for clarity. Full reasoning is provided in the documents. Geometry and decisions are exported after exact verification and checked by hash before rendering.

The problem and parallel-chord midpoint idea come from the user's original `ai-math-notes` exchange. The historical conversation and corrections are preserved with attribution. The four completed Euclid projects remain methodological and visual references. [Source discussion](docs/LITERATURE.md) · [Original exchange](sources/original_conic_qa.md)
