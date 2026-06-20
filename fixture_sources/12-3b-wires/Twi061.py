"""Twi061 — Vertex tolerance check returns required inflation amount.

Catalog claim: Diagnostic that, given an edge and its host face, computes the
minimum vertex tolerance that would be needed to absorb the edge endpoint
discrepancy. Returns separate values for the two endpoints. Lets the caller
choose between snap and tolerance-inflate. The diagnostic should report
toler1=5e-3 for the offset corner and toler2=0 for the others.

Mechanism IS identical to Twi048: a 10x10 square ADVANCED_FACE on a PLANE with
the top-right VERTEX_POINT at (10.005, 10.0, 0.0) instead of (10.0, 10.0, 0.0).
The UNCERTAINTY_MEASURE_WITH_UNIT declares global tolerance 1e-6 via the product
chain. CheckVertexTolerance on the right edge would compute: toler1=0 (start
vertex at (10,0,0) matches curve start), toler2=5e-3 (end vertex at (10.005,10,0)
is 0.005 from curve end (10,10,0)). The per-vertex inflation requirement IS the
mechanism — CheckVertexTolerance is diagnostic-only, it does not modify the shape.

Byte assertions:
  - contains(b'(10.005,10.0,0.0)')
  - contains(b'UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-06)')

Tier-3 assertions:
  - n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi061",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 square); "
        "EDGE_LOOP contains four EDGE_CURVEs; "
        "the top-right VERTEX_POINT is declared at (10.005,10.0,0.0) — offset 0.005 "
        "from where the right-edge 3D LINE evaluates at endpoint (10.0,10.0,0.0); "
        "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-06),...) sets global tolerance 1e-6; "
        "CheckVertexTolerance on the right edge returns toler1=0 (start vertex is exact) "
        "and toler2=5e-3 (end vertex needs 0.005 inflation to absorb the gap); "
        "per-vertex tolerance inflation requirement IS the mechanism; "
        "diagnostic-only: CheckVertexTolerance does not modify the shape; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: 10x10 square; top-right at (10.005, 10, 0) IS mechanism ─────────
v_bl = f.vertex_point(f.cartesian_point((0.0,    0.0,  0.0)))   # bottom-left
v_br = f.vertex_point(f.cartesian_point((10.0,   0.0,  0.0)))   # bottom-right
# DEFECT: vertex should be (10.0, 10.0, 0.0); declared 0.005 off
v_tr = f.vertex_point(f.cartesian_point((10.005, 10.0, 0.0)))   # top-right — OFFSET
v_tl = f.vertex_point(f.cartesian_point((0.0,   10.0, 0.0)))    # top-left

# ── Bottom edge: v_bl → v_br (correct) ───────────────────────────────────────
e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
oe_bot = f.oriented_edge(e_bot, True)

# ── Right edge: v_br → v_tr; curve ends at (10.0, 10.0, 0.0) but v_tr is at
#    (10.005, 10.0, 0.0) — end-vertex inflation requirement = 5e-3 IS mechanism
e_rgt  = f.edge_curve(v_br, v_tr,
                      f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
oe_rgt = f.oriented_edge(e_rgt, True)

# ── Top edge: v_tr → v_tl; LINE starts at offset vertex location ──────────────
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
# CRITICAL: use uncertainty=1.0E-06 so the file contains
# UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-06),...) — byte assertion
f.add_product_chain(sbsm, uncertainty=1.0E-06)
