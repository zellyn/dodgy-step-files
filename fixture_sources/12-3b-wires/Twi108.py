"""Twi108 — FixGaps3d 3D-Gap Repair.

Catalog claim: Wire with adjacent edges missing exactly (gap ~0.05 unit in Z
between P1 and P2 vertices). Vertex-tolerance ball overlap but distance exceeds
Confusion threshold.

Pattern: 4-edge planar loop with deliberate Z-offset at P2 to force FixGaps3d
bridge repair.

Coverage: ShapeFix_Wire.FixGaps3d edge vertex connection tolerance handling.

Mechanism IS a planar ADVANCED_FACE whose outer 4-edge EDGE_LOOP has a vertex
coordinate inconsistency: E0 ends at v_P1=(10,0,0) but E1 starts from v_P1b
=(10,0,0.05) — a 0.05-unit Z-gap. The gap exceeds the Confusion threshold
(1e-7) but vertex tolerance balls overlap (tolerance ~0.1 on each vertex).
FixGaps3d detects the gap and bridges it. The shape is healable to shape(1).

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi108",
    defect=(
        "Single ADVANCED_FACE on a PLANE in a CLOSED_SHELL; "
        "outer EDGE_LOOP has 4 edges; E0 ends at v_P1=(10,0,0), "
        "E1 starts at v_P1b=(10,0,0.05) — a deliberate 0.05-unit 3D gap in Z; "
        "vertex tolerance balls overlap (tolerance ~0.1) but gap exceeds Confusion; "
        "FixGaps3d detects the gap and bridges it with a new pcurve segment; "
        "P0=(0,0,0), P1=(10,0,0), P1b=(10,0,0.05), P2=(10,10,0), P3=(0,10,0); "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in CLOSED_SHELL; "
        "never orphaned — FixGaps3d edge vertex connection tolerance IS mechanism"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices: rectangular loop with Z-gap at P1/P1b ──────────────────────────
P0  = (0.0,  0.0,  0.0)
P1  = (10.0, 0.0,  0.0)    # E0 endpoint
P1b = (10.0, 0.0,  0.05)   # E1 startpoint — 0.05 Z-gap from P1 (IS defect)
P2  = (10.0, 10.0, 0.0)
P3  = (0.0,  10.0, 0.0)

v_P0  = f.vertex_point(f.cartesian_point(P0))
v_P1  = f.vertex_point(f.cartesian_point(P1))
v_P1b = f.vertex_point(f.cartesian_point(P1b))
v_P2  = f.vertex_point(f.cartesian_point(P2))
v_P3  = f.vertex_point(f.cartesian_point(P3))


def _line(src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    dz = dst[2] - src[2]
    mag = _math.sqrt(dx * dx + dy * dy + dz * dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx / mag, dy / mag, dz / mag)), mag),
    )


# E0: P0 → P1 (bottom)  — ends at v_P1=(10,0,0)
e_E0  = f.edge_curve(v_P0, v_P1,  _line(P0, P1))
oe_E0 = f.oriented_edge(e_E0, True)

# E1: P1b → P2 (right side) — starts at v_P1b=(10,0,0.05)  ← 0.05-unit Z-gap!
e_E1  = f.edge_curve(v_P1b, v_P2, _line(P1b, P2))
oe_E1 = f.oriented_edge(e_E1, True)

# E2: P2 → P3 (top)
e_E2  = f.edge_curve(v_P2, v_P3,  _line(P2, P3))
oe_E2 = f.oriented_edge(e_E2, True)

# E3: P3 → P0 (left side, closes loop)
e_E3  = f.edge_curve(v_P3, v_P0,  _line(P3, P0))
oe_E3 = f.oriented_edge(e_E3, True)

# ── EDGE_LOOP: gap between E0 endpoint (P1) and E1 start (P1b) ────────────────
loop = f.edge_loop([oe_E0, oe_E1, oe_E2, oe_E3])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi108.stp")
