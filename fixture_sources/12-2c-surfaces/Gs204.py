"""Gs204 — Surface closed in U only to within 1e-4 (poles do not coincide, so
the surface itself reports "not closed"), carrying two unshared seam-line
edges on one face: the seam merge is approved only via the isoparametric
closure fallback (`sew-seam-closed-surface-merge`, subvariant "closure
detected via isoline-distance fallback rather than the surface's own
IsUClosed/IsVClosed flag").

Catalog claim (occt-coverage PARTIAL `sew-seam-closed-surface-merge`):
Tsh209 covers the U-periodic case and Gs200 the V-periodic case, both on
surfaces that self-report closed. The third subvariant needs a surface whose
own closure flag is FALSE while it is nevertheless effectively closed, so
that the seam-merge gate has to fall back on comparing isoparametric-curve
endpoints against midpoints (`BRepBuilderAPI_Sewing::IsUClosedSurface` /
`IsVClosedSurface`, `BRepBuilderAPI_Sewing.cxx:239-289`, whose `else` branch
calls the static `IsClosedByIsos`, `:162-233`, when `IsUClosed()`/
`IsVClosed()` come back false).

Construction: a `B_SPLINE_SURFACE_WITH_KNOTS`, degree 1 x 1, shaped as a
12-sided prism of radius 1 and height 2 — 13 pole columns wrapping the full
360 degrees, where the LAST column is the first column displaced radially by
1e-4 instead of being identical to it. `Geom_BSplineSurface::IsUClosed()`
(`Geom_BSplineSurface_1.cxx:1216`) compares the two boundary U-isocurves with
`Precision::Confusion()` (1e-7), so a 1e-4 pole gap makes it report NOT
closed, while the surface is geometrically closed for every practical
purpose. The face is a Tsh209-style seam loop: bottom polyline, the seam line
at u=umax reversed, top polyline reversed, the seam line at u=umin reversed —
two DISTINCT, unshared, 1e-4-apart vertical edges on ONE face.

Live verification (this worktree's OCP/OCCT 7.8.1, fed the shape read from
THESE bytes):
  * default read -> shape_null=False, 1 face, 4 edges, surface is a
    `Geom_BSplineSurface` with IsUClosed=False, IsVClosed=False,
    IsUPeriodic=False, IsVPeriodic=False (asserted live, not assumed), and
    all four edges carry pcurves;
  * `BRepBuilderAPI_Sewing(1e-2)`.Perform() MERGES the two seam-line edges:
    NbContigousEdges()==1, NbMultipleEdges()==0, 4 unique edges -> 3.
    Both edges belong to the SAME face, so that merge is gated by
    `IsMergedClosed` (`BRepBuilderAPI_Sewing.cxx:1688-1689`, reached because
    `Faces1.Contains(Face2)`), whose first act is
    `if (!isUClosed && !isVClosed) return Standard_False` (`:1257`) with both
    flags coming from IsUClosedSurface/IsVClosedSurface. Since the surface
    itself reports neither U- nor V-closed, the merge can only have been
    approved through the isoline-distance fallback.
  * controls on the same generator: gap 1e-4 -> 0 (poles exactly coincident)
    makes OCCT hand back a U-PERIODIC surface (IsUClosed=True), i.e. the
    fallback is no longer needed — which is exactly why the gap has to be
    there; wrap 360 -> 180 degrees (a genuinely open patch, seam lines 2 apart)
    gives NbContigousEdges()==0, no merge.

Byte assertions:
  - count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 1
  - count_entity_def(b'ADVANCED_FACE') == 1
"""
import math

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs204",
    schema="AP242",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree 1x1, 12-sided prism, r=1, h=2) "
        "wrapping the full 360 degrees but whose LAST pole column is the "
        "first column displaced radially by 1e-4 instead of identical to it "
        "-- 1000x the 1e-7 pole-comparison tolerance, so the surface reports "
        "NOT closed in U while being geometrically closed. One ADVANCED_FACE "
        "on it carries two distinct, unshared, 1e-4-apart vertical seam-line "
        "edges (u=umin and u=umax), a same-face seam-merge candidate pair "
        "whose approval depends entirely on detecting the surface's closure "
        "without a closure flag to read"
    ),
)

R, H, N, GAP = 1.0, 2.0, 12, 1.0e-4


def cp(p):
    return f.cartesian_point(tuple(float(c) for c in p))


def dir3(t):
    n = sum(c * c for c in t) ** 0.5
    return f.direction(tuple(float(c) / n for c in t))


def seg(va, vb, pa, pb):
    d = [pb[i] - pa[i] for i in range(3)]
    L = sum(c * c for c in d) ** 0.5
    return f.edge_curve(va, vb, f.line(cp(pa), f.vector(dir3(d), L)))


# Pole ring: N+1 columns, the last one displaced radially by GAP.
nu = N + 1
ring = []
for i in range(nu):
    t = 2.0 * math.pi * i / N
    rad = R + (GAP if i == N else 0.0)
    ring.append((rad * math.cos(t), rad * math.sin(t)))

grid = [[cp([x, y, 0.0]), cp([x, y, H])] for (x, y) in ring]
u_mult = [2] + [1] * (nu - 2) + [2]
u_knots = [float(i) for i in range(nu)]
surf = f.b_spline_surface_with_knots(
    1, 1, grid, u_mult, [2, 2], u_knots, [0.0, 1.0],
    u_closed=True, v_closed=False)

p_first_b = (ring[0][0], ring[0][1], 0.0)
p_first_t = (ring[0][0], ring[0][1], H)
p_last_b = (ring[-1][0], ring[-1][1], 0.0)
p_last_t = (ring[-1][0], ring[-1][1], H)
v_fb = f.vertex_point(cp(p_first_b))
v_ft = f.vertex_point(cp(p_first_t))
v_lb = f.vertex_point(cp(p_last_b))
v_lt = f.vertex_point(cp(p_last_t))

c_mult = [2] + [1] * (nu - 2) + [2]
c_knots = [float(i) for i in range(nu)]
c_bot = f.b_spline_curve_with_knots(
    1, [cp([x, y, 0.0]) for (x, y) in ring], c_mult, c_knots)
c_top = f.b_spline_curve_with_knots(
    1, [cp([x, y, H]) for (x, y) in ring], c_mult, c_knots)
e_bot = f.edge_curve(v_fb, v_lb, c_bot)
e_top = f.edge_curve(v_ft, v_lt, c_top)
e_seam_umin = seg(v_fb, v_ft, p_first_b, p_first_t)
e_seam_umax = seg(v_lt, v_lb, p_last_t, p_last_b)

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_seam_umax, False),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_seam_umin, False),
])
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], surf,
                       same_sense=True)
shell = f.open_shell([face], name="gs204_isoline_closure_fallback_shell")
f.add_product_chain(f.shell_based_surface_model([shell]))
