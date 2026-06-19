"""Gs072 — RECTANGULAR_TRIMMED_SURFACE with epsilon parameter window.

Catalog claim: trim domain spans (u=1e-10 to u=1e-9, v=1e-10 to v=1e-9);
Newton iteration parameters underflow because the trim window is sub-eps.

Previous fixture had a structurally malformed B_SPLINE_SURFACE_WITH_KNOTS
(extra orientation flags, missing pole grid). Regen with a clean planar
B-spline surface under a RECTANGULAR_TRIMMED_SURFACE with epsilon bounds.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs072",
             defect="rectangular_trimmed_surface with epsilon parameter window")

# Underlying degree-2 × degree-2 planar B-spline surface (3×3 grid).
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (1.0, 2.0, 0.0)],
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0), (2.0, 2.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('planar_carrier',2,2,"
    f"({grid}),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(3,3),(3,3),"
    "(0.0,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# Rectangular-trimmed surface with epsilon-scale parameter window.
trimmed = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('epsilon_window',#{surf.eid},"
    "1.0E-10,1.0E-9,1.0E-10,1.0E-9,.T.,.T.)"
)

# Minimal face boundary so the fixture is consumable.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], trimmed)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
