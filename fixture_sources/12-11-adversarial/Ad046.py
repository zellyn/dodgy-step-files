"""Ad046 — STEP writer crashes on ADVANCED_FACE EDGE_CURVE with no SURFACE_CURVE
/ pcurve plus empty APPLIED_GROUP_ASSIGNMENT.

Catalog claim: writer-side null-deref when a shape has missing handles or
empty group attributes.  Common trigger: an EDGE_CURVE used on an ADVANCED_FACE
whose curve is a bare 3D LINE (no SURFACE_CURVE wrapper, no pcurve), combined
with an APPLIED_GROUP_ASSIGNMENT whose items list is empty; both attributes the
writer dereferences without a null check.

Reproducer recipe: shape with missing 2D-parametric curve fed to STEP writer;
or SolveSpace lathe-then-extrusion-difference part.

Byte assertions:
  contains(b'APPLIED_GROUP_ASSIGNMENT')
  contains(b'END-ISO-10303-21')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad046",
    defect=(
        "writer null-deref: EDGE_CURVE on ADVANCED_FACE with bare 3D LINE and "
        "no SURFACE_CURVE/pcurve; APPLIED_GROUP_ASSIGNMENT with empty items list; "
        "both trigger null-deref in writer output path; "
        "FreeCAD #5783 / SolveSpace 0-byte STEP output; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload 1: EDGE_CURVE on an ADVANCED_FACE with a bare 3D LINE —
# no SURFACE_CURVE wrapper, no pcurve.  This is the missing-handle precondition
# that triggers the writer null-deref when the shape is re-serialised.

# Build a minimal planar face with the bare-LINE edge curve.
p_origin = f.cartesian_point((0.0, 0.0, 0.0))
p_xaxis  = f.cartesian_point((1.0, 0.0, 0.0))
p_zaxis  = f.cartesian_point((0.0, 0.0, 1.0))

dir_z  = f.direction((0.0, 0.0, 1.0))
dir_x  = f.direction((1.0, 0.0, 0.0))
axis3d = f.axis2_placement_3d(p_origin, dir_z, dir_x)
plane  = f.plane(axis3d)

# Corners of a unit square.
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))

# Bare 3D LINEs — no SURFACE_CURVE, no pcurve.
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

# EDGE_CURVEs use bare LINE (no SURFACE_CURVE wrapper).
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
face = f.advanced_face([fob], plane, True)

# Attack payload 2: APPLIED_GROUP_ASSIGNMENT with empty items list.
# This is R050 (empty APPLIED_GROUP_ASSIGNMENT write exception).
# Satisfies: contains(b'APPLIED_GROUP_ASSIGNMENT')
group = f._emit_raw("GROUP('empty_group','triggers writer null-deref on empty items')")
f._emit_raw(f"APPLIED_GROUP_ASSIGNMENT(#{group.eid},(#{face.eid}),())")
