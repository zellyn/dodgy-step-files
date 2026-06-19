"""Gs135 — Self-intersecting B-spline surface; Bezier conversion misses
self-intersection.

Catalog claim: B-spline surface with a twisted control net (interior row
with extreme Y oscillation) produces a surface that crosses itself in 3D;
Bezier conversion fails to detect the self-intersection.

Previous fixture had a malformed pole grid (flat list instead of nested,
knot/multiplicity in wrong arg slots) — the file wouldn't parse correctly.
Regen with clean nested form: degree 2×2, 3×3 grid with middle Y row at
±2.0 producing a saddle that self-intersects on extension.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs135",
             defect="B-spline surface with self-intersecting twisted control net")

# 3×3 control grid. Middle V-row oscillates wildly in Z; outer rows are flat.
# This shape, when extended past the trim, folds back on itself.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0)],
    [(0.0, 1.0, 3.0), (1.0, 1.0, -3.0), (2.0, 1.0, 3.0)],   # twisted: ±3 Z
    [(0.0, 2.0, 0.0), (1.0, 2.0, 0.0), (2.0, 2.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('twisted_self_intersect',2,2,"
    f"({grid}),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(3,3),(3,3),"
    "(0.0,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# Minimal face boundary.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((2.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 2.0)
ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
