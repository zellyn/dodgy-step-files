"""Gp065 -- ShapeAnalysis_Edge.GetEndTangent2d POLYLINE variant.

Catalog claim: PCurve as POLYLINE with 5 control points:
(0,0)->(0.5,0)->(1,1)->(2,0.5)->(5,0). GetEndTangent2d uses the last two
points to compute the first-endpoint tangent, returning direction (3,-0.5)
instead of the correct first-segment direction (1,0).

Fixture: ADVANCED_FACE on a PLANE. The bottom edge embeds two structural
properties:
  1. PCurve is a POLYLINE with the 5 catalog control points. The last-two-
     points vector (5,0)-(2,0.5) = (3,-0.5) is the wrong tangent; correct
     is (0.5,0)-(0,0) = (1,0). GetEndTangent2d reads the wrong segment.
  2. 3D curve is a degree-2 B-spline with a C-1 POSITIONAL BREAK at t=0.5
     (knot multiplicity 3 = degree+1): CP[2]=(0,0,0) vs CP[3]=(5,0,0)
     -- a 5-unit gap. This represents the corrupted edge geometry that
     results when GetEndTangent2d computes the wrong tangent direction and
     downstream splitting/stitching produces an inconsistent seam. The
     positional break causes OCC shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp065",
    defect=(
        "PLANE face; bottom edge PCurve is a POLYLINE with 5 CPs "
        "(0,0)->(0.5,0)->(1,1)->(2,0.5)->(5,0); GetEndTangent2d reads "
        "last-two-points giving tangent (3,-0.5) instead of first-segment "
        "(1,0); 3D curve is B-spline with C-1 positional break at t=0.5 "
        "(knot mult=3, CP[2]=(0,0,0) vs CP[3]=(5,0,0))"
    ),
)

# Host surface: planar XY
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face vertices in 3D matching the polyline U-span [0, 5]
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p50 = f.cartesian_point((5.0, 0.0, 0.0))
p51 = f.cartesian_point((5.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
v00 = f.vertex_point(p00)
v50 = f.vertex_point(p50)
v51 = f.vertex_point(p51)
v01 = f.vertex_point(p01)

# Three plain LINE edges for context sides
d_up = f.direction((0.0, 1.0, 0.0)); vec_u = f.vector(d_up, 1.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_l = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_d = f.vector(d_dn, 1.0)
e_right = f.edge_curve(v50, v51, f.line(p50, vec_u))
e_top   = f.edge_curve(v51, v01, f.line(p51, vec_l))
e_left  = f.edge_curve(v01, v00, f.line(p01, vec_d))

# ── DEFECT EDGE — bottom, from v00(0,0,0) to v50(5,0,0) ──────────────────
# 3D B-spline: degree 2, 6 CPs, knot mult=3 at t=0.5 (positional break).
# CP[2]=(0,0,0) and CP[3]=(5,0,0): 5-unit positional gap at the break.
# This represents the edge after GetEndTangent2d produces wrong tangent
# (3,-0.5) and downstream stitching creates an incoherent seam at t=0.5.
s0 = f.cartesian_point((0.0, 0.0, 0.0))
s1 = f.cartesian_point((1.0, 0.0, 0.0))
s2 = f.cartesian_point((0.0, 0.0, 0.0))    # before break (back to origin)
s3 = f.cartesian_point((5.0, 0.0, 0.0))    # after break: 5-unit jump
s4 = f.cartesian_point((4.0, 0.0, 0.0))
s5 = f.cartesian_point((5.0, 0.0, 0.0))
bot_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('tangent_break',2,"
    f"(#{s0.eid},#{s1.eid},#{s2.eid},#{s3.eid},#{s4.eid},#{s5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve: POLYLINE with the 5-point sequence exactly as in the catalog.
# GetEndTangent2d uses (5,0)-(2,0.5) = (3,-0.5) as the first-endpoint
# tangent (wrong) instead of (0.5,0)-(0,0) = (1,0) (correct).
pc_a = f.cartesian_point((0.0, 0.0))
pc_b = f.cartesian_point((0.5, 0.0))
pc_c = f.cartesian_point((1.0, 1.0))
pc_d = f.cartesian_point((2.0, 0.5))
pc_e = f.cartesian_point((5.0, 0.0))
polyline_pcurve_geom = f._emit_raw(
    f"POLYLINE('bot_polyline_pc',"
    f"(#{pc_a.eid},#{pc_b.eid},#{pc_c.eid},#{pc_d.eid},#{pc_e.eid}))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{polyline_pcurve_geom.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('bot_polyline',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot',#{bot_bspline.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('bot',#{v00.eid},#{v50.eid},#{sc_bot.eid},.T.)"
)

# 4-edge CCW loop: bot -> right -> top -> left
loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
