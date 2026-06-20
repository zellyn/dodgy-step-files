"""Gn019 — Degenerate zero-length B_SPLINE pcurve (coincident control points / sample count <2).

Catalog claim: A pcurve on a CYLINDRICAL_SURFACE (or other periodic surface) is a
degenerate B_SPLINE_CURVE_WITH_KNOTS of degree 1 whose two control points are both
at the same UV (e.g. both (0,0)); a zero-length pcurve representing a seam. When
sampling such a pcurve for an ON_BrepTrim, step-g gets fewer than 2 distinct sample
points, yielding a degenerate trim.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE, radius=1, height=3.
  - Seam edge on the cylinder: the pcurve is a B_SPLINE_CURVE_WITH_KNOTS of degree 1,
    2 control points, BOTH at UV=(0.0, 0.0) — coincident, zero-length.
    Knots (0,1) mults (2,2) sum=4=1+2+1 ✓. This is the degenerate pcurve defect.
  - The 3D edge curve is a valid LINE along the seam (Z from 0 to 3, X=1, Y=0).
  - C-1 DRIVER: a second edge (bottom) uses B_SPLINE_CURVE_WITH_KNOTS degree-2
    positional break at t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap)
    in its 3D curve to ensure shape_null=True regardless of how OCC handles the
    degenerate pcurve.

Mechanism vs driver:
  - CATALOG MECHANISM: degree-1 B_SPLINE_CURVE_WITH_KNOTS pcurve with both CPs
    at (0,0) — coincident, zero-length; sample count evaluates to <2 distinct
    points; degenerate trim on cylindrical surface seam.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn019",
    defect=(
        "CYLINDRICAL_SURFACE seam pcurve B_SPLINE_CURVE_WITH_KNOTS degree-1 2 CPs; "
        "both CPs at UV=(0.0,0.0) — coincident, zero-length pcurve; "
        "knots (0.0,1.0) mults (2,2) sum=4=1+2+1 ✓; "
        "sample count <2 distinct points → degenerate trim in BRep; "
        "seam edge 3D curve is valid LINE along cylinder seam (Z: 0→3, X=1, Y=0); "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── DEFECT SURFACE: CYLINDRICAL_SURFACE, radius=1, height=3 ─────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
surf = f._emit_raw(f"CYLINDRICAL_SURFACE('degenerate_pcurve_cyl',#{cyl_plc.eid},1.0)")

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices on the seam: bottom (X=1, Y=0, Z=0) and top (X=1, Y=0, Z=3)
p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 3.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

# ── SEAM EDGE: 3D LINE valid; pcurve DEGENERATE (both CPs at (0,0)) ──────────
# 3D edge curve: line from (1,0,0) to (1,0,3) along Z
seam_p  = f.cartesian_point((1.0, 0.0, 0.0))
seam_d  = f.direction((0.0, 0.0, 1.0))
seam_v  = f.vector(seam_d, 3.0)
seam_l  = f.line(seam_p, seam_v)

# Degenerate pcurve: degree-1, 2 CPs both at (0.0, 0.0) in UV
dpc0 = f.cartesian_point((0.0, 0.0))   # coincident
dpc1 = f.cartesian_point((0.0, 0.0))   # coincident — zero-length pcurve

degen_pc_bsp = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degenerate_zero_length_pcurve',1,"
    f"(#{dpc0.eid},#{dpc1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

degen_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('degen_pcurve_def',(#{degen_pc_bsp.eid}),#{prc.eid})"
)
degen_pcurve = f._emit_raw(
    f"PCURVE('degen_pcurve_ent',#{surf.eid},#{degen_defrep.eid})"
)
seam_sc = f._emit_raw(
    f"SURFACE_CURVE('seam_sc',#{seam_l.eid},(#{degen_pcurve.eid}),.PCURVE_S1.)"
)
e_seam = f._emit_raw(
    f"EDGE_CURVE('seam_edge',#{v_bot.eid},#{v_top.eid},#{seam_sc.eid},.T.)"
)

# ── DEFECT EDGE — C-1 DRIVER ─────────────────────────────────────────────────
# Bottom circle arc (partial, from seam back to seam via a half arc, simplified to
# a B-spline with C-1 break).
dc0 = f.cartesian_point((1.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.75, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.5,  0.0, 0.0))
dc5 = f.cartesian_point((4.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degen_pcurve_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve for the C-1 driver edge: goes from V=0 to V=1 (0 to 2π) at U=0 (Z=0)
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.0,  0.25))
pp2 = f.cartesian_point((0.0,  0.5))
pp3 = f.cartesian_point((0.0,  0.5))
pp4 = f.cartesian_point((0.0,  0.75))
pp5 = f.cartesian_point((0.0,  1.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degen_pcurve_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('degen_c1_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve_c1 = f._emit_raw(f"PCURVE('degen_c1_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('degen_c1_sc',#{bspline_3d.eid},(#{pcurve_c1.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('degen_c1_edge',#{v_bot.eid},#{v_top.eid},#{sc_bot.eid},.T.)"
)

# Simple 2-edge loop: seam up + C-1 driver down (both v_bot→v_top, one reversed)
loop = f.edge_loop([
    f.oriented_edge(e_seam, True),
    f.oriented_edge(e_bot,  False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
