"""Twi106 — ShapeFix_Wire.FixIntersectingEdges accumulation cascade without upper bound.

Catalog claim: FixIntersectingEdges repairs wire self-intersections by splitting and
re-ordering edges. Multiple intersection points without upper-bound tolerance enforcement
cause accumulation cascade: each split generates additional vertices; re-insertion may
create new intersections at previously-clean edge pairs. A wire with 5+ edges in a
cascading zigzag pattern exhibits unbounded vertex accumulation or silent partial repair.

Mechanism IS a planar face whose outer wire has 5 edges in a cascading zigzag:
  P0=(0,0,0), P1=(8,4,0), P2=(2,4,0), P3=(6,0,0), P4=(4,6,0)

  E0: P0→P1 (diagonal up-right)      — crosses E2
  E1: P1→P2 (horizontal left)        — crosses E3
  E2: P2→P3 (diagonal down-right)    — crosses E0 and E4
  E3: P3→P4 (diagonal up)            — crosses E1
  E4: P4→P0 (diagonal down-left)     — crosses E2

Wire closes (P4→P0), but E0 crosses E2, E1 crosses E3, E2 crosses E4.
Each split generates new vertices; split of E0 creates a new vertex V_mid that
can create a new intersection with the already-split E2. FixIntersectingEdges
lacks an upper-bound tolerance cap, so the cascade continues until silent exit.

A second correct 10×10 square face at z=-1 provides n_faces_total == 2.

Tier-3 assertion:
  - n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi106",
    defect=(
        "Two ADVANCED_FACEs on PLANEs in a CLOSED_SHELL; "
        "face0: 5-edge cascading zigzag wire on PLANE at z=0; "
        "P0=(0,0,0), P1=(8,4,0), P2=(2,4,0), P3=(6,0,0), P4=(4,6,0); "
        "E0(P0→P1) crosses E2(P2→P3); E1(P1→P2) crosses E3(P3→P4); "
        "E2(P2→P3) also crosses E4(P4→P0); "
        "each FixIntersectingEdges split at intersection generates a new vertex; "
        "new vertex at mid-E0 creates additional intersection with post-split E2; "
        "no upper-bound tolerance cap — cascade continues; algorithm exits silently "
        "without bounding repair iterations — IS the mechanism; "
        "face1 is a correct 10x10 square at z=-1; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → "
        "ADVANCED_FACEs in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane 0: face with cascading zigzag wire ──────────────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f.plane(pl0_plc)

# Zigzag vertices: chosen so edges cascade-intersect
P0 = (0.0, 0.0, 0.0)
P1 = (8.0, 4.0, 0.0)
P2 = (2.0, 4.0, 0.0)
P3 = (6.0, 0.0, 0.0)
P4 = (4.0, 6.0, 0.0)

v_P0 = f.vertex_point(f.cartesian_point(P0))
v_P1 = f.vertex_point(f.cartesian_point(P1))
v_P2 = f.vertex_point(f.cartesian_point(P2))
v_P3 = f.vertex_point(f.cartesian_point(P3))
v_P4 = f.vertex_point(f.cartesian_point(P4))

def _make_line(src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    dz = dst[2] - src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag)
    )

# E0: P0(0,0,0) → P1(8,4,0) — diagonal up-right; crosses E2 at ~(4.25,2.12,0)
e0  = f.edge_curve(v_P0, v_P1, _make_line(P0, P1))
oe0 = f.oriented_edge(e0, True)

# E1: P1(8,4,0) → P2(2,4,0) — horizontal left; crosses E3
e1  = f.edge_curve(v_P1, v_P2, _make_line(P1, P2))
oe1 = f.oriented_edge(e1, True)

# E2: P2(2,4,0) → P3(6,0,0) — diagonal down-right; crosses E0 and E4
e2  = f.edge_curve(v_P2, v_P3, _make_line(P2, P3))
oe2 = f.oriented_edge(e2, True)

# E3: P3(6,0,0) → P4(4,6,0) — diagonal up; crosses E1
e3  = f.edge_curve(v_P3, v_P4, _make_line(P3, P4))
oe3 = f.oriented_edge(e3, True)

# E4: P4(4,6,0) → P0(0,0,0) — diagonal down-left; crosses E2
e4  = f.edge_curve(v_P4, v_P0, _make_line(P4, P0))
oe4 = f.oriented_edge(e4, True)

# 5-edge cascading zigzag loop: E0 crosses E2; E1 crosses E3; E2 crosses E4
# — FixIntersectingEdges accumulation cascade IS the mechanism
loop0 = f.edge_loop([oe0, oe1, oe2, oe3, oe4])
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi106.stp")
