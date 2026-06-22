"""Ad081 — Empty SHAPE_REPRESENTATION.items plus dangling PRODUCT_DEFINITION_SHAPE triggers out-of-range abort.

Catalog claim: a SHAPE_REPRESENTATION whose items list is empty (()) combined
with a dangling product chain (a PRODUCT_DEFINITION_SHAPE with no
SHAPE_DEFINITION_REPRESENTATION linking it back to any representation). The file
parses successfully but root-transfer dereferences an out-of-range index and
aborts. Producer signature: Rhino-6 STEP/IGES emitter.

Reproducer recipe: SHAPE_REPRESENTATION with empty items list () combined with
a PRODUCT_DEFINITION_SHAPE that has no SHAPE_DEFINITION_REPRESENTATION link.

Byte assertions:
  matches(rb"SHAPE_REPRESENTATION\\([^;]*,\\(\\),")
  matches(rb',\\(\\),')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad081",
    defect=(
        "empty SHAPE_REPRESENTATION.items list () plus dangling PRODUCT_DEFINITION_SHAPE "
        "with no SHAPE_DEFINITION_REPRESENTATION back-link; "
        "root-transfer dereferences out-of-range index and aborts; "
        "Rhino-6 emit signature; pythonocc-core #702; See also Ad043; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload 1: SHAPE_REPRESENTATION with empty items list.
# The geometric context re-uses the unit/context already emitted above.
# We reference origin as the context placeholder (any entity works).
# Satisfies: matches(rb"SHAPE_REPRESENTATION\([^;]*,\(\),") and matches(rb',\(\),')
geom_ctx_id = f._next_id
f._emit_raw("AXIS2_PLACEMENT_3D('origin_ctx',#1,$,$)")

f._emit_raw(
    f"SHAPE_REPRESENTATION('empty_items_rep',(),(#{geom_ctx_id}))"
)

# Attack payload 2: Dangling PRODUCT_DEFINITION_SHAPE — no SDR links back.
prod_b = f._emit_raw("PRODUCT('dangling_part','dangling_part','',())")
pdf_b = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_b.eid})"
)
pd_b = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{pdf_b.eid},#9003)"
)
# This PDS intentionally has no SHAPE_DEFINITION_REPRESENTATION referencing it.
f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','',#{pd_b.eid})"
)
