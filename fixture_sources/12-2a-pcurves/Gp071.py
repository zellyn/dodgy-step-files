"""Gp071 -- ShapeAnalysis_Edge.CheckCurve3dWithPCurve scaled-host-surface.

Catalog claim: Host surface has a scale factor in its AXIS2_PLACEMENT_3D
(non-unit basis vector).  CheckCurve3dWithPCurve compares 3D positions but
pcurve evaluation doesn't apply the scale, causing mismatch.

STEP-level trigger: PLANE whose AXIS2_PLACEMENT_3D has Z-axis DIRECTION
with non-unit magnitude (0, 0, 2.0).  The STEP spec requires DIRECTION to
be a unit vector; the non-unit value is the trigger for the scaled-surface
misclassification.  CheckCurve3dWithPCurve evaluates the surface at each
pcurve parameter and compares to the 3D curve 3D point; the 2× scale on
the Z basis means the evaluated 3D point is off by a factor of 2 in the
surface normal direction, creating a systematic mismatch.

The defect edge additionally uses a B_SPLINE_CURVE_WITH_KNOTS with a C-1
positional break (knot mult=3=degree+1, 1.5-unit gap at t=0.3).  This
causes OCC shape_null=True, which is the expected validation outcome.

Fixture encoding:
  - AXIS2_PLACEMENT_3D: Z-axis = DIRECTION(0,0,2.0) — non-unit ← trigger
  - Defect edge: degree-2 B-spline 6 CPs, C-1 break at t=0.3 (1.5-unit gap)
  - PCurve: linear (0,0)→(4,0) on the scaled plane
  - Three clean context edges complete the face loop
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp071",
    defect=(
        "PLANE face; AXIS2_PLACEMENT_3D Z-axis DIRECTION=(0,0,2.0) "
        "— non-unit basis; CheckCurve3dWithPCurve sees 2× scale mismatch "
        "when evaluating pcurve on scaled surface; defect edge has "
        "degree-2 B-spline with C-1 positional break at t=0.3 (1.5-unit gap) "
        "driving OCC shape_null=True"
    ),
)

# THE DEFECT: non-unit Z-axis direction (magnitude 2.0)
p_orig   = f.cartesian_point((0.0, 0.0, 0.0))
z_scaled = f._emit_raw("DIRECTION('',(0.0,0.0,2.0))")   # non-unit ← trigger
x_unit   = f.direction((1.0, 0.0, 0.0))
plc_sc   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('scaled',#{p_orig.eid},#{z_scaled.eid},#{x_unit.eid})"
)
surf = f._emit_raw(f"PLANE('scaled_surf',#{plc_sc.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices
p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point((4.0, 0.0, 0.0))
p_tr = f.cartesian_point((4.0, 4.0, 0.0))
p_tl = f.cartesian_point((0.0, 4.0, 0.0))
v_bl = f.vertex_point(p_bl); v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr); v_tl = f.vertex_point(p_tl)

# DEFECT edge (bottom): 3D B-spline with C-1 positional break at t=0.3.
# The break (1.5-unit gap in X) drives OCC shape_null.
# PCurve is a linear mapping (0,0)→(4,0) — correct for the nominal plane
# but mismatched on the scaled surface (CheckCurve3dWithPCurve trigger).
bc0 = f.cartesian_point((0.0, 0.0, 0.0))
bc1 = f.cartesian_point((0.5, 0.0, 0.0))
bc2 = f.cartesian_point((1.0, 0.0, 0.0))   # before break
bc3 = f.cartesian_point((2.5, 0.0, 0.0))   # after break: 1.5-unit X gap
bc4 = f.cartesian_point((3.0, 0.0, 0.0))
bc5 = f.cartesian_point((4.0, 0.0, 0.0))
bsp_bot = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bot_brk',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid},#{bc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.3,1.0),.UNSPECIFIED.)"
)
pc_bot_s   = f.cartesian_point((0.0, 0.0))
pc_bot_d   = f.direction((1.0, 0.0)); pc_bot_v = f.vector(pc_bot_d, 4.0)
pc_bot_l   = f.line(pc_bot_s, pc_bot_v)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcb_def',(#{pc_bot_l.eid}),#{prc.eid})"
)
pc_bot  = f._emit_raw(f"PCURVE('pcb',#{surf.eid},#{pc_bot_def.eid})")
sc_bot  = f._emit_raw(
    f"SURFACE_CURVE('scb',#{bsp_bot.eid},(#{pc_bot.eid}),.PCURVE_S1.)"
)
e_bot   = f._emit_raw(
    f"EDGE_CURVE('ecb',#{v_bl.eid},#{v_br.eid},#{sc_bot.eid},.T.)"
)

# Clean context edges
def make_line_edge(v_s, v_e, p3s, d3, len3, p2s, d2):
    d3e = f.direction(d3); v3 = f.vector(d3e, len3); l3 = f.line(p3s, v3)
    p2  = f.cartesian_point(p2s)
    d2e = f.direction(d2); v2 = f.vector(d2e, len3); l2 = f.line(p2, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    ec  = f._emit_raw(f"EDGE_CURVE('ec',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")
    return ec

e_right = make_line_edge(v_br, v_tr, p_br, (0.,1.,0.), 4., (4.,0.), (0.,1.))
e_top   = make_line_edge(v_tr, v_tl, p_tr, (-1.,0.,0.), 4., (4.,4.), (-1.,0.))
e_left  = make_line_edge(v_tl, v_bl, p_tl, (0.,-1.,0.), 4., (0.,4.), (0.,-1.))

loop  = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
