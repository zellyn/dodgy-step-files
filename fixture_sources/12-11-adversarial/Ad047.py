"""Ad047 — ADVANCED_FACE same_sense=.F. inverts surface normal.

Catalog claim: an ADVANCED_FACE whose same_sense flag is .F. while the
supporting surface (e.g. a PLANE with +Z normal) is itself oriented normally;
the face flag inverts the surface normal so the orientation is inverse of the
host surface.  Healing reverses face orientation, producing negative computed
area downstream.

Reproducer recipe: input with one mis-oriented face that triggers ShapeFix
orientation flip.

Byte assertions:
  matches(rb'ADVANCED_FACE\\([^;]*,\\.F\\.')
  count(b'.F.') >= 1

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad047",
    defect=(
        "ADVANCED_FACE.same_sense = .F. while supporting PLANE has +Z normal; "
        "face flag inverts surface normal — orientation is inverse of host surface; "
        "ShapeFix orientation flip produces negative computed area downstream; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Build a planar face with same_sense=.F. — the attack payload.
# The PLANE has a +Z normal (standard orientation); setting same_sense=.F.
# flips the face orientation, creating the mis-oriented face.

p_origin = f.cartesian_point((0.0, 0.0, 0.0))
dir_z = f.direction((0.0, 0.0, 1.0))
dir_x = f.direction((1.0, 0.0, 0.0))
axis3d = f.axis2_placement_3d(p_origin, dir_z, dir_x)
plane = f.plane(axis3d)

# Corners of a unit square in the XY plane.
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))

dir_px = f.direction(( 1.0, 0.0, 0.0))
dir_py = f.direction(( 0.0, 1.0, 0.0))
dir_nx = f.direction((-1.0, 0.0, 0.0))
dir_ny = f.direction(( 0.0,-1.0, 0.0))

vec_px = f.vector(dir_px, 1.0)
vec_py = f.vector(dir_py, 1.0)
vec_nx = f.vector(dir_nx, 1.0)
vec_ny = f.vector(dir_ny, 1.0)

line_bottom = f.line(p00, vec_px)
line_right  = f.line(p10, vec_py)
line_top    = f.line(p11, vec_nx)
line_left   = f.line(p01, vec_ny)

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

ec_bottom = f.edge_curve(v00, v10, line_bottom)
ec_right  = f.edge_curve(v10, v11, line_right)
ec_top    = f.edge_curve(v11, v01, line_top)
ec_left   = f.edge_curve(v01, v00, line_left)

oe_bottom = f.oriented_edge(ec_bottom, True)
oe_right  = f.oriented_edge(ec_right,  True)
oe_top    = f.oriented_edge(ec_top,    True)
oe_left   = f.oriented_edge(ec_left,   True)

loop = f.edge_loop([oe_bottom, oe_right, oe_top, oe_left])
fob  = f.face_outer_bound(loop, True)

# Attack payload: ADVANCED_FACE with same_sense = .F.
# This satisfies: matches(rb'ADVANCED_FACE\([^;]*,\.F\.')
# and: count(b'.F.') >= 1
bounds_ref = f"(#{fob.eid})"
f._emit_raw(
    f"ADVANCED_FACE('inverted_face',{bounds_ref},#{plane.eid},.F.)"
)
