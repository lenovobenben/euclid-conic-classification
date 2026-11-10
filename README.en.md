# Euclid-Conic-Classification

[简体中文](README.md) · **English**

**Classify a conic from a visible arc using a finite straightedge-and-compass procedure.**

The input is a nonzero connected arc of a nondegenerate real conic, promised to be a noncircular ellipse, a parabola, or a hyperbola. Selecting auxiliary points on the visible arc is allowed. The method works for every choice of five distinct points, including symmetric arcs, vertex-containing arcs, and arbitrarily short arcs.

[4K60 animation](animations/classification/media/ConicClassification_4k60.mp4) · [Complete solution, Chinese](docs/ANSWER.md) · [Proof, Chinese](docs/PROOF.md) · [Exact report](experiments/results/verification.json)

## Decision procedure

Select five distinct points $A,B,C_0,D,E$. Build the affine frame

$$A=(0,0),\quad B=(1,0),\quad C_0=(0,1).$$

Construct the coordinates $D=(u,v)$ and $E=(w,z)$ using parallels. Signed-length arithmetic is implemented through similar triangles. Set

$$r_1=(u^2-u,uv,v^2-v),\quad r_2=(w^2-w,wz,z^2-z),$$

$$(a,b,c)=r_1\times r_2,\quad \Delta=b^2-4ac.$$

The three outcomes are

| Condition | Classification |
|---|---|
| $\Delta<0$ | Ellipse |
| $\Delta=0$ | Parabola |
| $\Delta>0$ | Hyperbola |

Each scalar is represented by a point on an oriented reference line. The final decision is a point-equality or line-order test.

## Full-domain guarantee

A line meets a nondegenerate conic in at most two distinct points, so the first three selected points always form a frame. Five points with no three collinear impose five independent conditions on quadratic polynomials, giving a unique conic equation up to nonzero scale. Consequently, the two rows above are independent and their cross product never vanishes.

Changing the affine frame multiplies the discriminant by a strictly positive square factor. The sign therefore gives the same classification for every legal point selection. The complete proof covers arbitrary real coordinates. Step minimization is deferred.

## Exact verification

SageMath 10.7 verifies 18 symbolic identities and interpolation witnesses, 16 exact fixtures, all 1,920 point permutations, 95 signed-arithmetic checks, zero-divisor rejection, and five invalid-input controls. Independent paths recover the full conic through a 5-by-6 nullspace calculation and replay the geometric line-intersection macros.

All mathematical decisions use rational numbers, symbolic polynomials, and the exact real algebraic field `AA`. Tiny-arc fixtures use parameter spacing $10^{-12}$. Near-parabolic fixtures use parameters $\pm10^{-30}$. The general coverage guarantee is established in the proof.

Run from the repository root on macOS/Linux.

```sh
docker run --rm --network none \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -v "$PWD:/workspace:ro" -w /workspace \
  sagemath/sagemath@sha256:4f5589eb6c565949a006f8665de2876b8414410daf5ac554f4434a15d4f3d528 \
  sage -python experiments/verify.py
```

The expected exit status is zero and `valid` is `true`. Windows, regeneration and rendering commands are documented in [REPRODUCING](docs/REPRODUCING.md).

## Animation and sources

The 97.1-second Manim animation is rendered at 3840 × 2160 and 60 fps. It demonstrates point selection, the constructed affine frame, parallel projections, multiplication by similar triangles, and all three sign branches. It uses the preceding Euclid projects' dark-blue background and color roles. Geometry and decisions are exported after exact verification, and their hash is checked at render time.

The problem and the original parallel-chord and center-position ideas come from the user's `ai-math-notes` question. The original exchange is preserved with source attribution. The current method uses classical conic interpolation, constructible arithmetic and discriminant classification. Source discussion and corrections are documented in [LITERATURE](docs/LITERATURE.md), with the historical exchange in [sources](sources/README.md).

The four completed Euclid projects are methodological and presentation references. [Euclid-Min](https://github.com/lenovobenben/euclid-min) · [Euclid-CCC-Min](https://github.com/lenovobenben/euclid-ccc-min) · [Euclid-Equal-Angle-Min](https://github.com/lenovobenben/euclid-equal-angle-min) · [Euclid-Castillon-Min](https://github.com/lenovobenben/euclid-castillon-min)
