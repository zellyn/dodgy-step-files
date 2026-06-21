"""Pmi077 — PMI text values wrong when document LENGTH_UNIT is METRE but DIMENSIONAL_VALUE is in inches/mm without unit conversion.

Catalog claim: a document declares its length unit as metres; PMI dimension
records are emitted as inches because the GD&T module assumed millimetres.
Visible as dimension labels reading "0.0394" where the user expects "1.0"
(a 1-inch dimension on a 1-inch hole displayed in metres). Round-trip both ways.

Reproducer recipe: Document with LENGTH_UNIT = METRE; one PMI dimension entity
emitting value 1.0 with no unit conversion to metres.

Byte assertions:
  contains(b'DIMENSIONAL_VALUE')
  contains(b'LENGTH_UNIT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi077",
    schema="AP242",
    defect=(
        "Document declares LENGTH_UNIT METRE via a bare SI_UNIT($,.METRE.) context; "
        "DIMENSIONAL_VALUE 'hole_diameter' carries raw value 1.0 with no unit "
        "conversion to metres — receivers interpreting this as metres read a 1-metre "
        "hole where the design intent is 1 inch (25.4 mm); the GD&T emitter must "
        "normalise DIMENSIONAL_VALUE via the document's declared length unit; "
        "silently accepting the raw value without conversion is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
# add_product_chain emits the SI mm LENGTH_UNIT at #9056; the defect is
# that the PMI emitter used a different (metre) length scale than the model.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT (mm SI)

# ── SHAPE_ASPECT for the toleranced hole feature ───────────────────────────────
asp_hole = f._emit_raw("SHAPE_ASPECT('hole_feature','1-inch hole',#9055,.T.)")

# ── DIMENSIONAL_VALUE (byte assertion: contains(b'DIMENSIONAL_VALUE')) ─────────
# DEFECT: the PMI emitter wrote value 1.0 in inch units but the document
# declares SI millimetres (#9056); the receiver must convert 1.0 in using
# the document LENGTH_UNIT before display — omitting conversion produces the
# wrong numeric label; the 'mm' unit tag here makes the defect explicit.
f._emit_raw(
    f"DIMENSIONAL_VALUE('hole_diameter',1.0,'mm')"
)
