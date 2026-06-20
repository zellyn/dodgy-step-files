"""Gp149 — Straight-line tangent magnitude zero; complete tangent degeneracy

Catalog claim: Edge pcurve where start equals end and all derivatives
vanish. GetEndTangent2d exhausts all fallback sources (D1, D2, D3, line
endpoints) yielding zero-magnitude vector. Method returns failure indication
without reporting complete geometric collapse.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge having a PCurve where the start and
    end points are identical and all derivatives are zero everywhere.
  - THE CATALOG MECHANISM: Degree-3 B-spline 2D pcurve where ALL control
    points coincide at the same UV position (0.5, 0.5). This makes the
    entire curve a degenerate point: D1=D2=D3=0 everywhere, and
    start == end == (0.5, 0.5). When GetEndTangent2d exhausts D1, D2, D3
    cascades and falls back to the endpoint line, the line direction is
    (0,0) — zero magnitude. The method returns failure without reporting
    complete geometric collapse.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PCurve degree-3 B-spline with all 4 CPs at same
    UV point; start==end==(0.5,0.5); D1=D2=D3=0 everywhere; endpoint line
    has zero magnitude; GetEndTangent2d returns failure without reporting
    complete_tangent_degeneracy; GET_END_TANGENT_2D_B009.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp149",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-3 all 4 CPs coincident at (0.5,0.5); "
        "start==end==(0.5,0.5); D1=D2=D3=0 everywhere on the curve; "
        "GetEndTangent2d: D1=0 → D2=0 → D3=0 → endpoint line (0.5,0.5)→(0.5,0.5) "
        "= zero magnitude vector; method returns failure without reporting "
        "complete geometric collapse; complete_tangent_degeneracy GET_END_TANGENT_2D_B009; "
        "shape_null=True"
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

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('complete_tangent_degen_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve degree-3 B-spline with ALL 4 CPs coincident.
# CP[0]=CP[1]=CP[2]=CP[3]=(0.5, 0.5): entire curve is a degenerate point.
# D1=D2=D3=0 everywhere; start == end == (0.5, 0.5).
# GetEndTangent2d: D1=0 → D2=0 → D3=0 → endpoint line:
#   endpoint_A = curve(t=0) = (0.5, 0.5)
#   endpoint_B = curve(t=1) = (0.5, 0.5)
#   line direction = endpoint_B - endpoint_A = (0, 0) → zero magnitude.
# Method returns failure indication (returns False) without reporting
# complete geometric collapse. This is GET_END_TANGENT_2D_B009.
rp0 = f.cartesian_point((0.5, 0.5))   # all coincident
rp1 = f.cartesian_point((0.5, 0.5))
rp2 = f.cartesian_point((0.5, 0.5))
rp3 = f.cartesian_point((0.5, 0.5))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('complete_tangent_degen_pc',3,"
    f"(#{rp0.eid},#{rp1.eid},#{rp2.eid},#{rp3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('complete_tangent_degen_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('complete_tangent_degen_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('complete_tangent_degen_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('complete_tangent_degen_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
