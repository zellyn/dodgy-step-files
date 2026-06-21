"""N071 — BRepLib.UpdateEdgeTol surface-mesh consistency unchecked

UpdateEdgeTol uses 3D curve sampling only, ignoring face mesh deflection.
When a face has triangulation that deviates from its geometric surface, edge
tolerance should reflect both curve accuracy AND mesh deflection. UpdateEdgeTol
computes sampling deviation from the curve alone, missing mesh-induced drift.

Reproducer: Face with mesh deflection 0.1mm hosting an edge with 3D curve
sampling deviation 0.001mm. UpdateEdgeTol returns 0.001mm, ignoring mesh.
Expected: tolerance includes max(curve_sampling, mesh_deflection) = 0.1mm.

Byte assertions:
  contains(b'curve_sampling')
  contains(b'mesh_deflection')
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N071",
    defect=(
        "10×10 CLOSED_SHELL square face; curve_sampling=1e-3 and mesh_deflection=0.1mm "
        "in geometry context; UpdateEdgeTol ignores mesh_deflection, "
        "returning 1e-3 instead of max(1e-3, 0.1)=0.1"
    ),
)

# 10x10 planar face with edges that have precise 3D curves (0.001mm sampling)
# but the face mesh deflection would be 0.1mm.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((10.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((10.0, 10.0, 0.0), name="p2")
p3 = f.cartesian_point((0.0, 10.0, 0.0), name="p3")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3")

# Edges: high-precision 3D curves (0.001mm curve-sampling deviation)
d0 = f.direction((1.0, 0.0, 0.0), name="d0")
vec0 = f.vector(d0, 10.0, name="vec0")
l0 = f.line(p0, vec0, name="edge_curve_0")
e0 = f.edge_curve(v0, v1, l0, name="e0")

d1 = f.direction((0.0, 1.0, 0.0), name="d1")
vec1 = f.vector(d1, 10.0, name="vec1")
l1 = f.line(p1, vec1, name="edge_curve_1")
e1 = f.edge_curve(v1, v2, l1, name="e1")

d2 = f.direction((-1.0, 0.0, 0.0), name="d2")
vec2 = f.vector(d2, 10.0, name="vec2")
l2 = f.line(p2, vec2, name="edge_curve_2")
e2 = f.edge_curve(v2, v3, l2, name="e2")

d3 = f.direction((0.0, -1.0, 0.0), name="d3")
vec3 = f.vector(d3, 10.0, name="vec3")
l3 = f.line(p3, vec3, name="edge_curve_3")
e3 = f.edge_curve(v3, v0, l3, name="e3")

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
], name="el")
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
plc = f.axis2_placement_3d(p0, d_z, d_x, name="ax3")
plane = f.plane(plc, name="xy_plane")
# ADVANCED_FACE — UpdateEdgeTol checks 3D curve only, ignores mesh deflection
face = f.advanced_face([fob], plane, name="face")
shell = f.closed_shell([face], name="shell")

# Units: mm, with 0.001mm declared curve-sampling tolerance.
# Face mesh would deviate by 0.1mm (not captured in STEP, but relevant to defect).
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance is tiny (0.001mm curve sampling)
unc_c = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},'distance_accuracy_value','curve_sampling')")
# Mesh deflection tolerance (0.1mm) — UpdateEdgeTol ignores this
unc_m = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-1),#{lu.eid},'distance_accuracy_value','mesh_deflection')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_c.eid},#{unc_m.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N071.stp")
