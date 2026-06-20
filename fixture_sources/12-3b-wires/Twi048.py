"""Twi048 — Vertex tolerance smaller than the edge endpoint discrepancy it must absorb.

Catalog claim: A VERTEX_POINT carries a tolerance of 1e-6, but the edge curve's
evaluation at the endpoint is 5e-3 away from the vertex. The vertex's tolerance ball
does not reach the curve, so any "is this point on this edge?" query fails. Often
produced by senders that compute vertex tolerance globally rather than per-incident-edge.

Mechanism IS the VERTEX_POINT at (10.005, 10.0, 0.0) where the adjoining edge's 3D
LINE curve runs from (10.0, 0.0, 0.0) to (10.0, 10.0, 0.0); curve evaluation at the
endpoint reaches (10.0, 10.0, 0.0), but the declared VERTEX_POINT is 0.005 away.
The UNCERTAINTY_MEASURE_WITH_UNIT declares global tolerance 1e-6 — far smaller than
the 5e-3 discrepancy. The defective VERTEX_POINT IS wired into edges inside an
EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in a SHELL_BASED_SURFACE_MODEL;
never orphaned. The tolerance-ball miss IS the mechanism.

Byte assertions:
  - contains(b'(10.005,10.0,0.0)')
  - contains(b'1.0E-06')
  - contains(b'UNCERTAINTY_MEASURE_WITH_UNIT(')

Tier-3 assertions:
  - n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi048",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 square); "
        "EDGE_LOOP contains four EDGE_CURVEs; "
        "the top-right VERTEX_POINT is declared at (10.005,10.0,0.0) — offset 0.005 "
        "from where the adjoining edges' LINE curves evaluate; "
        "UNCERTAINTY_MEASURE_WITH_UNIT sets global tolerance 1e-6 which cannot absorb "
        "the 5e-3 endpoint discrepancy; "
        "the vertex tolerance ball does not reach the incident curves IS the mechanism; "
        "all VERTEX_POINTs and EDGE_CURVEs ARE wired into EDGE_LOOP → "
        "FACE_OUTER_BOUND → ADVANCED_FACE in shell — never orphaned; "
        "kernel must detect the shortfall and inflate vertex tolerance, snap vertex to "
        "curve, or reject the edge as not same-parameter"
    ),
)

# ── Force the UNCERTAINTY_MEASURE_WITH_UNIT into the file header via product chain ──
# The tolerance declaration is embedded as a named entity in the DATA section.
unc_val   = f._emit_raw("LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-06),#*)")
unc_ctxt  = f._emit_raw(
    "GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT('3D LENGTH','',1.0E-06,'MM')"
)
unc_entity = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-06),#*,'distance_accuracy_value','')"
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: 10x10 square; top-right offset by 0.005 IS mechanism ───────────
v_bl = f.vertex_point(f.cartesian_point((0.0,   0.0,  0.0)))   # bottom-left
v_br = f.vertex_point(f.cartesian_point((10.0,  0.0,  0.0)))   # bottom-right
# DEFECT: declared at (10.005, 10.0, 0.0) instead of (10.0, 10.0, 0.0)
v_tr = f.vertex_point(f.cartesian_point((10.005, 10.0, 0.0)))  # top-right — OFFSET
v_tl = f.vertex_point(f.cartesian_point((0.0,   10.0, 0.0)))   # top-left

# ── Bottom edge: v_bl → v_br (correct) ───────────────────────────────────────
bot_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                  f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e_bot  = f.edge_curve(v_bl, v_br, bot_line)
oe_bot = f.oriented_edge(e_bot, True)

# ── Right edge: v_br → v_tr; curve ends at (10.0,10.0,0.0) but v_tr is at
#    (10.005,10.0,0.0) — 0.005 gap, exceeds 1e-6 tolerance — IS mechanism ────
rgt_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                  f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e_rgt  = f.edge_curve(v_br, v_tr, rgt_line)
oe_rgt = f.oriented_edge(e_rgt, True)

# ── Top edge: v_tr → v_tl; starts from offset vertex — gap on start side too ─
top_line = f.line(f.cartesian_point((10.005, 10.0, 0.0)),
                  f.vector(f.direction((-1.0, 0.0, 0.0)), 10.005))
e_top  = f.edge_curve(v_tr, v_tl, top_line)
oe_top = f.oriented_edge(e_top, True)

# ── Left edge: v_tl → v_bl (correct) ─────────────────────────────────────────
lft_line = f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                  f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
e_lft  = f.edge_curve(v_tl, v_bl, lft_line)
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
f.add_product_chain(sbsm)
