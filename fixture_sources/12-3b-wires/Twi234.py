"""Twi234 — ShapeFix_Wire.FixDegenerated zero-vertex.

Catalog claim: Wire containing a vertex at exactly the origin (0,0,0).
FixDegenerated's vertex-distance test uses absolute comparison and treats
the origin specially, failing to recognize degenerate edges incident to it.

Mechanism: A 4-edge EDGE_LOOP on a PLANE. Three edges form a normal triangle
shape. One vertex of the triangle is placed at exactly (0,0,0) — the origin.
Between that origin vertex and the next vertex (1e-6, 0, 0) there is a
sub-tolerance micro-edge (length ~1e-6). FixDegenerated detects near-zero-
length edges by computing endpoint distance; however, when one endpoint IS
the geometric origin (0,0,0), the absolute-value distance metric returns a
value in [0, 1e-6] which can be confused with uninitialized/zero by the
implementation's special-case check for the origin point. The degenerate
micro-edge incident to (0,0,0) goes undetected IS the mechanism.

Wire on PLANE (normal +Z):
  P0 = (0, 0, 0)          — origin vertex IS the defect point
  P0b = (1e-6, 0, 0)      — micro-offset from origin
  P1 = (10, 0, 0)
  P2 = (5, 8, 0)
  E0: micro-edge from P0 to P0b (length ~1e-6) — incident to origin IS defect
  E1: LINE from P0b to P1
  E2: LINE from P1 to P2
  E3: LINE from P2 back to P0 (closing)

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile
import math as _math

f = StepFile(
    catalog_id="Twi234",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; 4-edge EDGE_LOOP; "
        "vertex V0 is at exactly (0,0,0) — the geometric origin IS the defect; "
        "E0 is a micro-edge of length ~1e-6 from (0,0,0) to (1e-6,0,0) — "
        "sub-tolerance degenerate edge incident to origin vertex; "
        "FixDegenerated absolute-comparison vertex-distance test fails at "
        "origin (0,0,0) — fails to detect the degenerate edge IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# -- PLANE: normal +Z ---------------------------------------------------------
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# -- Vertices -----------------------------------------------------------------
P0  = (0.0,    0.0, 0.0)   # exactly the origin — IS the defect
P0b = (1e-6,   0.0, 0.0)   # micro-offset from origin (sub-tolerance)
P1  = (10.0,   0.0, 0.0)
P2  = (5.0,    8.0, 0.0)

v0  = f.vertex_point(f.cartesian_point(P0))
v0b = f.vertex_point(f.cartesian_point(P0b))
v1  = f.vertex_point(f.cartesian_point(P1))
v2  = f.vertex_point(f.cartesian_point(P2))

# -- E0: micro-edge P0 -> P0b (length = 1e-6, incident to origin) ------------
# Degenerate sub-tolerance edge — FixDegenerated fails to catch it at origin
ln_e0 = f.line(
    f.cartesian_point(P0),
    f.vector(f.direction((1.0, 0.0, 0.0)), 1e-6),
)
e0 = f.edge_curve(v0, v0b, ln_e0)

# -- E1: P0b -> P1, LINE ------------------------------------------------------
dx1 = P1[0] - P0b[0]
ln_e1 = f.line(
    f.cartesian_point(P0b),
    f.vector(f.direction((1.0, 0.0, 0.0)), dx1),
)
e1 = f.edge_curve(v0b, v1, ln_e1)

# -- E2: P1 -> P2, LINE -------------------------------------------------------
dx2 = P2[0] - P1[0]
dy2 = P2[1] - P1[1]
mag2 = _math.sqrt(dx2*dx2 + dy2*dy2)
ln_e2 = f.line(
    f.cartesian_point(P1),
    f.vector(f.direction((dx2/mag2, dy2/mag2, 0.0)), mag2),
)
e2 = f.edge_curve(v1, v2, ln_e2)

# -- E3: P2 -> P0, closing LINE -----------------------------------------------
dx3 = P0[0] - P2[0]
dy3 = P0[1] - P2[1]
mag3 = _math.sqrt(dx3*dx3 + dy3*dy3)
ln_e3 = f.line(
    f.cartesian_point(P2),
    f.vector(f.direction((dx3/mag3, dy3/mag3, 0.0)), mag3),
)
e3 = f.edge_curve(v2, v0, ln_e3)

# -- EDGE_LOOP ----------------------------------------------------------------
loop  = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi234.stp")
