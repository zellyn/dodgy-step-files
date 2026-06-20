"""Twi060 — Vertex 3D point and edge pcurve endpoint disagree beyond tolerance.

Catalog claim: As Twi059 but the disagreement is between the 3D vertex and the
pcurve evaluated through the host surface. Both representations claim the same
endpoint; in fact they don't agree. Common when senders regenerate one
representation independently of the other.

Mechanism IS a square ADVANCED_FACE on a PLANE where one edge has a SURFACE_CURVE
combining a correct 3D LINE with a pcurve whose UV coordinates, when lifted
through the PLANE, evaluate to (10.0, 10.0, 0.0) — but the declared end
VERTEX_POINT is at (10.005, 10.0, 0.0). The 3D vertex disagrees with the pcurve
endpoint by 0.005, exceeding the declared tolerance of 1e-6. The pcurve is
anchored correctly in UV space; the vertex is the outlier. The defective
VERTEX_POINT IS wired into an EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in a
CLOSED_SHELL; never orphaned.

Byte assertions:
  - contains(b'(10.005,10.0,0.0)')
  - contains(b'1.0E-06')
  - contains(b'PLANE(')

Tier-3 assertions:
  - n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi060",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 square); "
        "the right edge uses a SURFACE_CURVE with a 3D LINE plus a PCURVE in UV; "
        "the PCURVE evaluates (via the PLANE surface) to (10.0, 10.0, 0.0) at t=1 — "
        "but the declared end VERTEX_POINT is at (10.005, 10.0, 0.0); "
        "the pcurve-endpoint vs 3D-vertex disagreement of 0.005 exceeds declared "
        "tolerance 1e-6; CheckVerticesWithPCurve reports the mismatch; "
        "pcurve-counterpart of Twi059: pcurve is correct, vertex is the outlier; "
        "the vertex/pcurve-endpoint disagreement IS the mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── Embed literal '1.0E-06' string for byte assertion ────────────────────────
# The add_product_chain formatter writes '1.000000E-06'; we inject a raw entity
# so the file literally contains '1.0E-06' as required by the byte assertion.
_unc_raw = f._emit_raw(
    "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-06),#*,'distance_accuracy_value','')"
)

# ── PLANE surface: normal +Z, axes at origin ──────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: 10x10 square; top-right is offset — IS the pcurve/vertex mismatch
v_bl = f.vertex_point(f.cartesian_point((0.0,    0.0,  0.0)))   # bottom-left
v_br = f.vertex_point(f.cartesian_point((10.0,   0.0,  0.0)))   # bottom-right
# DEFECT: vertex at (10.005, 10.0, 0.0); pcurve evaluates to (10.0, 10.0, 0.0)
v_tr = f.vertex_point(f.cartesian_point((10.005, 10.0, 0.0)))   # top-right — OFFSET
v_tl = f.vertex_point(f.cartesian_point((0.0,   10.0, 0.0)))    # top-left

# ── Bottom edge: v_bl → v_br; plain EDGE_CURVE (no pcurve needed) ────────────
e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
oe_bot = f.oriented_edge(e_bot, True)

# ── Right edge: v_br → v_tr; SURFACE_CURVE with 3D LINE + PCURVE ─────────────
# 3D LINE: correct, from (10,0,0) going +Y by 10 → ends at (10,10,0)
rgt_3d = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))

# Pcurve on the PLANE: UV = (U, V) maps to (U, V, 0) on this +Z plane.
# Correct pcurve goes from UV=(10,0) to UV=(10,10), lifting to (10,0,0)→(10,10,0).
# The pcurve endpoint (10,10) lifts to (10.0, 10.0, 0.0) — vertex is at (10.005, 10.0, 0.0).
# The 0.005 discrepancy IS the CheckVerticesWithPCurve defect.
rgt_pc_orig   = f.cartesian_point((10.0, 0.0))          # UV start (t=0): lifts to (10,0,0)
rgt_pc_dir2d  = f.direction((0.0, 1.0))                 # UV direction +V
rgt_pc_line2d = f.line(rgt_pc_orig, f.vector(rgt_pc_dir2d, 10.0))
rgt_pc_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{rgt_pc_line2d.eid}),#*)"
)
rgt_pcurve = f._emit_raw(
    f"PCURVE('',#{plane.eid},#{rgt_pc_defrep.eid})"
)
# SURFACE_CURVE: 3D LINE + pcurve
rgt_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{rgt_3d.eid},(#{rgt_pcurve.eid}),.PCURVE_S1.)"
)
e_rgt  = f._emit_raw(
    f"EDGE_CURVE('',#{v_br.eid},#{v_tr.eid},#{rgt_sc.eid},.T.)"
)
oe_rgt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_rgt.eid},.T.)")

# ── Top edge: v_tr → v_tl (correct plain edge) ───────────────────────────────
e_top  = f.edge_curve(v_tr, v_tl,
                      f.line(f.cartesian_point((10.005, 10.0, 0.0)),
                             f.vector(f.direction((-1.0, 0.0, 0.0)), 10.005)))
oe_top = f.oriented_edge(e_top, True)

# ── Left edge: v_tl → v_bl (correct plain edge) ──────────────────────────────
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
# Declare tight tolerance 1e-6 so the 0.005 pcurve/vertex gap is detectable
f.add_product_chain(sbsm, uncertainty=1.0E-06)
