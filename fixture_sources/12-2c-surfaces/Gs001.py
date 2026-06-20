"""Gs001 — TOROIDAL_SURFACE with negative MajorRadius (SolidWorks/Pro-E orientation marker).

Catalog claim: Some vendors encode reversed face orientation by emitting a
TOROIDAL_SURFACE with negative major_radius (here major=-50.0, minor=10.0).
Translators that take the radius at face value compute the wrong geometry;
translators checking only sign produce partially wrong shapes.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE('',axis2, -50.0, 10.0) IS the ADVANCED_FACE.face_geometry.
    Negative major_radius (-50) encodes an orientation flip.
  - A small rectangular wire on the torus (parametric corners computed with
    |major|=50, minor=10) is used as the face boundary — the torus IS the
    surface topology is wired to.
  - Byte assertions: contains(b'TOROIDAL_SURFACE('), contains(b'-50.0,10.0').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE with negative major_radius IS the
    ADVANCED_FACE.face_geometry; negative radius forces degenerate evaluation.
  - shape_null driver: negative-radius torus produces null shape under strict
    kernel that enforces heal-or-reject.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs001",
    defect=(
        "TOROIDAL_SURFACE major_radius=-50.0 minor_radius=10.0 IS "
        "ADVANCED_FACE.face_geometry; negative major_radius encodes "
        "SolidWorks/Pro-E orientation flip; degenerate torus evaluation; "
        "shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: TOROIDAL_SURFACE with negative major_radius ────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)

# Negative major_radius = -50.0 IS the defect; minor=10.0 (byte assertion -50.0,10.0)
torus = f._emit_raw(f"TOROIDAL_SURFACE('gs001_torus',#{plc.eid},-50.0,10.0)")

# ── Face boundary: small patch, corners computed with |major|=50, minor=10 ────
# Torus parametrization (u=azimuth, v=meridian), |R|=50, r=10:
#   x = (|R| + r*cos(v)) * cos(u)
#   y = (|R| + r*cos(v)) * sin(u)
#   z = r * sin(v)
# Use a small patch: u in [0, 0.1], v in [0, 0.1].
R_abs = 50.0
r     = 10.0
u_vals = [0.0, 0.1, 0.1, 0.0]
v_vals = [0.0, 0.0, 0.1, 0.1]
pts = []
for u, v in zip(u_vals, v_vals):
    x = (R_abs + r * math.cos(v)) * math.cos(u)
    y = (R_abs + r * math.cos(v)) * math.sin(u)
    z = r * math.sin(v)
    pts.append(f.cartesian_point((x, y, z)))

# prc for pcurves on torus
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Build 4 line edges on the torus using SURFACE_CURVE + PCURVE
# Parametric corners: (0,0),(0.1,0),(0.1,0.1),(0,0.1)
uv_corners = [(0.0,0.0),(0.1,0.0),(0.1,0.1),(0.0,0.1)]

def mk_torus_edge(v_start, v_end, p3_start, p3_dir, p3_len,
                  p2_start, p2_dir, p2_len):
    p3s = f.cartesian_point(p3_start)
    d3  = f.direction(p3_dir)
    vec3 = f.vector(d3, p3_len)
    l3   = f.line(p3s, vec3)
    p2s  = f.cartesian_point(p2_start)
    d2   = f.direction(p2_dir)
    vec2 = f.vector(d2, p2_len)
    l2   = f.line(p2s, vec2)
    pcd  = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc   = f._emit_raw(f"PCURVE('pc',#{torus.eid},#{pcd.eid})")
    sc   = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{v_start.eid},#{v_end.eid},#{sc.eid},.T.)")

vs = [f.vertex_point(p) for p in pts]

# Bottom: (0,0)→(0.1,0), u increases, v=0
e0 = mk_torus_edge(vs[0], vs[1],
    (pts[0].coords if hasattr(pts[0],'coords') else (R_abs+r, 0.0, 0.0)),
    (1.0, 0.0, 0.0), 5.0,
    (0.0, 0.0), (1.0, 0.0), 0.1)

# Right: (0.1,0)→(0.1,0.1), v increases, u=0.1
e1 = mk_torus_edge(vs[1], vs[2],
    (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0,
    (0.1, 0.0), (0.0, 1.0), 0.1)

# Top: (0.1,0.1)→(0,0.1), u decreases, v=0.1
e2 = mk_torus_edge(vs[2], vs[3],
    (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 1.0,
    (0.1, 0.1), (-1.0, 0.0), 0.1)

# Left: (0,0.1)→(0,0), v decreases, u=0
e3 = mk_torus_edge(vs[3], vs[0],
    (0.0, 0.0, 0.0), (0.0, -1.0, 0.0), 1.0,
    (0.0, 0.1), (0.0, -1.0), 0.1)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
# TOROIDAL_SURFACE with negative major_radius IS the face_geometry.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
