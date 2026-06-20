"""Twi160 — ShapeFix_Wire.FixLacking degenerate-vertex-gap.

Catalog claim: Wire missing an edge between v1 and v2 where dist(v1,v2) < Confusion
(effectively coincident). FixLacking inserts a degenerate edge but the
construction has wrong direction.

Mechanism IS a planar ADVANCED_FACE whose outer EDGE_LOOP has 3 edges forming a
triangle, but with a near-coincident vertex pair (V2 at (10,0,0) and V2' at
(10,0,5e-8)):
  - E0: LINE V0=(0,0,0) → V1=(10,0,0)   — bottom
  - E1: LINE V1=(10,0,0) → V3=(5,10,0)  — right side
  - E2: LINE V3=(5,10,0) → V2'=(10,0,5e-8) — returns near V1 but not exactly

E2 ends at V2'=(10,0,5e-8) which is 5e-8 from V1=(10,0,0) — well within
OCCT's Confusion tolerance (~1e-7). The wire is "almost closed" but has a
micro-gap. FixLacking inserts a degenerate spanning edge at V2'→V1 (or V1→V2'),
but the direction of the degenerate edge is wrong because the healer picks
the wrong endpoint order when the gap is below Confusion.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi160",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 3 LINE edges forming near-closed triangle; "
        "V1=(10,0,0) and V2'=(10,0,5e-8) are 5e-8 apart — below Confusion; "
        "E0 LINE (0,0,0)→(10,0,0), "
        "E1 LINE (10,0,0)→(5,10,0), "
        "E2 LINE (5,10,0)→(10,0,5e-8) — ends at near-coincident V2'; "
        "micro-gap of 5e-8 between V2' and V1 IS the defect; "
        "FixLacking inserts degenerate edge but wrong direction; "
        "dist(V1,V2') < Confusion IS the mechanism; "
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

# ── Vertices ──────────────────────────────────────────────────────────────────
P0  = (0.0,  0.0,    0.0)
P1  = (10.0, 0.0,    0.0)    # wire start/end (correct)
P3  = (5.0,  10.0,   0.0)    # apex
P2p = (10.0, 0.0,    5.0e-8) # near-coincident with P1 — IS the defect

v_P0  = f.vertex_point(f.cartesian_point(P0))
v_P1  = f.vertex_point(f.cartesian_point(P1))
v_P3  = f.vertex_point(f.cartesian_point(P3))
v_P2p = f.vertex_point(f.cartesian_point(P2p))   # near-coincident end


def _line_edge(v_src, v_dst, src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    dz = dst[2] - src[2]
    mag = _math.sqrt(dx * dx + dy * dy + dz * dz)
    ln = f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx / mag, dy / mag, dz / mag)), mag),
    )
    return f.edge_curve(v_src, v_dst, ln, True)


# ── E0: (0,0,0) → (10,0,0) ───────────────────────────────────────────────────
e0  = _line_edge(v_P0, v_P1, P0, P1)
oe0 = f.oriented_edge(e0, True)

# ── E1: (10,0,0) → (5,10,0) ──────────────────────────────────────────────────
e1  = _line_edge(v_P1, v_P3, P1, P3)
oe1 = f.oriented_edge(e1, True)

# ── E2: (5,10,0) → (10,0,5e-8) — ends near V1 but not at it ─────────────────
e2  = _line_edge(v_P3, v_P2p, P3, P2p)
oe2 = f.oriented_edge(e2, True)

# ── EDGE_LOOP: 3 edges, wire nearly closed (5e-8 gap) ────────────────────────
loop = f.edge_loop([oe0, oe1, oe2])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi160.stp")
