"""Twi159 — ShapeAnalysis_Wire.CheckOrder wire-completely-reversed.

Catalog claim: 4-edge closed wire where all ORIENTED_EDGEs use .F. (reversed)
orientation. CheckOrder should detect that the entire wire is traversed in the
reverse direction and flag it as a fixable mode rather than failing silently.

Mechanism IS a planar ADVANCED_FACE whose outer EDGE_LOOP contains 4 line
edges forming a 10×10 square, but ALL four ORIENTED_EDGEs have orientation=.F.:
  - OE0: edge E0 (P0→P1 in 3D), oriented .F. → traversed P1→P0
  - OE1: edge E1 (P1→P2 in 3D), oriented .F. → traversed P2→P1
  - OE2: edge E2 (P2→P3 in 3D), oriented .F. → traversed P3→P2
  - OE3: edge E3 (P3→P0 in 3D), oriented .F. → traversed P0→P3

With all four orientations reversed, the wire logically traverses
P0→P3→P2→P1→P0 (clockwise as seen from +Z), which is geometrically valid but
in the "wrong" winding for an outer-bound face. CheckOrder detects whether
adjacent oriented-edge endpoints match: OE0 end (P0) must equal OE1 start (P2)
— they don't, so CheckOrder fires. Whether it correctly identifies this as
a global reversal (fixable) vs random disorder is the checked behaviour.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi159",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 4 LINE edges forming a 10x10 square; "
        "ALL four ORIENTED_EDGEs have orientation=.F. (reversed) IS the defect; "
        "wire logically traverses counter-clockwise square in clockwise order; "
        "edges: E0 (0,0,0)→(10,0,0), E1 (10,0,0)→(10,10,0), "
        "E2 (10,10,0)→(0,10,0), E3 (0,10,0)→(0,0,0) in 3D; "
        "all oriented .F. so traversal is P1→P0, P2→P1, P3→P2, P0→P3; "
        "CheckOrder adjacency check fires; "
        "complete-reversal fixable mode IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND → ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices: 10×10 square ────────────────────────────────────────────────────
P0 = (0.0,  0.0,  0.0)   # bottom-left
P1 = (10.0, 0.0,  0.0)   # bottom-right
P2 = (10.0, 10.0, 0.0)   # top-right
P3 = (0.0,  10.0, 0.0)   # top-left

v_P0 = f.vertex_point(f.cartesian_point(P0))
v_P1 = f.vertex_point(f.cartesian_point(P1))
v_P2 = f.vertex_point(f.cartesian_point(P2))
v_P3 = f.vertex_point(f.cartesian_point(P3))

# ── Edges (3D curve goes in the natural direction P_i → P_{i+1}) ─────────────
# E0: P0 → P1 (+X direction)
e0_line = f.line(f.cartesian_point(P0), f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e0 = f.edge_curve(v_P0, v_P1, e0_line, True)

# E1: P1 → P2 (+Y direction)
e1_line = f.line(f.cartesian_point(P1), f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e1 = f.edge_curve(v_P1, v_P2, e1_line, True)

# E2: P2 → P3 (-X direction)
e2_line = f.line(f.cartesian_point(P2), f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
e2 = f.edge_curve(v_P2, v_P3, e2_line, True)

# E3: P3 → P0 (-Y direction)
e3_line = f.line(f.cartesian_point(P3), f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
e3 = f.edge_curve(v_P3, v_P0, e3_line, True)

# ── ALL ORIENTED_EDGEs use orientation=False — IS the defect ─────────────────
# With .F., traversal of E0 goes P1→P0, E1 goes P2→P1, E2 goes P3→P2, E3→P0→P3
# The wire sequence OE0,OE1,OE2,OE3 is therefore: P1→P0, P2→P1, P3→P2, P0→P3
# This is a complete reversal (clockwise instead of CCW), but the loop is not
# connected in order (P0 ≠ P2), which CheckOrder flags.
oe0 = f.oriented_edge(e0, False)   # .F. — DEFECT
oe1 = f.oriented_edge(e1, False)   # .F. — DEFECT
oe2 = f.oriented_edge(e2, False)   # .F. — DEFECT
oe3 = f.oriented_edge(e3, False)   # .F. — DEFECT

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([oe0, oe1, oe2, oe3])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi159.stp")
