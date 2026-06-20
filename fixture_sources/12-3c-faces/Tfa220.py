"""Tfa220 — concat_result_truncation

PLANE face whose EDGE_LOOP mixes a straight LINE edge with a circular arc
separated by a bridging segment. The gap between LINE and CIRCLE is large
enough that ConcatC1 in UnionPCurves (line 2037) produces 2 fragments.
Without fragment-count validation the code calls Add() anyway, force-merging
them into an artificial C1 chain with a discontinuity.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The face outer
boundary is a 4-edge loop:
  e0: LINE (0,0)→(2,0)
  e_gap: bridging LINE (2,0)→(8,5) — large gap ~7.81 units
  e1: CIRCLE arc (8,5)→(7,4): quarter arc, center (7,5), radius 1
  e2: closing LINE (7,4)→(0,0)
The large gap between the line endpoint and circle means ConcatC1 cannot
produce a geometrically continuous result — it returns 2 fragments. Without
validation at line 2037 the code force-merges, creating artificial C1 chain.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'CIRCLE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa220",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "4-edge loop: LINE(0,0→2,0) + GAP-LINE(2,0→8,5) len≈7.81 + "
        "CIRCLE-arc center(7,5) r=1 from(8,5)→(7,4) + CLOSE-LINE(7,4→0,0); "
        "large gap (~7.81 units) between LINE end and CIRCLE start; "
        "UnionPCurves line 2037: ConcatC1 returns 2 fragments for gapped chain; "
        "code calls Add() without fragment-count check → force-merged artificial C1; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ───────────────────────────────────────
plane_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
surf = f.plane(plane_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
p_v0 = f.cartesian_point((0.0, 0.0, 0.0))   # loop start/end
p_v1 = f.cartesian_point((2.0, 0.0, 0.0))   # LINE end
p_v2 = f.cartesian_point((8.0, 5.0, 0.0))   # arc start (after large gap)
p_v3 = f.cartesian_point((7.0, 4.0, 0.0))   # arc end

v_v0 = f.vertex_point(p_v0)
v_v1 = f.vertex_point(p_v1)
v_v2 = f.vertex_point(p_v2)
v_v3 = f.vertex_point(p_v3)

# ── e0: straight LINE (0,0,0)→(2,0,0) ────────────────────────────────────────
e0 = f.edge_curve(
    v_v0, v_v1,
    f.line(p_v0, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0))
)

# ── e_gap: bridging LINE (2,0,0)→(8,5,0) — large gap ~7.81 ─────────────────
gap_dx, gap_dy = 6.0, 5.0
gap_len = _math.sqrt(gap_dx**2 + gap_dy**2)
e_gap = f.edge_curve(
    v_v1, v_v2,
    f.line(p_v1, f.vector(f.direction((gap_dx/gap_len, gap_dy/gap_len, 0.0)), gap_len))
)

# ── e1: CIRCLE arc from (8,5,0) to (7,4,0) ───────────────────────────────────
# Center (7,5,0), radius=1.0. At angle=0 → (8,5,0); at angle=-π/2 → (7,4,0).
arc_ctr = f.cartesian_point((7.0, 5.0, 0.0))
arc_plc = f.axis2_placement_3d(
    arc_ctr,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),   # ref dir → angle=0 at (8,5,0)
)
arc_circle = f.circle(arc_plc, 1.0)
e1 = f.edge_curve(v_v2, v_v3, arc_circle)

# ── e2: closing LINE (7,4,0)→(0,0,0) ─────────────────────────────────────────
close_dx, close_dy = -7.0, -4.0
close_len = _math.sqrt(close_dx**2 + close_dy**2)
e2 = f.edge_curve(
    v_v3, v_v0,
    f.line(p_v3, f.vector(f.direction((close_dx/close_len, close_dy/close_len, 0.0)), close_len))
)

# ── EDGE_LOOP: 4 edges ────────────────────────────────────────────────────────
face_loop = f.edge_loop([
    f.oriented_edge(e0,     True),
    f.oriented_edge(e_gap,  True),
    f.oriented_edge(e1,     True),
    f.oriented_edge(e2,     True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa220.stp")
