"""Gn081 — ShapeAnalysis_Curve.GetSamplePoints CIRCLE scale-insensitive cap.

Catalog claim: GetSamplePoints for CIRCLE samples scale-insensitively.
Full-circle CIRCLE (radius 0.001mm) samples with fixed 360-point cap regardless
of scale, producing 1µm spacing for 1µm radius curve (exceeds 1e-7 tolerance).

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - CIRCLE with radius 0.001 (1µm). Full parametric range [0, 2π].
    GetSamplePoints uses a hardcoded cap of 360 samples; for radius=0.001mm
    the arc length per sample = 2π×0.001/360 ≈ 1.75e-5mm, but the per-sample
    chord error at that scale exceeds 1e-7mm tolerance threshold.
    The scale-insensitive cap means that micro-scale circles are over-sampled
    relative to chord error budget — chord deviation h = r(1-cos(π/180)) ≈
    0.001×1.5e-4 ≈ 1.5e-7, just above the 1e-7 cut-off.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the micro-scale CIRCLE on a normal-scale plane causes
    geometric mismatch (scale ratio 1000:1) that drives shape_null=True
    via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: CIRCLE radius=0.001mm; IS defect edge SURFACE_CURVE.curve_3d;
    GetSamplePoints fixed 360-cap produces chord error 1.5e-7 > 1e-7 tolerance —
    scale-insensitive sampling fails for micro-scale curves.
  - C-1 DRIVER: micro-circle on unit-scale plane drives scale mismatch → shape_null=True.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gn081",
    defect=(
        "CIRCLE radius=0.001mm; "
        "full range [0,2π]; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints fixed 360-point cap → chord error 1.5e-7 > 1e-7 tolerance; "
        "scale-insensitive sampling fails for micro-scale CIRCLE; "
        "micro-circle on unit-scale plane drives scale mismatch → shape_null=True"
    ),
)

# ── Flat plane for the face ───────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: CIRCLE radius=0.001mm, center at (0.5, 0.5, 0) ────────
# Axis placement for the circle
c_orig = f.cartesian_point((0.5, 0.5, 0.0))   # center on face
c_norm = f.direction((0.0, 0.0, 1.0))
c_xdir = f.direction((1.0, 0.0, 0.0))
c_ax3  = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('c_ax3',#{c_orig.eid},#{c_norm.eid},#{c_xdir.eid})"
)
# CIRCLE radius=0.001 (1µm)
mech_3d = f._emit_raw(f"CIRCLE('gn081_micro_circle',#{c_ax3.eid},0.001)")

# pcurve: full circle in 2D — use a CIRCLE in 2D parametric space
# For simplicity use a degenerate line pcurve (the mismatch IS the defect)
c2_orig = f.cartesian_point((0.5, 0.5))
c2_xdir = f.direction((1.0, 0.0))
c2_ax2  = f._emit_raw(f"AXIS2_PLACEMENT_2D('c2_ax2',#{c2_orig.eid},#{c2_xdir.eid})")
pc_circle = f._emit_raw(f"CIRCLE('gn081_pc_circle',#{c2_ax2.eid},0.001)")
pcd = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn081_pcdef',(#{pc_circle.eid}),#{prc.eid})"
)
pc  = f._emit_raw(f"PCURVE('gn081_pc',#{plane.eid},#{pcd.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn081_sc',#{mech_3d.eid},(#{pc.eid}),.PCURVE_S1.)"
)

# For a closed circle edge, start==end vertex at (0.501, 0.5, 0)
# (center + radius along X, at the seam)
p_seam = f.cartesian_point((0.501, 0.5, 0.0))
v_seam = f.vertex_point(p_seam)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn081_defect_edge',#{v_seam.eid},#{v_seam.eid},#{sc_defect.eid},.T.)"
)

# The face is a square [0,1]×[0,1] with the micro-circle hole inside.
# For simplicity, build the outer loop as 4 line edges (no inner loop).
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 1.0, 0.0))
p_d = f.cartesian_point((0.0, 1.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_bot   = mk_line_edge(v_a, v_b, (0.0, 0.0, 0.0), (1.,0.,0.), (0.0, 0.0), (1.,0.), 1.0)
e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 1.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 1.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 1.0)

outer_loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])

# Inner loop: the micro-circle edge (defect)
inner_loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
])

outer_bound = f.face_outer_bound(outer_loop)
inner_bound = f._emit_raw(f"FACE_BOUND('inner_bound',#{inner_loop.eid},.T.)")

face  = f.advanced_face([outer_bound, inner_bound], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
