"""Ad051 — Reference to non-existent entity number (negative or out-of-range).

Catalog claim: references to entity numbers beyond DATA section, or legacy
negative numbers, yield literal NULL via lookup; older OCCT segfaulted.

Reproducer recipe: ADVANCED_FACE referencing #NNN where NNN > max_id, or #-1.

Byte assertions:
  contains(b'#-1') or matches(rb'#-\\d+')
  matches(rb'#-\\d+')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad051",
    defect=(
        "negative entity references (#-1, #-2) and out-of-range IDs; "
        "legacy negative numbers yield NULL via lookup; "
        "ADVANCED_FACE and SHAPE_REPRESENTATION referencing #-1; "
        "out-of-range #9999999 reference; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload 1: ADVANCED_FACE referencing #-1 (negative entity number).
# Satisfies: contains(b'#-1') and matches(rb'#-\d+')
f._emit_raw("ADVANCED_FACE('neg_ref',(#-1),#-2,.T.)")

# Attack payload 2: SHAPE_REPRESENTATION referencing negative ID #-1.
# Cross-oracle note: pure-Python Part-21 rejects (E_UNRESOLVED_REFS);
# OCCT silently accepts (load is empty).
f._emit_raw("SHAPE_REPRESENTATION('neg_sr',(#-1),#-2)")

# Attack payload 3: MANIFOLD_SOLID_BREP referencing out-of-range positive ID.
# Reinforces the "beyond DATA section" class of the same bug.
f._emit_raw("MANIFOLD_SOLID_BREP('out_of_range',#9999999)")

# Attack payload 4: VERTEX_POINT referencing negative-index CARTESIAN_POINT.
f._emit_raw("VERTEX_POINT('neg_vertex',#-3)")
