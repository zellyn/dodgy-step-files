"""Gs190 — TOROIDAL_SURFACE with minor_radius and major_radius attribute values swapped.

Catalog claim: STEP file with a MANIFOLD_SOLID_BREP containing a donut-shaped body.
The TOROIDAL_SURFACE entity encodes major_radius=2.0, minor_radius=10.0 (swapped:
the minor radius is larger than the major, which would produce a self-intersecting
torus — an impossible geometry). The intent is to test reader behavior when the
minor/major radius roles are swapped from their intended meaning.

ISO 10303-42 §4.4.37 TOROIDAL_SURFACE: positional order is (position, major_radius,
minor_radius).  A conforming torus has major_radius > minor_radius; here the values
are inverted — minor (2.0) appears in the major_radius slot and major (10.0) appears
in the minor_radius slot.

Source: SolidCAM/HSMWorks STEP import community forum (B4 wave-6 DEF-CC).

Mechanism: TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry with swapped radii
(major_radius=2.0, minor_radius=10.0). A conforming reader produces a
geometrically-inverted torus; the tier-3 oracle confirms the swap by reading the
actual attribute values from the file.

Byte assertions:
  contains(b'TOROIDAL_SURFACE')
  contains(b'2.0,10.0')   (major=2.0 then minor=10.0, swapped order)

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1) (OCC accepts self-intersecting torus)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs190",
    defect=(
        "TOROIDAL_SURFACE IS ADVANCED_FACE.face_geometry; "
        "major_radius=2.0, minor_radius=10.0 (values swapped — minor > major, "
        "self-intersecting torus); ISO 10303-42 §4.4.37 positional order violated; "
        "SolidCAM/HSMWorks STEP import forum (DEF-CC); "
        "OCC may accept with geometrically-inverted torus"
    ),
)

# ── DEFECT: TOROIDAL_SURFACE with swapped radii ───────────────────────────────
# ISO 10303-42 §4.4.37: TOROIDAL_SURFACE(position, major_radius, minor_radius)
# Correct: major_radius=10.0, minor_radius=2.0 (tube radius 2 on ring of radius 10)
# DEFECT:  major_radius=2.0,  minor_radius=10.0 (values swapped — self-intersecting)
MAJOR_RADIUS = 2.0   # DEFECT: should be 10.0 (swapped)
MINOR_RADIUS = 10.0  # DEFECT: should be 2.0  (swapped)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)

# Byte assertion: contains(b'TOROIDAL_SURFACE') and contains(b'2.0,10.0')
# Using _emit_raw so the swapped values appear literally in file
torus = f._emit_raw(
    f"TOROIDAL_SURFACE('gs190_torus',#{plc.eid},{MAJOR_RADIUS},{MINOR_RADIUS})"
)

# ── Parametric representation context (2D) ───────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Build a small rectangular patch on the (intended) torus surface ───────────
# Use the INTENDED geometry (major=10, minor=2) for 3D point coordinates so
# that the 3D boundary is geometrically coherent, while the TOROIDAL_SURFACE
# encodes the defect (swapped) values.
# Torus parametrization: x=(R+r*cos(v))*cos(u), y=(R+r*cos(v))*sin(u), z=r*sin(v)
# Intended: R_intended=10, r_intended=2 (so the 3D coordinates are physically meaningful)
R_int = 10.0  # intended major
r_int = 2.0   # intended minor

def torus_pt(u, v):
    return (
        (R_int + r_int * math.cos(v)) * math.cos(u),
        (R_int + r_int * math.cos(v)) * math.sin(u),
        r_int * math.sin(v),
    )

# Use a small patch: u in [0, 0.1], v in [0, 0.1]
corners_uv = [(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.1)]
corners_3d = [torus_pt(u, v) for u, v in corners_uv]

pts   = [f.cartesian_point(c) for c in corners_3d]
verts = [f.vertex_point(p) for p in pts]

def mk_torus_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3s  = f.cartesian_point(p3_start)
    d3   = f.direction(d3t)
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

# Bottom: (0,0)→(0.1,0), u increases, v=0
e0 = mk_torus_edge(verts[0], verts[1],
    corners_3d[0], (1.0, 0.0, 0.0), 1.0,
    (0.0, 0.0), (1.0, 0.0), 0.1)

# Right: (0.1,0)→(0.1,0.1), v increases, u=0.1
e1 = mk_torus_edge(verts[1], verts[2],
    corners_3d[1], (0.0, 1.0, 0.0), 1.0,
    (0.1, 0.0), (0.0, 1.0), 0.1)

# Top: (0.1,0.1)→(0,0.1), u decreases, v=0.1
e2 = mk_torus_edge(verts[2], verts[3],
    corners_3d[2], (-1.0, 0.0, 0.0), 1.0,
    (0.1, 0.1), (-1.0, 0.0), 0.1)

# Left: (0,0.1)→(0,0), v decreases, u=0
e3 = mk_torus_edge(verts[3], verts[0],
    corners_3d[3], (0.0, -1.0, 0.0), 1.0,
    (0.0, 0.1), (0.0, -1.0), 0.1)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# TOROIDAL_SURFACE with SWAPPED radii IS the face_geometry — defect IS wired in
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
