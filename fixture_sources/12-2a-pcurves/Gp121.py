"""Gp121 — ShapeAnalysis_Edge.CheckCurve3dWithPCurve OFFSET_CURVE.

Catalog claim: Edge with 3D OFFSET_CURVE wrapping a line. CheckCurve3dWithPCurve
samples but offset application uses base-curve normal, ignoring offset distance.
OCC reconciles offset with 3D curve and heals.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - THE CATALOG MECHANISM: The pcurve is an OFFSET_CURVE_2D wrapping a base
    LINE in UV. The OFFSET_CURVE_2D shifts the base line by an offset distance
    (0.3 units) perpendicular to the line direction. CheckCurve3dWithPCurve
    evaluates the pcurve (the offset curve) and compares sample points to the
    3D curve. The offset application uses the base-curve normal direction, but
    ignores that the 3D edge itself may not be offset-corrected — the checker
    sees an apparent mismatch (the pcurve is shifted perpendicular to the 3D
    line) but silently passes because OCC reconciles the offset geometry.
    OCC heals to shape(1)/shape(1).
  - 3D curve: a clean LINE from (0,0,0) to (4,0,0). Geometry is valid.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve is OFFSET_CURVE_2D wrapping a LINE, offset=0.3;
    CheckCurve3dWithPCurve offset-normal ignores offset distance; OCC heals.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp121",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D LINE (0,0,0)→(4,0,0); "
        "PCurve: OFFSET_CURVE_2D wrapping LINE UV (0,0.3) direction (1,0) "
        "offset_distance=0.3 (shifted 0.3 units in +v from base LINE at v=0); "
        "CheckCurve3dWithPCurve samples OFFSET_CURVE_2D — offset application "
        "uses base-curve normal, ignores offset distance; apparent 3D/2D mismatch "
        "silently passes; OCC reconciles offset; shape(1)/shape(1)"
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

# Face corners: rectangle [0,4] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) with proper pcurves
def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 2.0, 0.0), (-1., 0., 0.), 4.0, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# 3D curve: clean LINE from (0,0,0) to (4,0,0)
line_p  = f.cartesian_point((0.0, 0.0, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 4.0)
line_3d = f.line(line_p, line_v)

# THE CATALOG MECHANISM: PCurve is OFFSET_CURVE_2D wrapping a base LINE.
# Base LINE in UV: origin at (0.0, 0.0), direction (1,0), length 4.0.
# OFFSET_CURVE_2D: offset distance = 0.3 in +v direction (perpendicular to LINE).
# The offset shifts the base line from v=0 to v=0.3 in UV space.
# CheckCurve3dWithPCurve samples the OFFSET_CURVE_2D and compares to the 3D LINE.
# The 3D LINE lies at v=0 (z=0 plane, x-direction); the pcurve offset curve
# is at v=0.3 in UV. The checker's offset application uses the base-curve
# normal but ignores the actual offset distance when validating the 3D/2D gap.
# OCC reconciles this discrepancy and heals to shape(1)/shape(1).
base_pt   = f.cartesian_point((0.0, 0.0))
base_dir  = f.direction((1.0, 0.0))
base_vec  = f.vector(base_dir, 4.0)
base_line = f.line(base_pt, base_vec)

# OFFSET_CURVE_2D: wraps the base LINE, offset distance 0.3
# OFFSET_CURVE_2D(name, basis_curve, distance, self_intersect)
offset_pc = f._emit_raw(
    f"OFFSET_CURVE_2D('offset_pcurve',#{base_line.eid},0.3,.F.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('offset_pc_def',(#{offset_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('offset_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('offset_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('offset_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
