"""Gn180 — B-spline surface with an empty control-points list.

Catalog claim: a face's surface is written as a degree-1x1 B-spline
surface whose control_points_list is `()` — no control net at all, where
ISO 10303-42 requires a two-dimensional list with at least (degree+1)
rows and columns. The surface spelling of the corpus's long-standing
empty-control-points CURVE fixture: the knot vectors and multiplicities
are present and self-consistent for a 2x2 net, so every argument EXCEPT
the net reads plausibly.

Canonical claimant for the B-spline-surface row of the nonempty-aggregate
table (structural-linter v4).

Geometry: a square boundary (four line edges at z=0) bound to the
empty-net surface; the boundary chain is complete and correct.

Byte assertions:
  - contains(b"B_SPLINE_SURFACE_WITH_KNOTS('empty_net'")
  - matches(rb"B_SPLINE_SURFACE_WITH_KNOTS\\('empty_net',1,1,\\(\\)")

Structural assertion: struct == EMPTY_AGGREGATE
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn180",
    defect=(
        "ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS('empty_net',1,1,(),...) "
        "— the control-points list empty where the schema requires at least "
        "a 2x2 net; knot vectors and multiplicities are present and "
        "self-consistent, so only the net is missing. The square boundary "
        "chain below the face is complete and correct"
    ),
)

S = 10.0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
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

# THE DEFECT: empty control net; all other arguments self-consistent.
surf = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('empty_net',1,1,(),.UNSPECIFIED.,.F.,.F.,.F.,"
    "(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)
face = f.advanced_face([f.face_outer_bound(loop)], surf, name="gn180_face")
sbsm = f.shell_based_surface_model([f.open_shell([face])])
f.add_product_chain(sbsm)
