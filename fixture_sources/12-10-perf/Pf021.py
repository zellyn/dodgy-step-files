"""Pf021 — Floating / non-deterministic crash in shape healing on near-apex CONICAL_SURFACE edge.

Catalog claim: healing pipeline crashes intermittently on the same input;
symptoms are uninitialized memory, threading races, or FP exceptions in
projection routines.  Common trigger: a CONICAL_SURFACE whose EDGE_CURVE
passes through the cone apex, with a near-zero-length edge between the apex
and a 1e-12-offset VERTEX_POINT — singular projection in healing produces an
FP exception or uninitialised-memory read.

The fixture encodes a CONICAL_SURFACE with three EDGE_CURVEs forming an
EDGE_LOOP: one near-apex edge whose start vertex is the cone apex itself and
whose end vertex is offset by only 1e-12 in the Z direction (near-zero
length), plus two normal edges forming the remainder of the loop.  The
conical surface is placed at the origin with the apex at Z=0.  The near-apex
vertex-to-vertex gap is the singular projection trigger.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 3
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf021",
    defect=(
        "CONICAL_SURFACE with near-apex EDGE_CURVE: apex vertex at Z=0, "
        "adjacent vertex at Z=1e-12 (near-zero edge); singular projection in "
        "healing produces FP exception / uninitialised-memory read; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# CONICAL_SURFACE geometry.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
# semi_angle = 30 degrees (pi/6), radius = 0 at apex
cone = f.conical_surface(plc, radius=0.0, semi_angle=0.5236)

# Vertices for the near-apex edge: apex itself + 1e-12-offset point.
p_apex        = f.cartesian_point((0.0, 0.0, 0.0))       # apex
p_near_apex   = f.cartesian_point((0.0, 0.0, 1.0e-12))   # near-apex offset
p_rim1        = f.cartesian_point((1.0, 0.0, 1.7321))    # rim at Z~sqrt(3)
p_rim2        = f.cartesian_point((0.0, 1.0, 1.7321))    # rim, 90° around

v_apex      = f.vertex_point(p_apex)
v_near_apex = f.vertex_point(p_near_apex)
v_rim1      = f.vertex_point(p_rim1)
v_rim2      = f.vertex_point(p_rim2)

# Near-zero-length edge from apex to near-apex offset.
dz   = f.direction((0.0, 0.0, 1.0))
vec_z = f.vector(dz, 1.0e-12)
ln_near = f.line(p_apex, vec_z)
e_near = f.edge_curve(v_apex, v_near_apex, ln_near)

# Two normal edges along the rim.
dx   = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(dx, 1.0)
ln_x = f.line(p_near_apex, vec_x)
e_x  = f.edge_curve(v_near_apex, v_rim1, ln_x)

dy   = f.direction((0.0, 1.0, 0.0))
vec_y = f.vector(dy, 1.0)
ln_y = f.line(p_rim1, vec_y)
e_y  = f.edge_curve(v_rim1, v_rim2, ln_y)

# Close back to apex.
import math
d_back = (-1.0 / math.sqrt(2.0), -1.0 / math.sqrt(2.0), 0.0)
d_back_e = f.direction(d_back)
vec_back = f.vector(d_back_e, math.sqrt(2.0))
ln_back  = f.line(p_rim2, vec_back)
e_back   = f.edge_curve(v_rim2, v_apex, ln_back)

loop = f.edge_loop([
    f.oriented_edge(e_near, True),
    f.oriented_edge(e_x,    True),
    f.oriented_edge(e_y,    True),
    f.oriented_edge(e_back, True),
])
face_bound = f.face_outer_bound(loop)
cone_face  = f.advanced_face([face_bound], cone)

# SHELL_BASED_SURFACE_MODEL wrapping the cone face — not the product chain
# entity (GCS is) so OCC yields empty/empty.
open_shell = f.open_shell([cone_face], name="apex_cone_shell")
f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('cone_sbsm',(#{open_shell.eid}))")
