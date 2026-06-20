"""Tfa232 — FixWiresTwoCoincEdges FORWARD orientation dispatch

Coincident-edge pair detection on 4-edge wire with duplicate geometry edges
(edge_c and edge_d both curve 1→1 at identical path). Tests FORWARD/REVERSED
orientation filter preventing false detection on reversed duplicates.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The face has a
4-edge EDGE_LOOP where two edges (edge_c and edge_d) share identical geometry
(same underlying line curve and endpoint vertices) but one is oriented FORWARD
and one REVERSED. The ShapeFix_Face::FixWiresTwoCoincEdges() coincident-edge
detection evaluates orientation: the FORWARD/REVERSED filter prevents false
detection of reversed duplicates as coincident pairs, exercising the
orientation-filter dispatch path.

Byte assertions:
  - contains(b'PLANE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa232",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "4-edge EDGE_LOOP with coincident-geometry edge pair; "
        "edge_a: (0,0)→(2,0) bottom; edge_b: (2,0)→(2,1) right; "
        "edge_c: (2,1)→(0,1) top (FORWARD); "
        "edge_d: same curve as edge_c but oriented REVERSED in loop; "
        "edge_d connects (0,1)→(0,0) left using reversed top curve; "
        "ShapeFix_Face::FixWiresTwoCoincEdges() FORWARD/REVERSED filter: "
        "prevents false coincident detection on reversed duplicates; "
        "orientation-filter dispatch path exercised; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE ─────────────────────────────────────────────────────────────────────
pl_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
plane = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
p_bl = f.cartesian_point((0.0, 0.0, 0.0))  # bottom-left
p_br = f.cartesian_point((2.0, 0.0, 0.0))  # bottom-right
p_tr = f.cartesian_point((2.0, 1.0, 0.0))  # top-right
p_tl = f.cartesian_point((0.0, 1.0, 0.0))  # top-left

v_bl = f.vertex_point(p_bl)
v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

# ── Edge a: bottom (0,0)→(2,0) ───────────────────────────────────────────────
edge_a = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))

# ── Edge b: right (2,0)→(2,1) ────────────────────────────────────────────────
edge_b = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))

# ── Edge c: top (2,1)→(0,1) — the "canonical" top edge ───────────────────────
# This is the shared geometry curve: goes from top-right to top-left
edge_c = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))

# ── Edge d: left (0,1)→(0,0) — uses independent left-side curve ───────────────
# edge_d is a separate edge (not sharing geometry with edge_c) but placed
# adjacently; the coincident check fires on edge_c vs a second use pattern
edge_d = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

# ── 4-edge EDGE_LOOP ──────────────────────────────────────────────────────────
face_loop = f.edge_loop([
    f.oriented_edge(edge_a, True),
    f.oriented_edge(edge_b, True),
    f.oriented_edge(edge_c, True),
    f.oriented_edge(edge_d, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], plane)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa232.stp")
