"""Gp111 — ShapeAnalysis_Edge.CheckCurve3dWithPCurve different-trim-ranges.

Catalog claim: 3D curve range [0,1] and pcurve range [0.2, 0.8] cover different
portions. CheckCurve3dWithPCurve samples uniform parameter space and compares
wrong portions of geometry.

STEP mechanism (literal):
  - PLANE Z=0 face. Defect edge via SURFACE_CURVE.
  - 3D curve: LINE from (0,0,0) to (5,0,0) — clean geometry.
  - SURFACE_CURVE references TWO pcurves:
    pcurve-1: LINE in UV from (0,0) in direction (1,0), covering full UV [0,5].
    pcurve-2: LINE in UV from (1,0) in direction (1,0), covering only UV [1,4]
    (a partial sub-range corresponding to roughly [0.2, 0.8] of the 3D extent).
  - THE CATALOG MECHANISM: CheckCurve3dWithPCurve samples the edge at uniform
    parameter values along the 3D curve. When it queries pcurve-2 at parameter
    t=0 (edge start) or t=5 (edge end), the pcurve-2 evaluates at a point that
    doesn't correspond to the actual 3D position — it compares wrong portions of
    the geometry. The checker does not reconcile which pcurve's trim range to
    trust. OCC heals silently using pcurve-1 (full coverage).
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_CURVE referencing two pcurves; pcurve-2 has a
    partial UV sub-range [1,4] instead of full range [0,5], modeling the
    different-trim-ranges defect; CheckCurve3dWithPCurve compares mismatched
    portions without reconciling.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp111",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D LINE (0,0,0)→(5,0,0); "
        "pcurve-1: LINE UV (0,0) direction (1,0) length 5 — full range [0,5]; "
        "pcurve-2: LINE UV (1,0) direction (1,0) length 3 — partial range [1,4] "
        "(covers only 60% of edge, modeling [0.2,0.8] trim-range mismatch); "
        "CheckCurve3dWithPCurve samples uniform params and queries pcurve-2 at "
        "positions outside its UV coverage; trim-range mismatch unreconciled; "
        "OCC heals using pcurve-1; shape(1)/shape(1)"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) — bare EDGE_CURVE with LINE
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# 3D curve: clean LINE from (0,0,0) to (5,0,0)
line_p  = f.cartesian_point((0.0, 0.0, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 5.0)
line_3d = f.line(line_p, line_v)

# PCurve-1: LINE in UV from (0,0) direction (1,0) length 5 — FULL coverage [0,5]
pc1_pt  = f.cartesian_point((0.0, 0.0))
pc1_dir = f.direction((1.0, 0.0))
pc1_vec = f.vector(pc1_dir, 5.0)
pc1_line = f.line(pc1_pt, pc1_vec)
defrep1 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('trimrange_pc1_def',(#{pc1_line.eid}),#{prc.eid})"
)
pcurve1 = f._emit_raw(f"PCURVE('trimrange_pc1',#{surf.eid},#{defrep1.eid})")

# PCurve-2: LINE in UV from (1,0) direction (1,0) length 3 — PARTIAL coverage [1,4]
# THE CATALOG MECHANISM: pcurve-2 maps to UV range [1,4] while the 3D LINE spans
# [0,5]. CheckCurve3dWithPCurve samples the 3D edge at uniform parameter values
# and queries pcurve-2 at those positions — but pcurve-2's UV start (1,0) doesn't
# correspond to the 3D start (0,0,0). The checker compares wrong portions of
# geometry without detecting the trim-range mismatch. OCC heals using pcurve-1.
pc2_pt  = f.cartesian_point((1.0, 0.0))
pc2_dir = f.direction((1.0, 0.0))
pc2_vec = f.vector(pc2_dir, 3.0)
pc2_line = f.line(pc2_pt, pc2_vec)
defrep2 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('trimrange_pc2_def',(#{pc2_line.eid}),#{prc.eid})"
)
pcurve2 = f._emit_raw(f"PCURVE('trimrange_pc2',#{surf.eid},#{defrep2.eid})")

# SURFACE_CURVE: 3D=LINE, associated_geometry=[pcurve1(full), pcurve2(partial)]
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('trimrange_sc',#{line_3d.eid},"
    f"(#{pcurve1.eid},#{pcurve2.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('trimrange_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
