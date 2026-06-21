"""N073 — BRepLib.UpdateDeflection null-triangulation skip

UpdateDeflection checks if a face has triangulation; if reference is null,
it silently skips. Deflection state remains uninitialized (undefined, stale, or
zero), and downstream consumers may read garbage or assume face is
valid-triangulated when it is not.

Reproducer: Face created from surface (no triangulation attached). Call
UpdateDeflection(face, tol). If face->Triangulation() is null, routine returns
without setting deflection state.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 4
  count_entity_def(b'ADVANCED_FACE') == 1

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N073",
    defect=(
        "5×5 CLOSED_SHELL planar face with no triangulation data; "
        "UpdateDeflection finds null face->Triangulation() and silently returns "
        "without setting deflection state — stale/undefined deflection downstream"
    ),
)

# Planar face without explicit triangulation record.
# UpdateDeflection called on this face will find null triangulation and skip.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((5.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((5.0, 5.0, 0.0), name="p2")
p3 = f.cartesian_point((0.0, 5.0, 0.0), name="p3")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3")

# Simple edge-loop quad
d0 = f.direction((1.0, 0.0, 0.0), name="d0")
vec0 = f.vector(d0, 5.0, name="vec0")
l0 = f.line(p0, vec0, name="line0")
e0 = f.edge_curve(v0, v1, l0, name="e0")

d1 = f.direction((0.0, 1.0, 0.0), name="d1")
vec1 = f.vector(d1, 5.0, name="vec1")
l1 = f.line(p1, vec1, name="line1")
e1 = f.edge_curve(v1, v2, l1, name="e1")

d2 = f.direction((-1.0, 0.0, 0.0), name="d2")
vec2 = f.vector(d2, 5.0, name="vec2")
l2 = f.line(p2, vec2, name="line2")
e2 = f.edge_curve(v2, v3, l2, name="e2")

d3 = f.direction((0.0, -1.0, 0.0), name="d3")
vec3 = f.vector(d3, 5.0, name="vec3")
l3 = f.line(p3, vec3, name="line3")
e3 = f.edge_curve(v3, v0, l3, name="e3")

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
fob = f.face_outer_bound(loop)

# Plane surface (no triangulation attached in STEP data)
d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
plc = f.axis2_placement_3d(p0, d_z, d_x, name="ax3")
plane = f.plane(plc, name="xy_plane")
# ADVANCED_FACE with no triangulation — UpdateDeflection will skip
face = f.advanced_face([fob], plane, name="face")
shell = f.closed_shell([face], name="shell")

# Units and nominal tolerance
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-2),#{lu.eid},'distance_accuracy_value','')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N073.stp")
