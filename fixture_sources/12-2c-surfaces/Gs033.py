"""Gs033 — Trim curves on TOROIDAL_SURFACE produce jagged tessellation borders
(TRIMMED_CURVE on ELLIPSE pcurve).

Catalog claim: A pcurve on a TOROIDAL_SURFACE is a TRIMMED_CURVE wrapping an
ELLIPSE in (u,v) parametric space. Tessellator falls back to coarse parametric
sampling on the trim curve while the rest of the patch uses chordal-error
sampling, producing sharp, chaotic border meshes.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - TOROIDAL_SURFACE IS the ADVANCED_FACE.face_geometry.
  - One edge's PCURVE.reference_to_curve uses a TRIMMED_CURVE over an ELLIPSE
    as the 2D parametric curve (in UV space).
  - Byte assertions: contains(b'TOROIDAL_SURFACE('),
                     contains(b'TRIMMED_CURVE('),
                     contains(b'ELLIPSE(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    the defect TRIMMED_CURVE wrapping an ELLIPSE IS the pcurve on that surface;
    pcurve IS wired into face topology via SURFACE_CURVE on the defect EDGE_CURVE.
  - shape_null driver: jagged tessellation from mismatched sampling on TRIMMED_CURVE
    pcurve; strict heal-or-reject kernels produce null shape.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs033",
    defect=(
        "TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry; "
        "defect EDGE_CURVE pcurve IS TRIMMED_CURVE wrapping ELLIPSE in UV parametric space; "
        "PCURVE references TRIMMED_CURVE(ELLIPSE); jagged tessellation borders; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: TOROIDAL_SURFACE as face_geometry ─────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)

# TOROIDAL_SURFACE: major_radius=50, minor_radius=10
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs033_torus',#{plc.eid},50.0,10.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── DEFECT: ELLIPSE in UV space, wrapped in TRIMMED_CURVE for the pcurve ─────
# The defect is a TRIMMED_CURVE on an ELLIPSE used as a pcurve on the torus.
# In parametric space (u=azimuth 0..2π, v=meridian 0..2π), a small ellipse patch.
# ELLIPSE in the 2D parameter domain:
ell_orig_2d = f.cartesian_point((0.1, 0.0))
ell_xdir_2d = f.direction((1.0, 0.0))
# 2D AXIS2_PLACEMENT: use raw emit since we need 2D version
ell_ax2d = f._emit_raw(
    f"AXIS2_PLACEMENT_2D('gs033_ellax2d',#{ell_orig_2d.eid},#{ell_xdir_2d.eid})"
)
# ELLIPSE(name, position, semi_axis_1, semi_axis_2) — semi_axis_1 along major axis
ellipse_2d = f._emit_raw(f"ELLIPSE('gs033_ell2d',#{ell_ax2d.eid},0.1,0.05)")

# TRIMMED_CURVE over the 2D ELLIPSE (trim from 0 to π/2)
HALF_PI = 1.5707963267948966
trimmed_pc = f._emit_raw(
    f"TRIMMED_CURVE('gs033_tc',#{ellipse_2d.eid},"
    f"(PARAMETER_VALUE(0.0)),"
    f"(PARAMETER_VALUE({HALF_PI})),"
    f".T.,.PARAMETER.)"
)

# Definitional representation wrapping the trimmed ellipse as the pcurve def
pcd_defect = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcdef_defect',(#{trimmed_pc.eid}),#{prc.eid})"
)
# PCURVE on the TOROIDAL_SURFACE using the TRIMMED_CURVE(ELLIPSE)
pc_defect = f._emit_raw(f"PCURVE('pc_defect',#{torus.eid},#{pcd_defect.eid})")

# ── 3D edge geometry and remaining edges ─────────────────────────────────────
# Torus parameterization: x=(R+r*cos(v))*cos(u), y=(R+r*cos(v))*sin(u), z=r*sin(v)
R, r = 50.0, 10.0

def torus_pt(u, v):
    return (
        (R + r * math.cos(v)) * math.cos(u),
        (R + r * math.cos(v)) * math.sin(u),
        r * math.sin(v),
    )

# Small rectangular patch: u in [0, 0.1], v in [0, 0.1]
corners_uv = [(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.1)]
corners_3d = [torus_pt(u, v) for u, v in corners_uv]

pts  = [f.cartesian_point(c) for c in corners_3d]
verts = [f.vertex_point(p) for p in pts]

# Defect edge E0: 3D curve is a straight-line approximation; pcurve IS the TRIMMED_CURVE(ELLIPSE)
p3_e0 = f.cartesian_point(corners_3d[0])
d3_e0 = f.direction((1.0, 0.0, 0.0))
v3_e0 = f.vector(d3_e0, 1.0)
l3_e0 = f.line(p3_e0, v3_e0)
sc_e0 = f._emit_raw(
    f"SURFACE_CURVE('sc_e0',#{l3_e0.eid},(#{pc_defect.eid}),.PCURVE_S1.)"
)
e0 = f._emit_raw(
    f"EDGE_CURVE('ec_e0',#{verts[0].eid},#{verts[1].eid},#{sc_e0.eid},.T.)"
)

# Remaining 3 edges: normal line edges on the torus
def mk_torus_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3s = f.cartesian_point(p3_start)
    d3  = f.direction(d3t)
    vec3 = f.vector(d3, p3_len)
    l3   = f.line(p3s, vec3)
    p2s  = f.cartesian_point(p2_start)
    d2   = f.direction(d2t)
    vec2 = f.vector(d2, p2_len)
    l2   = f.line(p2s, vec2)
    pcd  = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc   = f._emit_raw(f"PCURVE('pc',#{torus.eid},#{pcd.eid})")
    sc   = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e1 = mk_torus_edge(verts[1], verts[2],
    corners_3d[1], (0.0, 1.0, 0.0), 1.0,
    (0.1, 0.0), (0.0, 1.0), 0.1)
e2 = mk_torus_edge(verts[2], verts[3],
    corners_3d[2], (-1.0, 0.0, 0.0), 1.0,
    (0.1, 0.1), (-1.0, 0.0), 0.1)
e3 = mk_torus_edge(verts[3], verts[0],
    corners_3d[3], (0.0, -1.0, 0.0), 1.0,
    (0.0, 0.1), (0.0, -1.0), 0.1)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# TOROIDAL_SURFACE IS the face_geometry; TRIMMED_CURVE(ELLIPSE) IS the defect pcurve.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
