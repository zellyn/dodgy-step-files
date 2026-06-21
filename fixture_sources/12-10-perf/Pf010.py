"""Pf010 — Cyclic / self-referential reference graph causes infinite recursion.

Catalog claim: a COMPOSITE_CURVE_SEGMENT whose parent_curve is the composite
itself, or a SHAPE_REPRESENTATION_RELATIONSHIP whose rep_2 is itself, causes
the reference resolver to loop forever or stack-overflow.

The fixture encodes the pattern using a COMPOSITE_CURVE whose first segment's
parent_curve reference cycles back to the composite entity itself (forward-
referenced using _emit_raw with pre-planned IDs).  A GEOMETRIC_CURVE_SET is
used as the product-chain model entity so OCC yields empty/empty.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 2
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf010",
    defect=(
        "COMPOSITE_CURVE segment whose parent_curve references the composite "
        "itself; reference resolver follows cycle indefinitely; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Supporting point for the composite.
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((2.0, 0.0, 0.0))

# Plan cyclic IDs:
#   composite_id  = base + 0
#   seg_id        = base + 1
base = f._next_id
composite_id = base + 0
seg_id       = base + 1

# Segment: parent_curve = composite_id (forward ref back to the composite).
# COMPOSITE_CURVE_SEGMENT(transition_code, same_sense, parent_curve)
f._emit_raw(
    f"COMPOSITE_CURVE('cyclic_composite',(#{seg_id}),.F.)"
)  # composite_id
f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{composite_id})"
)  # seg_id — parent_curve points back to composite_id

assert f._next_id == base + 2, (
    f"ID layout mismatch: expected {base+2}, got {f._next_id}"
)
