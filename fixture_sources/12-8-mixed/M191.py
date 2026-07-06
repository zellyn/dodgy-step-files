"""M191 — Isolated wireframe: GEOMETRIC_CURVE_SET of the 12 edges of a cube,
no topology (no EDGE_CURVE / EDGE_LOOP / FACE / SHELL / SOLID).

Catalog claim (input pattern): the transferred shape is a
GEOMETRIC_CURVE_SET whose items are twelve valid LINE curves tracing the
outline of a 10 mm cube. There is no topological superstructure at all —
no VERTEX_POINT, no EDGE_CURVE, no EDGE_LOOP, no ADVANCED_FACE, no
CLOSED_SHELL, no MANIFOLD_SOLID_BREP. The producer delivered a wireframe
where a downstream consumer expected a solid (a geometry-completeness /
"wireframe-only export" defect, common from sketch/curve exporters and
electrical/harness tools).

Distinguished from M051 (GEOMETRIC_CURVE_SET aggregating *non-geometric*
children — a schema-illegal mix that crashes OCC with signal 11) and from
M058 (curve set carried in an AP203-tag / AP214-entity schema-mismatch
file): here every item is a legal geometric_select curve, the file is
well-formed, and OCC transfers the set cleanly to a compound of loose
edges. The defect is completeness (no solid), not corruption.

Mechanism: GEOMETRIC_CURVE_SET → MANIFOLD_SURFACE_SHAPE_REPRESENTATION.
OCC imports one COMPOUND holding 12 free EDGEs; solid==0, face==0,
wire==0 — no solid root exists to hand to a boolean / meshing / mass-props
pipeline. Kernel must surface the wireframe-only nature (warn, or expose a
subshape inventory) rather than silently report success with an empty
solid set.

Byte assertions:
  - contains(b'GEOMETRIC_CURVE_SET')
  - count_entity_def(b'LINE') == 12
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 0

Tier-3 assertions (n_faces_total == 0 proves no solid: a solid requires faces):
  - shape_null == False
  - n_faces_total == 0
  - n_edges_total == 12
  - n_vertices_total == 0

Expected: occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M191",
    defect=(
        "GEOMETRIC_CURVE_SET of the 12 LINE curves of a cube outline with NO "
        "topology (no EDGE_CURVE/EDGE_LOOP/FACE/SHELL/SOLID); a legal "
        "wireframe delivered where a solid was expected (geometry-completeness "
        "defect); every item is a valid geometric_select curve so OCC "
        "transfers cleanly to a COMPOUND of 12 loose edges — solid==0, "
        "face==0; distinct from M051 (non-geometric children, crashes) and "
        "M058 (schema mismatch); GEOMETRIC_CURVE_SET IS the model entity — "
        "OCC yields a wireframe compound, never a solid root"
    ),
)

# 8 cube corners
C = [
    (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0),
    (0.0, 0.0, 10.0), (10.0, 0.0, 10.0), (10.0, 10.0, 10.0), (0.0, 10.0, 10.0),
]
# 12 cube edges as (start_idx, end_idx)
EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),   # bottom
    (4, 5), (5, 6), (6, 7), (7, 4),   # top
    (0, 4), (1, 5), (2, 6), (3, 7),   # verticals
]

lines = []
for a, b in EDGES:
    dx, dy, dz = (C[b][0] - C[a][0], C[b][1] - C[a][1], C[b][2] - C[a][2])
    mag = (dx * dx + dy * dy + dz * dz) ** 0.5
    d = f.direction((dx / mag, dy / mag, dz / mag))
    lines.append(f.line(f.cartesian_point(C[a]), f.vector(d, mag)))

curve_set = f._emit_raw(
    "GEOMETRIC_CURVE_SET('cube-wireframe-no-topology',("
    + ",".join(f"#{ln.eid}" for ln in lines) + "))"
)

f.add_product_chain(curve_set, mode="surface_shape")
