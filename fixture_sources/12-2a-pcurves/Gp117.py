"""Gp117 — Closed pcurve, open 3D curve mismatch.

Catalog claim: ShapeFix_Edge.FixAddCurve3d constructs wrong 3D curve when
pcurve is closed circle but edge is open. Closure doesn't match edge vertices.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - THE CATALOG MECHANISM: The pcurve is a B_SPLINE_CURVE_WITH_KNOTS degree-2
    with CP[0]==CP[N] (closed loop: first and last CPs coincide). The 3D curve
    is an open LINE running from one vertex to another. The pcurve closure
    implies the edge should return to its start in UV space, but the 3D LINE is
    open — its endpoints are distinct. FixAddCurve3d constructs a 3D curve from
    the pcurve but the closure flag mismatch means the constructed 3D curve
    doesn't agree with the actual edge vertices. OCC tolerates this mismatch
    and heals to shape(1)/shape(1).
  - 3D curve: a clean LINE from (0,0,0) to (4,0,0). Geometry is valid.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve B-spline CP[0]==CP[N] (closed form) but 3D curve
    is open LINE; FixAddCurve3d closure mismatch; OCC heals silently.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp117",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D LINE (0,0,0)→(4,0,0) — open; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2 5 CPs closed_curve=.T. with "
        "CP[0]=(0,0)==CP[4]=(0,0) (closed loop in UV); "
        "pcurve closure flag .T. contradicts open 3D LINE; "
        "FixAddCurve3d constructs wrong 3D curve from closed pcurve; "
        "OCC tolerates closure mismatch; shape(1)/shape(1)"
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

# 3D curve: open LINE from (0,0,0) to (4,0,0)
line_p  = f.cartesian_point((0.0, 0.0, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 4.0)
line_3d = f.line(line_p, line_v)

# THE CATALOG MECHANISM: PCurve B-spline degree-2 with closed_curve=.T.
# CP[0] == CP[4] = (0.0, 0.0) — the loop closes back to UV origin.
# The loop goes out to (4,0) and returns, but the flag claims it's closed.
# This contradicts the open 3D LINE whose endpoints are (0,0,0) and (4,0,0).
# FixAddCurve3d attempts to build a 3D curve from this closed pcurve but
# gets a closed geometry that doesn't match the distinct edge vertices.
# OCC tolerates this and heals to shape(1)/shape(1).
pp0 = f.cartesian_point((0.0, 0.0))   # start == end (closed)
pp1 = f.cartesian_point((2.0, 0.0))   # midpoint: (2,0) in UV
pp2 = f.cartesian_point((4.0, 0.0))   # furthest reach in UV
pp3 = f.cartesian_point((2.0, 0.0))   # return path — mirrors pp1
pp4 = f.cartesian_point((0.0, 0.0))   # end == start (closed loop)

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('closed_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid}),"
    f".UNSPECIFIED.,.T.,.F.,"
    f"(3,1,1,3),(0.0,0.25,0.75,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('closed_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('closed_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('closed_open_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('closed_open_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
