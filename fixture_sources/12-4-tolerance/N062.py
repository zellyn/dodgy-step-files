"""N062 — ShapeAnalysis_ShapeTolerance.GlobalTolerance min/max dispatch

GlobalTolerance with mode=-1 (minimum) returns inconsistent results when the
input shape contains both VERTEX and EDGE with identical tolerance values. The
tie-breaking logic is order-dependent and affected by topological traversal order.

Geometry: 4-vertex square face (1×1) with edges and vertices all declaring
1e-3 tolerance. Two UNCERTAINTY_MEASURE_WITH_UNIT entries (1e-3 each) for
vertex and edge in GEOMETRIC_REPRESENTATION_CONTEXT.

Byte assertions:
  contains(b'vertex_tolerance')
  contains(b'edge_tolerance')
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N062",
    defect=(
        "1×1 square CLOSED_SHELL face; vertex_tolerance=1e-3 and edge_tolerance=1e-3 "
        "in geometry context; GlobalTolerance(mode=-1) tie-breaking is "
        "topological-traversal-order-dependent for identical values"
    ),
)

# 4-vertex square face (1x1) with edges and vertices all declaring 1.0e-3 tolerance
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((1.0, 1.0, 0.0), name="p2")
p3 = f.cartesian_point((0.0, 1.0, 0.0), name="p3")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3")

# 4 edges of square
de0 = f.direction((1.0, 0.0, 0.0), name="d_e0")
ve0 = f.vector(de0, 1.0, name="vec_e0")
le0 = f.line(p0, ve0, name="line_e0")
e0 = f.edge_curve(v0, v1, le0, name="e0")

de1 = f.direction((0.0, 1.0, 0.0), name="d_e1")
ve1 = f.vector(de1, 1.0, name="vec_e1")
le1 = f.line(p1, ve1, name="line_e1")
e1 = f.edge_curve(v1, v2, le1, name="e1")

de2 = f.direction((-1.0, 0.0, 0.0), name="d_e2")
ve2 = f.vector(de2, 1.0, name="vec_e2")
le2 = f.line(p2, ve2, name="line_e2")
e2 = f.edge_curve(v2, v3, le2, name="e2")

de3 = f.direction((0.0, -1.0, 0.0), name="d_e3")
ve3 = f.vector(de3, 1.0, name="vec_e3")
le3 = f.line(p3, ve3, name="line_e3")
e3 = f.edge_curve(v3, v0, le3, name="e3")

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Plane surface
orig = f.cartesian_point((0.0, 0.0, 0.0), name="origin")
dz = f.direction((0.0, 0.0, 1.0), name="z")
dx = f.direction((1.0, 0.0, 0.0), name="x")
plc = f.axis2_placement_3d(orig, dz, dx)
plane = f.plane(plc)

# Face on plane
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)
shell = f.closed_shell([face], name="shell")

# Units and TWO tolerance declarations with same value (1.0e-3)
# — the tie condition that creates traversal-order dependency
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Vertex tolerance: 1.0e-3
unc_v = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},'distance_accuracy_value','vertex_tolerance')")
# Edge tolerance: 1.0e-3 (tie condition)
unc_e = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},'distance_accuracy_value','edge_tolerance')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_v.eid},#{unc_e.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N062.stp")
