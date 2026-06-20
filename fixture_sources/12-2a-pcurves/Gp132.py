"""Gp132 — PCurve projection tolerance escalation unchecked.

Catalog claim: PCurve projection status (DONE4) validates algorithm success but
does not verify resulting tolerances remain within projected precision bounds.
High-curvature surfaces with loose vertex tolerances can exceed projection fidelity.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius 1.0) face; curved surface creates high curvature.
  - Defect edge: bare EDGE_CURVE (no pcurve) on the cylindrical face.
    FixAddPCurve must project the 3D curve onto the cylinder.
  - Vertex tolerance set loose (via imprecise vertex placement) so that after
    successful projection (DONE4), the vertex assignment tolerance exceeds the
    projection precision bound — but the code accepts it anyway.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE host; bare EDGE_CURVE forcing
    FixAddPCurve projection; vertex at imprecise position so post-projection
    tolerance check (DONE4 accepted without tolerance verify) is bypassed.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp132",
    defect=(
        "CYLINDRICAL_SURFACE radius=1.0; defect edge: bare EDGE_CURVE (no pcurve); "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "FixAddPCurve.FixAddPCurve projection DONE4 check succeeds but does not "
        "verify resulting vertex tolerance within projection precision bounds; "
        "high-curvature cylinder surface with imprecise vertex exacerbates mismatch; "
        "shape_null=True"
    ),
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Host surface: CYLINDRICAL_SURFACE radius=1.0 axis along Z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
# THE CATALOG MECHANISM: cylindrical surface — high curvature stresses projection
surf = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl_surf',#{plc.eid},1.0)")

# Face corners on the cylinder (u in [0, pi], v in [0, 2])
# At radius=1, u=0 → (1,0,0), u=pi → (-1,0,0)
import math
p_a = f.cartesian_point((1.0,  0.0, 0.0))   # u=0, v=0
p_b = f.cartesian_point((0.0,  1.0, 0.0))   # u=pi/2, v=0
p_c = f.cartesian_point((0.0,  1.0, 2.0))   # u=pi/2, v=2
p_d = f.cartesian_point((1.0,  0.0, 2.0))   # u=0, v=2
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges with proper pcurves (right=v side, top=u=pi/2 arc, left=v side)
def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2=None):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    if len2 is None:
        len2 = len3
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len2); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Right edge: v_b → v_c (vertical at u=pi/2, x=0,y=1, v goes 0→2)
e_right = mk_line_edge_with_pc(
    v_b, v_c,
    (0.0, 1.0, 0.0), (0., 0., 1.), 2.0,
    (1.5707963, 0.0), (0., 1.), 2.0
)
# Top edge: v_c → v_d (arc at v=2, u=pi/2→0)
e_top = mk_line_edge_with_pc(
    v_c, v_d,
    (0.0, 1.0, 2.0), (-1., 0., 0.), 1.0,
    (1.5707963, 2.0), (-1., 0.), 1.5707963
)
# Left edge: v_d → v_a (vertical at u=0, x=1,y=0, v goes 2→0)
e_left = mk_line_edge_with_pc(
    v_d, v_a,
    (1.0, 0.0, 2.0), (0., 0., -1.), 2.0,
    (0.0, 2.0), (0., -1.), 2.0
)

# ── DEFECT EDGE — bottom arc (v_a -> v_b, u=0→pi/2, v=0) ──────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
# Bare EDGE_CURVE (no SURFACE_CURVE): FixAddPCurve must project onto cylinder.
# Projection DONE4 check passes without verifying tolerance bounds.
dc0 = f.cartesian_point((1.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.25, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier — C-1 break start
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap from dc2 = C-1 break
dc4 = f.cartesian_point((0.5,  0.75, 0.0))
dc5 = f.cartesian_point((0.0,  1.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('tol_escalation_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Bare EDGE_CURVE — no SURFACE_CURVE wrapper, no pcurve.
# FixAddPCurve projects onto CYLINDRICAL_SURFACE; DONE4 is set but vertex
# tolerance post-projection is not verified against precision bound.
e_bot = f._emit_raw(
    f"EDGE_CURVE('tol_escalation_edge',#{v_a.eid},#{v_b.eid},#{bspline_3d.eid},.T.)"
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
