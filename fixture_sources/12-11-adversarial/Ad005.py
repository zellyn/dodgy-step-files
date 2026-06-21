"""Ad005 — Dangling forward reference to undefined #NNN.

Catalog claim: attribute slots reference instance IDs never declared, or whose
ID exceeds reasonable bounds; resolver dereferences nullptr from lookup table.

Byte assertions:
  matches(rb'ADVANCED_FACE\\([^;]*#42[^;]*#43') or contains(b'#999999999')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad005",
    defect=(
        "dangling forward references to undefined IDs; "
        "ADVANCED_FACE references #42 and #43 (never declared); "
        "MANIFOLD_SOLID_BREP references #999999999 (extreme-magnitude ID); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payloads:
# (1) ADVANCED_FACE referencing #42 and #43 — both never declared.
# Satisfies: matches(rb'ADVANCED_FACE\([^;]*#42[^;]*#43')
f._emit_raw("ADVANCED_FACE('',(#42),#43,.T.)")

# (2) Extreme-magnitude undefined ID.
# Satisfies: contains(b'#999999999')
f._emit_raw("MANIFOLD_SOLID_BREP('',#999999999)")

# (3) Plausible-range undefined ID (extra signal).
f._emit_raw("SHAPE_REPRESENTATION('s',(#100),#101)")
