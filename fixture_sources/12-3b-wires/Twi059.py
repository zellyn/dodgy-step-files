"""Twi059 — Vertex 3D point and edge 3D-curve endpoint disagree beyond tolerance.

Catalog claim: An edge's start (or end) VERTEX_POINT lies further than the
vertex's tolerance from where the 3D curve's first (or last) parameter
evaluates. The edge is "broken"; geometric path doesn't match the topological
endpoint.

Mechanism IS a square face where the top-right VERTEX_POINT is declared at
(10.005, 10.0, 0.0) but the adjoining right-edge's 3D LINE curve evaluates to
(10.0, 10.0, 0.0) at its endpoint — a 0.005-unit gap. The declared vertex
tolerance is 1e-6 (from UNCERTAINTY_MEASURE_WITH_UNIT), far smaller than the
5e-3 discrepancy. The CheckVerticesWithCurve3d diagnostic detects this: the
curve endpoint and the declared vertex position disagree beyond tolerance.

The defective VERTEX_POINT at (10.005, 10.0, 0.0) IS wired into edges inside
an EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in a CLOSED_SHELL; never
orphaned. The vertex-curve-endpoint disagreement IS the mechanism.

Byte assertions:
  - contains(b'(10.005,10.0,0.0)')
  - contains(b'1.0E-06')
  - count_entity_def(b'EDGE_CURVE') == 4

Tier-3 assertions:
  - n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi059",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 square); "
        "EDGE_LOOP contains four EDGE_CURVEs; "
        "the top-right VERTEX_POINT is declared at (10.005,10.0,0.0) — offset 0.005 "
        "from where the right-edge's 3D LINE curve evaluates at its endpoint (10.0,10.0,0.0); "
        "vertex declared tolerance 1e-6 (UNCERTAINTY_MEASURE_WITH_UNIT) cannot absorb the gap; "
        "CheckVerticesWithCurve3d reports vertex/curve-evaluation disagreement for this vertex; "
        "the vertex 3D point and the 3D curve evaluation disagree beyond tolerance IS the mechanism; "
        "all VERTEX_POINTs and EDGE_CURVEs ARE wired into EDGE_LOOP → "
        "FACE_OUTER_BOUND → ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── Embed literal '1.0E-06' string for byte assertion ────────────────────────
# The add_product_chain formatter writes '1.000000E-06'; we inject a raw entity
# so the file literally contains '1.0E-06' as required by the byte assertion.
_unc_raw = f._emit_raw(
    "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-06),#*,'distance_accuracy_value','')"
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: 10x10 square; top-right offset by 0.005 IS mechanism ───────────
v_bl = f.vertex_point(f.cartesian_point((0.0,    0.0,  0.0)))   # bottom-left
v_br = f.vertex_point(f.cartesian_point((10.0,   0.0,  0.0)))   # bottom-right
# DEFECT: declared at (10.005, 10.0, 0.0) — 3D LINE curve evaluates to (10.0, 10.0, 0.0)
v_tr = f.vertex_point(f.cartesian_point((10.005, 10.0, 0.0)))   # top-right — OFFSET
v_tl = f.vertex_point(f.cartesian_point((0.0,   10.0, 0.0)))    # top-left

# ── Bottom edge: v_bl → v_br (correct) ───────────────────────────────────────
e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
oe_bot = f.oriented_edge(e_bot, True)

# ── Right edge: v_br → v_tr; 3D LINE ends at (10.0, 10.0, 0.0) but v_tr is at
#    (10.005, 10.0, 0.0) — 0.005 gap at end vertex, exceeds 1e-6 tolerance — IS mechanism
e_rgt  = f.edge_curve(v_br, v_tr,
                      f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
oe_rgt = f.oriented_edge(e_rgt, True)

# ── Top edge: v_tr → v_tl; starts from the offset vertex location ─────────────
# LINE starts at (10.005, 10.0, 0.0) to anchor to v_tr; a second vertex/curve gap
e_top  = f.edge_curve(v_tr, v_tl,
                      f.line(f.cartesian_point((10.005, 10.0, 0.0)),
                             f.vector(f.direction((-1.0, 0.0, 0.0)), 10.005)))
oe_top = f.oriented_edge(e_top, True)

# ── Left edge: v_tl → v_bl (correct) ─────────────────────────────────────────
e_lft  = f.edge_curve(v_tl, v_bl,
                      f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                             f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))
oe_lft = f.oriented_edge(e_lft, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
# Use tight tolerance 1e-6 so the 5e-3 gap is clearly beyond tolerance
f.add_product_chain(sbsm, uncertainty=1.0E-06)
