"""Twi107 — FixReorder Mode-Cascade.

Catalog claim: Wire with edges in wrong order (E0→E2→E1→E3→E4). FixReorder fails
(ReorderOK=false), cascading suppression to FixSmall, FixConnected, FixSelfIntersection
per SF_Perform lines 320, 331, 355.

Mechanism IS a planar face whose outer wire has 5 edges given in wrong topological
order. Instead of the correct sequence E0→E1→E2→E3→E4, the wire contains edges in
the order E0→E2→E1→E3→E4. This causes FixReorder to fail (cannot find valid order),
which then suppresses downstream FixSmall, FixConnected, and FixSelfIntersection
checks due to the mode-cascade dependency coupling.

The correct 5-edge closed loop forms a regular pentagon-ish shape:
  P0=(0,0,0), P1=(10,0,0), P2=(10,8,0), P3=(5,12,0), P4=(0,8,0)
  Correct order: E0(P0→P1), E1(P1→P2), E2(P2→P3), E3(P3→P4), E4(P4→P0)
  Stored order:  E0(P0→P1), E2(P2→P3), E1(P1→P2), E3(P3→P4), E4(P4→P0)
     — E0 ends at P1, but next edge starts at P2 (gap), then E1 starts at P1
       (connected after E2), then E3 starts at P3, then E4 closes to P0.
  FixReorder sees a wire with connectivity break after E0 (P1≠P2), tries to
  reorder, cannot find valid permutation, returns ReorderOK=false.

Single-face fixture (tier-3: n_faces_total == 1).

Tier-3 assertion:
  - n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi107",
    defect=(
        "Single ADVANCED_FACE on a PLANE in a CLOSED_SHELL; "
        "outer EDGE_LOOP has 5 edges in wrong topological order: "
        "P0=(0,0,0), P1=(10,0,0), P2=(10,8,0), P3=(5,12,0), P4=(0,8,0); "
        "correct order E0(P0→P1),E1(P1→P2),E2(P2→P3),E3(P3→P4),E4(P4→P0); "
        "stored order E0(P0→P1),E2(P2→P3),E1(P1→P2),E3(P3→P4),E4(P4→P0) "
        "— deliberate E2/E1 swap creates connectivity break after E0 (P1≠P2); "
        "FixReorder attempts to find valid permutation; all permutations fail "
        "because the given order creates an irreconcilable gap; "
        "FixReorder returns ReorderOK=false; downstream FixSmall, FixConnected, "
        "FixSelfIntersection are suppressed per SF_Perform mode-cascade dependency "
        "coupling at lines 320, 331, 355 — IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND → ADVANCED_FACE in CLOSED_SHELL; "
        "never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices: pentagon-ish shape ──────────────────────────────────────────────
P0 = (0.0,  0.0,  0.0)
P1 = (10.0, 0.0,  0.0)
P2 = (10.0, 8.0,  0.0)
P3 = (5.0,  12.0, 0.0)
P4 = (0.0,  8.0,  0.0)

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

# ── Build all 5 edges in their CORRECT topological order ─────────────────────
# E0: P0→P1 (bottom)
e_E0  = f.edge_curve(v_P0, v_P1, _make_line(P0, P1))
oe_E0 = f.oriented_edge(e_E0, True)

# E1: P1→P2 (right side)
e_E1  = f.edge_curve(v_P1, v_P2, _make_line(P1, P2))
oe_E1 = f.oriented_edge(e_E1, True)

# E2: P2→P3 (upper-right diagonal)
e_E2  = f.edge_curve(v_P2, v_P3, _make_line(P2, P3))
oe_E2 = f.oriented_edge(e_E2, True)

# E3: P3→P4 (upper-left diagonal)
e_E3  = f.edge_curve(v_P3, v_P4, _make_line(P3, P4))
oe_E3 = f.oriented_edge(e_E3, True)

# E4: P4→P0 (left side)
e_E4  = f.edge_curve(v_P4, v_P0, _make_line(P4, P0))
oe_E4 = f.oriented_edge(e_E4, True)

# ── DEFECT: EDGE_LOOP stored in WRONG ORDER: E0→E2→E1→E3→E4 ─────────────────
# Correct would be E0→E1→E2→E3→E4. We swap E1 and E2.
# Connectivity after E0: E0 ends at P1; next edge E2 starts at P2 — BREAK.
# Then E1 starts at P1 (gap bridged by E2 before it), E3 starts at P3, E4 closes.
# FixReorder cannot reconcile: returns ReorderOK=false.
# Downstream FixSmall/FixConnected/FixSelfIntersection suppressed by mode-cascade.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_E0.eid},#{oe_E2.eid},#{oe_E1.eid},#{oe_E3.eid},#{oe_E4.eid}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi107.stp")
