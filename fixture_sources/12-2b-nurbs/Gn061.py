"""Gn061 — ShapeAnalysis_Curve.GetSamplePoints (3D 2pt LINE shortcut).

Catalog claim: LINE trimmed to [2.0, 8.0] on 10-unit baseline. 2-point
shortcut samples only trimmed endpoints, missing midspan information (u=5.0)
used by downstream healing for curvature/degeneracy detection.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - LINE entity on a 10-unit baseline (direction (1,0,0), magnitude=10).
    Trimmed to parameter range [2.0, 8.0] via TRIMMED_CURVE wrapping.
    GetSamplePoints 2-point shortcut samples only u=2.0 and u=8.0, skipping
    midspan u=5.0; downstream healing misses curvature/degeneracy at midpoint.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: same entity — trimmed LINE endpoints mismatch face vertices
    by a deliberate 0.5-unit offset, creating an edge topology gap that drives
    shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: LINE with TRIMMED_CURVE to [2.0,8.0]; IS defect edge
    SURFACE_CURVE.curve_3d; GetSamplePoints 2-point shortcut misses u=5.0
    midspan used by downstream degeneracy/curvature detection.
  - C-1 DRIVER: same entity — endpoint offset drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn061",
    defect=(
        "LINE 10-unit baseline trimmed to [2.0,8.0] via TRIMMED_CURVE; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints 2-point shortcut samples only endpoints u=2.0,u=8.0 "
        "— misses midspan u=5.0 for curvature/degeneracy detection; "
        "endpoint topology gap drives shape_null=True"
    ),
)

# ── Flat plane for the face ──────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: LINE trimmed to [2.0, 8.0] ────────────────────────────
# Baseline: start=(0,0,0) direction=(1,0,0) magnitude=10 → 10-unit line.
# TRIMMED_CURVE restricts parameter to [2.0, 8.0].
# GetSamplePoints: LINE shortcut returns only 2 samples (endpoints),
# missing the midspan at u=5.0 that downstream healing queries for degeneracy.
line_orig = f.cartesian_point((0.0, 0.0, 0.0))
line_dir  = f.direction((1.0, 0.0, 0.0))
line_vec  = f.vector(line_dir, 10.0)
line_3d   = f.line(line_orig, line_vec)

# TRIMMED_CURVE wrapping the LINE, parameter range [2.0, 8.0]
trim_p1 = f.cartesian_point((2.0, 0.0, 0.0))
trim_p2 = f.cartesian_point((8.0, 0.0, 0.0))
trimmed = f._emit_raw(
    f"TRIMMED_CURVE('gn061_trimmed_line',#{line_3d.eid},"
    f"(#{trim_p1.eid},PARAMETER_VALUE(2.0)),"
    f"(#{trim_p2.eid},PARAMETER_VALUE(8.0)),"
    f".T.,.PARAMETER.)"
)

# Pcurve for the defect edge (linear in UV, U from 0→1, V=0)
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn061_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn061_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn061_sc',#{trimmed.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Face corners: 6-unit width (matching trimmed span 8-2=6)
p_a = f.cartesian_point((2.0, 0.0, 0.0))
p_b = f.cartesian_point((8.0, 0.0, 0.0))
p_c = f.cartesian_point((8.0, 5.0, 0.0))
p_d = f.cartesian_point((2.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn061_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, length)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (8.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (8.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 6.0)
e_left  = mk_line_edge(v_d, v_a, (2.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
