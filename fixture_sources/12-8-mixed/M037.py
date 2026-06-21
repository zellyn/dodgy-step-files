"""M037 — AP209 FEM element wrong node count.

Catalog claim: A finite-element entity declares quadratic_tetrahedron topology
but lists 8 nodes instead of 10; or unknown element type.

Reproducer recipe: AP209 file with curve_3d_element_descriptor declaring
quadratic tet shape but with node_list of length 8.

Byte assertions:
  contains(b'quadratic_tetrahedron')
  contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M037",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 FEM element with wrong node count; "
        "input: AP242/AP209 STEP file where a VOLUME_3D_ELEMENT_DESCRIPTOR declares "
        "quadratic_tetrahedron topology (which requires 10 nodes) but the associated "
        "node list has only 8 entries; "
        "per ISO 10303-104 AP209 a quadratic tetrahedron (C3D10) must have 10 nodes; "
        "kernel must drop the element and warn, not silently accept malformed FEA data; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: AP209 element wrong node count, FEA element node count wrong for hex8, "
        "quadratic_tetrahedron with 8 nodes, unknown FEM element type"
    ),
)

# ── FEM node coordinates (8 nodes provided, 10 required for quadratic tet) ────
nodes = []
node_coords = [
    (0., 0., 0.),
    (1., 0., 0.),
    (0., 1., 0.),
    (0., 0., 1.),
    (0.5, 0., 0.),
    (0.5, 0.5, 0.),
    (0., 0.5, 0.),
    (0., 0., 0.5),
]
for i, (x, y, z) in enumerate(node_coords):
    n = f._emit_raw(f"CARTESIAN_POINT('node_{i+1}',({x},{y},{z}))")
    nodes.append(n)

node_list_refs = ",".join(f"#{n.eid}" for n in nodes)

# ── VOLUME_3D_ELEMENT_DESCRIPTOR declaring quadratic_tetrahedron ──────────────
# Byte assertion: contains(b'VOLUME_3D_ELEMENT_DESCRIPTOR')
# Byte assertion: contains(b'quadratic_tetrahedron')
elem_desc = f._emit_raw(
    "VOLUME_3D_ELEMENT_DESCRIPTOR('quadratic_tetrahedron',$,$,$,$)"
)

# Element connectivity referencing 8 nodes (wrong: quadratic tet needs 10)
elem_conn = f._emit_raw(
    f"VALUE_REPRESENTATION_ITEM('node_list',"
    f"MEASURE_VALUE({len(nodes)}))"
)

# Node count mismatch marker
node_count_item = f._emit_raw(
    f"INTEGER_REPRESENTATION_ITEM('declared_node_count',8)"
)
expected_count_item = f._emit_raw(
    f"INTEGER_REPRESENTATION_ITEM('required_node_count_quadratic_tetrahedron',10)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('ap209-fem-element-wrong-node-count',"
    f"(#{elem_desc.eid},#{elem_conn.eid},"
    f"#{node_count_item.eid},#{expected_count_item.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M037.stp")
