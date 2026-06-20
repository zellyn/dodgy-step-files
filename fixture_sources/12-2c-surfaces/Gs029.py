"""Gs029 — Curve with last < first parameter range.

Catalog claim: A TRIMMED_CURVE or EDGE_CURVE claims [first, last] parameter
range outside the curve's natural domain or with last < first.  Translator and
downstream evaluation must normalize.

Reproducer: TRIMMED_CURVE over a unit-radius CIRCLE with
  trim_1=PARAMETER_VALUE(2π), trim_2=PARAMETER_VALUE(0), sense_agreement=.T.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry, giving the edge a surface context
    so the defect is wired into face topology.
  - Defect EDGE_CURVE: 3D curve IS a TRIMMED_CURVE wrapping a CIRCLE of radius
    1.0, with trim_1=PARAMETER_VALUE(6.2831853071795864) (=2π) and
    trim_2=PARAMETER_VALUE(0.0), sense_agreement=.T. — last < first.
  - The TRIMMED_CURVE IS the curve_3d of the SURFACE_CURVE of the defect
    EDGE_CURVE.
  - Byte assertions: contains(b'TRIMMED_CURVE('),
                     contains(b'PARAMETER_VALUE(6.2831853071795864)'),
                     contains(b'PARAMETER_VALUE(0.0)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: the defect TRIMMED_CURVE IS the curve_3d of the defect
    EDGE_CURVE's SURFACE_CURVE; trim_1=2π > trim_2=0 (last < first, reversed
    range); PLANE IS the ADVANCED_FACE.face_geometry; reversed trim drives
    shape(1) (live OCC heals) on strict heal-or-reject kernels.
"""
import math
from step_corpus.step_builder import StepFile

TWO_PI = 6.2831853071795864   # byte assertion value

f = StepFile(
    catalog_id="Gs029",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; defect EDGE_CURVE curve_3d IS "
        "TRIMMED_CURVE over CIRCLE radius=1.0 with trim_1=PARAMETER_VALUE("
        "6.2831853071795864) trim_2=PARAMETER_VALUE(0.0) sense_agreement=.T.; "
        "last < first (reversed parameter range); shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs029_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs029_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CIRCLE for the TRIMMED_CURVE ──────────────────────────────────────────────
# Unit circle centered at (0,0,0) in XY plane.
circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_z    = f.direction((0.0, 0.0, 1.0))
circ_x    = f.direction((1.0, 0.0, 0.0))
circ_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs029_cax',#{circ_orig.eid},#{circ_z.eid},#{circ_x.eid})"
)
circle = f._emit_raw(f"CIRCLE('gs029_circ',#{circ_ax.eid},1.0)")

# ── TRIMMED_CURVE with trim_1=2π, trim_2=0 (last < first) ────────────────────
# Byte assertions: PARAMETER_VALUE(6.2831853071795864) and PARAMETER_VALUE(0.0)
# TRIMMED_CURVE(name, basis_curve, trim_1, trim_2, sense_agreement, master_representation)
# trim_1 and trim_2 are SELECT (PARAMETER_VALUE or CARTESIAN_POINT) enclosed in sets.
trimmed = f._emit_raw(
    f"TRIMMED_CURVE('gs029_tc',#{circle.eid},"
    f"(PARAMETER_VALUE(6.2831853071795864)),"
    f"(PARAMETER_VALUE(0.0)),"
    f".T.,.PARAMETER.)"
)

# ── Face boundary: small square, defect edge E0 bottom uses TRIMMED_CURVE ─────
# The circle has radius 1, circumference 2π≈6.28; its chord at t=2π→0 sweeps
# the full circle but with reversed sense.  For the wire we use the trimmed curve
# as edge E0 and straight lines for E1-E3 to form a closed loop on the plane.
#
# Vertex positions: A=(1,0,0) (circle at t=0=t=2π), B=(1,0,0) same point
# since the circle closes on itself.  Use a degenerate single-vertex closed loop:
# but a STEP face boundary needs at least one EDGE_LOOP with proper topology.
# Instead: use 4 vertices on the plane and straight-line edges E0-E3, but
# replace E0's 3D curve with the TRIMMED_CURVE.  The trimmed curve (full circle)
# doesn't geometrically match the edge endpoints — that mismatch is the defect.

p_A = f.cartesian_point((1.0,  0.0, 0.0))
p_B = f.cartesian_point((5.0,  0.0, 0.0))
p_C = f.cartesian_point((5.0,  4.0, 0.0))
p_D = f.cartesian_point((1.0,  4.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: 3D curve IS the TRIMMED_CURVE (trim_1=2π > trim_2=0)
p2_e0  = f.cartesian_point((1.0, 0.0))
d2_e0  = f.direction((1.0, 0.0))
v2_e0  = f.vector(d2_e0, 4.0)
l2_e0  = f.line(p2_e0, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{plane.eid},#{pcd_e0.eid})")
sc_e0  = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{trimmed.eid},(#{pc_e0.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e1 = mk_edge_line(v_B, v_C,
    (5.0, 0.0, 0.0), (0.0, 1.0, 0.0), 4.0,
    (5.0, 0.0),      (0.0, 1.0),       4.0)
e2 = mk_edge_line(v_C, v_D,
    (5.0, 4.0, 0.0), (-1.0, 0.0, 0.0), 4.0,
    (5.0, 4.0),      (-1.0, 0.0),       4.0)
e3 = mk_edge_line(v_D, v_A,
    (1.0, 4.0, 0.0), (0.0, -1.0, 0.0), 4.0,
    (1.0, 4.0),      (0.0, -1.0),       4.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; defect TRIMMED_CURVE IS the defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
