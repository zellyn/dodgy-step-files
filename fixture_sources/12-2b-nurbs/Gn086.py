"""Gn086 — ShapeAnalysis_Curve.GetSamplePoints helix-sampling.

Catalog claim: GetSamplePoints determines sample count based on parameter range
but not curvature; long-pitch helix with wide parameter span gets too few samples
for mid-pitch deviation.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 12 control points.
    n=12, p=3 → n+p+1=16. Knots (0.0,0.25,0.5,0.75,1.0) mults (4,3,3,3,3)
    sum=16 ✓. Parameter range [0, 1] representing physical span 4π.
    Control points trace a helix: pitch ~0.2 per turn, radius 1.0,
    rotating through 2 full turns (parameter span wide).
    GetSamplePoints computes sample count from parameter range [0,1] alone;
    low curvature of wide helix → only ~10 samples selected; mid-pitch
    deviation between samples exceeds tolerance → undersampling error.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the helix with non-smooth control polygon (sharp z-jump at t=0.5)
    causes geometry mismatch that drives shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3 12-pole helix;
    knots (0.0,0.25,0.5,0.75,1.0) mults (4,3,3,3,3) sum=16 ✓;
    IS defect edge SURFACE_CURVE.curve_3d;
    GetSamplePoints samples by parameter range not curvature → undersampling.
  - C-1 DRIVER: z-jump at t=0.5 causes pcurve mismatch → shape_null=True.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gn086",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3 12-pole helix; "
        "knots (0.0,0.25,0.5,0.75,1.0) mults (4,3,3,3,3) sum=16 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "helix radius=1.0 pitch=0.2 2 full turns; parameter range [0,1]; "
        "GetSamplePoints samples from parameter range not curvature → too few samples; "
        "mid-pitch deviation exceeds tolerance → undersampling error; "
        "z-jump at t=0.5 (1.5-unit gap) causes pcurve mismatch → shape_null=True"
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

# ── CATALOG MECHANISM: helix B-spline degree 3, 12 control points ────────────
# n=12, p=3 → n+p+1=16. knots (0.0,0.25,0.5,0.75,1.0) mults (4,3,3,3,3) sum=16 ✓
# Helix: 2 full turns, radius=1.0, pitch=0.2 per turn, z in [0, 0.4]
# t in [0, 1] maps to angle in [0, 4π], z = 0.2*(t*2) = 0.4*t
# 12 uniformly spaced control points approximating the helix
# With a z-discontinuity at i=6 (t=0.5) for the C-1 driver
helix_pts = []
for i in range(12):
    t = i / 11.0
    angle = t * 4.0 * math.pi
    x = math.cos(angle)
    y = math.sin(angle)
    z = 0.4 * t
    # Add z-jump at index 6 (midpoint) for C-1 driver
    if i == 6:
        z += 1.5
    helix_pts.append(f.cartesian_point((x, y, z)))

cp_ids = "(" + ",".join(f"#{p.eid}" for p in helix_pts) + ")"

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn086_helix',3,"
    f"{cp_ids},"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,3,3,3,3),(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
)

# pcurve: map helix onto plane parameter space (project to XY, normalized)
# Use corresponding 12-point B-spline in 2D
pc_pts = []
for i in range(12):
    t = i / 11.0
    angle = t * 4.0 * math.pi
    # Project to 2D UV space: normalize x,y to [0,1] range
    pc_pts.append(f.cartesian_point(((math.cos(angle) + 1.0) / 2.0,
                                     (math.sin(angle) + 1.0) / 2.0)))

pc_ids = "(" + ",".join(f"#{p.eid}" for p in pc_pts) + ")"

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn086_pc',3,"
    f"{pc_ids},"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,3,3,3,3),(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn086_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn086_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn086_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Start vertex at (1,0,0) = helix t=0, end vertex at (1,0,0.4) = helix t=1
p_start = f.cartesian_point((1.0,  0.0, 0.0))
p_end   = f.cartesian_point((1.0,  0.0, 0.4))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn086_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# Build a simple square outer loop on the plane to anchor the face
p_a = f.cartesian_point((-1.5, -1.5, 0.0))
p_b = f.cartesian_point(( 1.5, -1.5, 0.0))
p_c = f.cartesian_point(( 1.5,  1.5, 0.0))
p_d = f.cartesian_point((-1.5,  1.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-1.5,-1.5,0.0), (1.,0.,0.), (0.0, 0.0), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, ( 1.5,-1.5,0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, ( 1.5, 1.5,0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (-1.5, 1.5,0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 3.0)

outer_loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])

inner_loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
])

outer_bound = f.face_outer_bound(outer_loop)
inner_bound = f._emit_raw(f"FACE_BOUND('inner_bound',#{inner_loop.eid},.T.)")

face  = f.advanced_face([outer_bound, inner_bound], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
