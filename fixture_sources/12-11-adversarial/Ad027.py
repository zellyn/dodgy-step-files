"""Ad027 — STEP "zip bomb": 10⁷ tiny instances exhaust memory.

Catalog claim: file declares N million CARTESIAN_POINTs; parser allocates
O(N) instance pointer table and O(N×K) reverse-reference map; small input
expands to many GB resident.

Byte assertions:
  count_entity_def(b'CARTESIAN_POINT') >= 5 or count(b'#') >= 100
  count_entity_def(b'CARTESIAN_POINT') >= 5 or count(b'#') >= 30

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad027",
    defect=(
        "zip-bomb: many CARTESIAN_POINT declarations exhaust O(N) instance table; "
        "structural attack pattern — parser must enforce max_instances budget; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: many CARTESIAN_POINT declarations.
# At fixture scale this is modest; production exploitation inflates the
# count to millions.  The pattern (N small instances) is the bug trigger.
# count_entity_def(b'CARTESIAN_POINT') >= 5 and count(b'#') >= 100.
for i in range(50):
    x = float(i) * 0.01
    f._emit_raw(f"CARTESIAN_POINT('',(1.0E+308,{x},{x}))")
