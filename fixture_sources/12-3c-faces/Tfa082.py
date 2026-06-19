"""Tfa082 — CheckPin pin singularity along V parametric axis.

Catalog claim: face with sharp pin singularity along the V parametric axis;
ShapeAnalysis_CheckSmallFace::CheckPin assumes pins align with U, missing
axis-agnostic detection.

Previous fixture used B_SPLINE_SURFACE (no _WITH_KNOTS) with marginal Z
delta (0.001). Regen with proper B_SPLINE_SURFACE_WITH_KNOTS where the
V=0 row of poles is all coincident — true pin singularity at v=0.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa082",
             defect="V-axis pin: V=0 row collapsed to single point")

# 3 U × 3 V control grid. V=0 row: all three poles at (0,0,0) → true pin.
# V=1 row: spread along Z to give the surface volume.
# V=2 row: spread along X+Z.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)],   # V=0 row: pin
    [(1.0, 1.0, 0.5), (2.0, 1.0, 1.0), (3.0, 1.0, 0.5)],
    [(2.0, 2.0, 0.0), (3.0, 2.0, 0.5), (4.0, 2.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('v_axis_pin',2,2,"
    f"({grid}),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(3,3),(3,3),"
    "(0.0,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# Minimal face boundary.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((4.0, 2.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
import math
dx, dy = 4.0, 2.0
mag = math.hypot(dx, dy)
d = f.direction((dx / mag, dy / mag, 0.0))
vec = f.vector(d, mag)
ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
