"""M192 — Point-set only: GEOMETRIC_SET of eight CARTESIAN_POINTs, no
curves, no surfaces, no topology.

Catalog claim (input pattern): the transferred shape is a GEOMETRIC_SET
whose items are eight bare CARTESIAN_POINTs (the corners of a 10 mm cube).
There are no curves, no surfaces, and no topological entities of any kind —
the model is a pure point cloud. Producers of scan/probe data, feature
points, and "reference geometry only" exports emit exactly this. A
downstream consumer expecting a solid (or any bounded geometry) receives a
zero-dimensional model.

Distinct from the wireframe class (M191, curves-only → edges) and from the
curve-set crash/mismatch fixtures (M051 non-geometric children → signal 11;
M058 schema mismatch): every item here is a legal geometric_select POINT,
the file is well-formed, and OCC transfers the set to a COMPOUND of loose
VERTEXes — vertex>0 but edge==face==solid==0.

Mechanism: GEOMETRIC_SET → MANIFOLD_SURFACE_SHAPE_REPRESENTATION. OCC
imports one COMPOUND holding 8 free VERTEXes; there is no curve, surface,
shell, or solid. Kernel must not report import success as if a solid were
produced: it should surface the point-only nature (warn / subshape
inventory), since boolean, meshing, and mass-property pipelines have
nothing to operate on.

Byte assertions:
  - contains(b'GEOMETRIC_SET')
  - count_entity_def(b'CARTESIAN_POINT') == 8
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 0

Tier-3 assertions (n_faces_total == 0 proves no solid: a solid requires faces):
  - shape_null == False
  - n_faces_total == 0
  - n_edges_total == 0
  - n_vertices_total == 8

Expected: occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M192",
    defect=(
        "GEOMETRIC_SET of eight bare CARTESIAN_POINTs (cube corners) with NO "
        "curves, surfaces, or topology — a pure point cloud delivered where "
        "bounded geometry was expected (geometry-completeness defect); every "
        "item is a valid geometric_select POINT so OCC transfers cleanly to a "
        "COMPOUND of 8 loose vertices — edge==face==solid==0; distinct from "
        "M191 (wireframe/curves) and M051 (non-geometric children, crashes); "
        "GEOMETRIC_SET IS the model entity — OCC yields a vertex compound, "
        "never a solid root"
    ),
)

C = [
    (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0),
    (0.0, 0.0, 10.0), (10.0, 0.0, 10.0), (10.0, 10.0, 10.0), (0.0, 10.0, 10.0),
]
points = [f.cartesian_point(p) for p in C]

point_set = f._emit_raw(
    "GEOMETRIC_SET('cube-corners-point-cloud',("
    + ",".join(f"#{p.eid}" for p in points) + "))"
)

f.add_product_chain(point_set, mode="surface_shape")
