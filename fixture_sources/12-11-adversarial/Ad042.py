"""Ad042 — Reference to entity-of-wrong-type in attribute slot.

Catalog claim: schema SELECT type validated by structural shape only;
attribute type is wrong subtype, leading downstream chained calls
(x->A()->B()) to deref a null handle.  Reproducer: minimum AP214 with
#27=SHAPE_DEFINITION_REPRESENTATION(#23,#26) where #23=SHAPE_ASPECT(..)
instead of PROPERTY_DEFINITION_SHAPE.

Byte assertions:
  contains(b'SHAPE_DEFINITION_REPRESENTATION') and contains(b'SHAPE_ASPECT')
  contains(b'SHAPE_DEFINITION_REPRESENTATION') and contains(b'SHAPE_ASPECT(')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad042",
    defect=(
        "type-confusion: SHAPE_ASPECT in SHAPE_DEFINITION_REPRESENTATION attribute slot "
        "that requires PROPERTY_DEFINITION_SHAPE; schema SELECT branch mismatch → "
        "null-handle deref on chained accessor; "
        "1088/1267 SDRs broken in 430 MB CATIA V6 file; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: SHAPE_DEFINITION_REPRESENTATION whose first attribute
# must be PROPERTY_DEFINITION_SHAPE but is SHAPE_ASPECT instead.
#
# We pin the attack entities to low IDs matching the catalog's reproducer
# recipe (#23=SHAPE_ASPECT, #26=..., #27=SHAPE_DEFINITION_REPRESENTATION).
# Use IDs well below the PRODUCT chain (9000+).

f._next_id = 23

# #23 = SHAPE_ASPECT (wrong type — should be PROPERTY_DEFINITION_SHAPE)
shape_aspect = f._emit_raw(
    "SHAPE_ASPECT('mistyped_aspect','wrong branch',"
    "#9000,.T.)"   # #9000 is APPLICATION_CONTEXT in PRODUCT chain
)
# shape_aspect.eid == 23

f._next_id = 24
product_def_shape = f._emit_raw(
    "PRODUCT_DEFINITION_SHAPE('','',"
    "#9000)"
)
# #24 = PRODUCT_DEFINITION_SHAPE (a valid PDS, not used as SDR first-arg)

f._next_id = 25
shape_rep = f._emit_raw(
    "SHAPE_REPRESENTATION('',(#1),#9000)"
)
# #25 = SHAPE_REPRESENTATION referencing our CARTESIAN_POINT

f._next_id = 26
advanced_rep = f._emit_raw(
    "ADVANCED_BREP_SHAPE_REPRESENTATION('',(#1),#9000)"
)
# #26 = representation

f._next_id = 27
# #27 = SHAPE_DEFINITION_REPRESENTATION(#23,#26):
# first arg MUST be PROPERTY_DEFINITION but is SHAPE_ASPECT → type confusion.
f._emit_raw(
    f"SHAPE_DEFINITION_REPRESENTATION(#{shape_aspect.eid},#{advanced_rep.eid})"
)
