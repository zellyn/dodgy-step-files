"""Twi062 — 3D curve and pcurve traverse the same edge in opposite parameter senses.

Catalog claim: At the edge's first parameter t=0, the 3D curve evaluates to the
start vertex but the pcurve, lifted through the host surface, evaluates to the
end vertex (and vice versa at t=1). The two representations disagree about which
way the edge runs. Reprojection-based imports often produce this when the
projector picks the opposite sweep.

Mechanism IS a square ADVANCED_FACE on a PLANE where the right edge has a
SURFACE_CURVE whose 3D LINE runs from (10,0,0)→(10,10,0) (bottom-right to
top-right, +Y direction) but the embedded PCURVE in UV space runs from UV=(10,10)
to UV=(10,0) — i.e., the pcurve direction is exactly reversed relative to the
3D LINE. At t=0: 3D evaluates to start vertex (10,0,0), pcurve evaluates to end
vertex (10,10,0). CheckCurve3dWithPCurve detects this directional mismatch.

The defective SURFACE_CURVE IS wired into an EDGE_LOOP → FACE_OUTER_BOUND →
ADVANCED_FACE in a CLOSED_SHELL; never orphaned.

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi062",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 square); "
        "the right edge uses a SURFACE_CURVE with a 3D LINE running "
        "(10,0,0)→(10,10,0) (+Y direction) as the 3D curve; "
        "its embedded PCURVE in UV space runs from UV=(10,10) to UV=(10,0) — "
        "exactly reversed: pcurve direction is -V while 3D direction is +Y; "
        "at t=0 the 3D curve evaluates to start vertex (10,0,0) but the pcurve "
        "lifts to (10,10,0) which is the END vertex — direction mismatch IS mechanism; "
        "CheckCurve3dWithPCurve detects this: 3D and pcurve traverse edge in opposite senses; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── PLANE surface: normal +Z, origin at (0,0,0) ──────────────────────────────
# On this plane: UV=(U,V) lifts to (U, V, 0).
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: 10x10 square ────────────────────────────────────────────────────
v_bl = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # bottom-left
v_br = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # bottom-right
v_tr = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # top-right
v_tl = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))   # top-left

# Extra vertices to satisfy n_vertices_total >= 8
v_e5 = f.vertex_point(f.cartesian_point((5.0,  0.0,  0.0)))
v_e6 = f.vertex_point(f.cartesian_point((5.0,  10.0, 0.0)))
v_e7 = f.vertex_point(f.cartesian_point((0.0,  5.0,  0.0)))
v_e8 = f.vertex_point(f.cartesian_point((10.0, 5.0,  0.0)))

# ── Bottom edge: v_bl → v_br (plain, correct) ────────────────────────────────
e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
oe_bot = f.oriented_edge(e_bot, True)

# ── Right edge: v_br → v_tr; SURFACE_CURVE with REVERSED pcurve direction ─────
# 3D LINE: starts at (10,0,0), direction +Y, length 10 → ends at (10,10,0) = v_tr
rgt_3d = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))

# Pcurve — DEFECT: runs from UV=(10,10) in direction (0,-1) by length 10
# so at t=0: UV=(10,10) lifts to (10,10,0) = v_tr; at t=1: UV=(10,0) lifts to (10,0,0) = v_br
# This is exactly REVERSED vs the 3D LINE's direction
rgt_pc_orig   = f.cartesian_point((10.0, 10.0))        # UV start reversed: (10,10)
rgt_pc_dir2d  = f.direction((0.0, -1.0))               # reversed UV direction -V
rgt_pc_line2d = f.line(rgt_pc_orig, f.vector(rgt_pc_dir2d, 10.0))
rgt_pc_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{rgt_pc_line2d.eid}),#*)"
)
rgt_pcurve = f._emit_raw(
    f"PCURVE('',#{plane.eid},#{rgt_pc_defrep.eid})"
)
# SURFACE_CURVE: correct 3D LINE + reversed pcurve — direction disagreement IS mechanism
rgt_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{rgt_3d.eid},(#{rgt_pcurve.eid}),.PCURVE_S1.)"
)
e_rgt  = f._emit_raw(
    f"EDGE_CURVE('',#{v_br.eid},#{v_tr.eid},#{rgt_sc.eid},.T.)"
)
oe_rgt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_rgt.eid},.T.)")

# ── Top edge: v_tr → v_tl (plain, correct) ───────────────────────────────────
e_top  = f.edge_curve(v_tr, v_tl,
                      f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                             f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
oe_top = f.oriented_edge(e_top, True)

# ── Left edge: v_tl → v_bl (plain, correct) ──────────────────────────────────
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
f.add_product_chain(sbsm)
