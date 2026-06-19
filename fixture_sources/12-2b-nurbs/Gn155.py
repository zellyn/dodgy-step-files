"""Gn155 — Interior B-spline knot multiplicity equals degree (C1 discontinuity).

Catalog claim: B-spline surface with U-degree 3, U-knots (4, 3, 1) at
(0, 0.5, 1) — interior knot multiplicity = degree creates C1 but not C2
continuity (discontinuous second derivative). Healer must detect and
flag, or apply knot removal to restore C2.

Previous fixture had a self-contradicting comment block — same numbers
but conflicting prose. Regen via builder for crisp encoding.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn155",
             defect="C1 break at interior U-knot (multiplicity = degree)")

# 4 U × 3 V control grid. Lift Z at U=1, U=2 to make the surface non-planar
# so the C1/C2 distinction is observable.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.5), (1.0, 1.0, 1.0), (1.0, 2.0, 0.5)],
    [(2.0, 0.0, 0.5), (2.0, 1.0, 1.0), (2.0, 2.0, 0.5)],
    [(3.0, 0.0, 0.0), (3.0, 1.0, 0.0), (3.0, 2.0, 0.0)],
]]

# Use _emit_raw for non-rational B_SPLINE_SURFACE_WITH_KNOTS.
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('c1_break',3,2,"
    f"({grid}),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(4,3,1),(3,3),"        # U multiplicities (4,3,1) → interior u=0.5 has mult=3=degree
    "(0.0,0.5,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# Minimal face boundary.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((3.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 3.0)
ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
