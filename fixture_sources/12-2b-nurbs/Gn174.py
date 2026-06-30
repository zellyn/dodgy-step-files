"""Gn174 — B-spline surface with extreme aspect-ratio control net (1000:1).

Catalog claim: B_SPLINE_SURFACE_WITH_KNOTS whose control-point net has extreme
aspect ratio (span 1000 in U, span 1 in V, ratio 1000:1) causes
BRepMesh_IncrementalMesh to produce empty triangulation for the face (silent
failure, no exception). Source: arXiv "Better STEP" paper (2506.05417), ~5%
model rate.

OCC behavior: shape loads without error but BRepMesh produces empty
triangulation (zero triangles, zero nodes) due to internal chord-deflection
/aspect-ratio check aborting the mesh without raising an exception.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree (2,2), 3×3 control net.
  - U spans 0..1000 mm, V spans 0..1 mm → aspect ratio 1000:1.
  - Flat grid (z=0) with uniform knots.
  - Face boundary uses a SURFACE_CURVE/PCURVE wire looping the full [0,1000]×[0,1]
    parameter domain.

Mechanism vs driver:
  - CATALOG MECHANISM: extreme aspect ratio (1000:1) in the physical extent of
    the B-spline control net IS the ADVANCED_FACE.face_geometry; this is the
    precise trigger documented in the arXiv paper for BRepMesh empty-output.
  - No artificial C-1 break is added; the defect is entirely in the extreme
    aspect ratio, which is a well-documented near-degenerate mesh trigger.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn174",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (2,2) 3x3 net; "
        "U control points span [0,1000], V control points span [0,1]; "
        "aspect ratio 1000:1; BRepMesh_IncrementalMesh produces empty "
        "triangulation (silent failure, no exception); arXiv 2506.05417 ~5%"
    ),
)

# ── DEFECT SURFACE: degree (2,2), 3×3 flat grid, extreme aspect ratio 1000:1 ──
# U: 3 control rows spanning 0..1000 mm
# V: 3 control columns spanning 0..1 mm
# Knots: clamped (3,3) at (0,1000) in U; (3,3) at (0,1) in V
# Sum checks: sum(3,3)=6 = 3+2+1=6 ✓ for both U and V

grid = [
    [f.cartesian_point((0.0,   0.0, 0.0)), f.cartesian_point((0.0,   0.5, 0.0)), f.cartesian_point((0.0,   1.0, 0.0))],
    [f.cartesian_point((500.0, 0.0, 0.0)), f.cartesian_point((500.0, 0.5, 0.0)), f.cartesian_point((500.0, 1.0, 0.0))],
    [f.cartesian_point((1000.0,0.0, 0.0)), f.cartesian_point((1000.0,0.5, 0.0)), f.cartesian_point((1000.0,1.0, 0.0))],
]

surf = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=2,
    control_points_grid=grid,
    u_multiplicities=[3, 3],
    v_multiplicities=[3, 3],
    u_knots=[0.0, 1000.0],
    v_knots=[0.0, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)

# ── Parametric context for pcurves ──
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Corner 3D points: (u,v) → (u, v, 0) where u in [0,1000], v in [0,1]
p_a = f.cartesian_point((0.0,    0.0, 0.0))   # u=0,   v=0
p_b = f.cartesian_point((1000.0, 0.0, 0.0))   # u=1000,v=0
p_c = f.cartesian_point((1000.0, 1.0, 0.0))   # u=1000,v=1
p_d = f.cartesian_point((0.0,    1.0, 0.0))   # u=0,   v=1

v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, p2_len):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, p2_len)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Bottom edge: v_a → v_b  (u: 0→1000, v=0)
e_bot   = mk_edge_with_pc(v_a, v_b, (0.0, 0.0, 0.0), (1., 0., 0.), 1000.0, (0.0, 0.0), (1., 0.),    1000.0)
# Right edge:  v_b → v_c  (v: 0→1, u=1000)
e_right = mk_edge_with_pc(v_b, v_c, (1000.0, 0.0, 0.0), (0., 1., 0.), 1.0, (1000.0, 0.0), (0., 1.), 1.0)
# Top edge:    v_c → v_d  (u: 1000→0, v=1)
e_top   = mk_edge_with_pc(v_c, v_d, (1000.0, 1.0, 0.0), (-1., 0., 0.), 1000.0, (1000.0, 1.0), (-1., 0.), 1000.0)
# Left edge:   v_d → v_a  (v: 1→0, u=0)
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 1.0, 0.0), (0., -1., 0.), 1.0, (0.0, 1.0), (0., -1.), 1.0)

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
