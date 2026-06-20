"""Twi103 — ShapeFix_Wire.FixSelfIntersectingEdge 30-iteration convergence silently exits.

Catalog claim: FixSelfIntersectingEdge implements a hard 30-iteration limit for
self-intersection repair convergence. Persistent intersections after 30 iterations
cause silent exit without reporting failure status or incomplete repair. Pathological
wire geometry with unresolvable self-intersections (e.g., topologically required
crossing) fails without diagnostic.

Mechanism IS a planar face whose outer EDGE_LOOP has 4 edges forming an S-curve
(figure-eight / crossing) path that self-intersects. The edges form two crossing
pairs: E0↔E2 cross each other, E1↔E3 cross each other. Each repair iteration
shifts vertices without resolving the underlying topology; after 30 iterations the
algorithm exits silently.

Wire layout (crossing S-shape in XY plane):
  P0=(0,0,0), P1=(10,10,0), P2=(0,10,0), P3=(10,0,0)
  E0: P0→P1  (diagonal bottom-left to top-right)
  E1: P1→P2  (top-right to top-left)
  E2: P2→P3  (top-left to bottom-right — crosses E0)
  E3: P3→P0  (bottom-right to bottom-left)
The wire is closed (P3→P0), but E0 and E2 are crossing diagonals, encoding the
topologically required self-intersection.

A second correct 10×10 square face at z=-1 provides n_faces_total == 2.

Tier-3 assertion:
  - n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi103",
    defect=(
        "Two ADVANCED_FACEs on PLANEs in a CLOSED_SHELL; "
        "face0: 4-edge S-curve (figure-eight crossing) wire on a PLANE at z=0; "
        "P0=(0,0,0), P1=(10,10,0), P2=(0,10,0), P3=(10,0,0); "
        "E0(P0→P1) and E2(P2→P3) are crossing diagonals — self-intersecting pair; "
        "E1(P1→P2) and E3(P3→P0) connect the crossing loop; "
        "wire closes (P0 start = P0 end via E3) but topology is a figure-eight; "
        "ShapeFix_Wire.FixSelfIntersectingEdge hits 30-iteration hard limit and "
        "exits silently without reporting convergence failure — IS the mechanism; "
        "face1 is a correct 10x10 square at z=-1; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → "
        "ADVANCED_FACEs in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane 0: face with self-intersecting S-curve wire ────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f.plane(pl0_plc)

# Vertices: 4 corners forming an S-curve crossing pattern
v_P0 = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # bottom-left
v_P1 = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # top-right
v_P2 = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))   # top-left
v_P3 = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # bottom-right

import math as _math

# E0: P0(0,0,0) → P1(10,10,0)  — diagonal bottom-left to top-right
_d0 = _math.hypot(10.0, 10.0)
e0_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                 f.vector(f.direction((10.0 / _d0, 10.0 / _d0, 0.0)), _d0))
e0  = f.edge_curve(v_P0, v_P1, e0_line)
oe0 = f.oriented_edge(e0, True)

# E1: P1(10,10,0) → P2(0,10,0)  — top right to top left
e1_line = f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                 f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
e1  = f.edge_curve(v_P1, v_P2, e1_line)
oe1 = f.oriented_edge(e1, True)

# E2: P2(0,10,0) → P3(10,0,0)  — diagonal top-left to bottom-right (crosses E0!)
_d2 = _math.hypot(10.0, 10.0)
e2_line = f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                 f.vector(f.direction((10.0 / _d2, -10.0 / _d2, 0.0)), _d2))
e2  = f.edge_curve(v_P2, v_P3, e2_line)
oe2 = f.oriented_edge(e2, True)

# E3: P3(10,0,0) → P0(0,0,0)  — bottom right to bottom left
e3_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                 f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
e3  = f.edge_curve(v_P3, v_P0, e3_line)
oe3 = f.oriented_edge(e3, True)

# 4-edge crossing loop: wire closes (P0 start = P0 end) but is a figure-eight
# E0 and E2 cross at the center (5,5,0) — self-intersection IS mechanism
loop0 = f.edge_loop([oe0, oe1, oe2, oe3])
fob0  = f.face_outer_bound(loop0)
face0 = f.advanced_face([fob0], plane0)

# ── Plane 1: correct 10x10 square at z=-1 ─────────────────────────────────────
pl1_orig = f.cartesian_point((0.0, 0.0, -1.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
pl1_plc  = f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir)
plane1   = f.plane(pl1_plc)

v_bl1 = f.vertex_point(f.cartesian_point((0.0,  0.0,  -1.0)))
v_br1 = f.vertex_point(f.cartesian_point((10.0, 0.0,  -1.0)))
v_tr1 = f.vertex_point(f.cartesian_point((10.0, 10.0, -1.0)))
v_tl1 = f.vertex_point(f.cartesian_point((0.0,  10.0, -1.0)))

eb1 = f.edge_curve(v_bl1, v_br1,
                   f.line(f.cartesian_point((0.0, 0.0, -1.0)),
                          f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
er1 = f.edge_curve(v_br1, v_tr1,
                   f.line(f.cartesian_point((10.0, 0.0, -1.0)),
                          f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
et1 = f.edge_curve(v_tr1, v_tl1,
                   f.line(f.cartesian_point((10.0, 10.0, -1.0)),
                          f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
el1 = f.edge_curve(v_tl1, v_bl1,
                   f.line(f.cartesian_point((0.0, 10.0, -1.0)),
                          f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))

oeb1 = f.oriented_edge(eb1, True)
oer1 = f.oriented_edge(er1, True)
oet1 = f.oriented_edge(et1, True)
oel1 = f.oriented_edge(el1, True)

loop1 = f.edge_loop([oeb1, oer1, oet1, oel1])
fob1  = f.face_outer_bound(loop1)
face1 = f.advanced_face([fob1], plane1)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi103.stp")
