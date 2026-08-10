"""Twi310 — Cartesian point with an empty coordinate list.

Catalog claim: a corner point of an otherwise-correct square wire is
written as `CARTESIAN_POINT('corner_no_coords',())` — the coordinate list
empty where ISO 10303-42 requires one to three reals. A point with no
coordinates is never valid in any context. The point is consumed twice —
as the corner vertex's geometry and as the bottom edge's line origin — so
the defect is wired into the wire through both paths.

Canonical claimant for the cartesian-point row of the nonempty-aggregate
table (structural-linter v4); the direction spelling of the same defect has
its own claimant elsewhere.

Byte assertions:
  - contains(b"CARTESIAN_POINT('corner_no_coords',())")
  - count_entity_def(b'CARTESIAN_POINT') >= 4

Structural assertion: struct == EMPTY_AGGREGATE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi310",
    defect=(
        "the origin corner written as CARTESIAN_POINT('corner_no_coords',()) "
        "— empty coordinate list where the schema requires one to three "
        "reals; consumed both as the corner vertex's geometry and as the "
        "bottom edge's line origin, so the coordinate-less point is wired "
        "into the wire through two paths"
    ),
)

S = 10.0
# THE DEFECT: no coordinates at all.
p0 = f._emit_raw("CARTESIAN_POINT('corner_no_coords',())")
p1 = f.cartesian_point((S, 0.0, 0.0))
p2 = f.cartesian_point((S, S, 0.0))
p3 = f.cartesian_point((0.0, S, 0.0))
v0, v1, v2, v3 = (f.vertex_point(p) for p in (p0, p1, p2, p3))

dx = f.direction((1.0, 0.0, 0.0))
dy = f.direction((0.0, 1.0, 0.0))
dnx = f.direction((-1.0, 0.0, 0.0))
dny = f.direction((0.0, -1.0, 0.0))

e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(dx, S)))
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(dy, S)))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(dnx, S)))
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(dny, S)))

loop = f.edge_loop([f.oriented_edge(e, True) for e in (e0, e1, e2, e3)])
anchor = f.cartesian_point((0.0, 0.0, 0.0))
plane = f.plane(f.axis2_placement_3d(anchor, f.direction((0.0, 0.0, 1.0)), dx))
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="twi310_square")
sbsm = f.shell_based_surface_model([f.open_shell([face])])
f.add_product_chain(sbsm)
