"""Pmi138 — GEOMETRIC_TOLERANCE magnitude via MEASURE_REPRESENTATION_ITEM indirect chain.

Catalog claim: a STEP AP242 file (modeled on NX/NIST-style exports) where a
GEOMETRIC_TOLERANCE (flatness callout) magnitude is NOT stored in the direct
attribute slot that OCCT's writer produces, but instead is reached through an
indirect chain:
  GEOMETRIC_TOLERANCE → (no direct magnitude) → PROPERTY_DEFINITION_REPRESENTATION
  → REPRESENTATION → MEASURE_REPRESENTATION_ITEM → value

OCCT 7.9's StepDimTol_GeometricTolerance::Magnitude() returns a null handle
for this encoding because it only looks at the direct attribute; the indirect
MEASURE_REPRESENTATION_ITEM path is not traversed.  Fixed in OCCT 8.0.x master.

The fixture encodes a flatness tolerance on a SHAPE_ASPECT using the alternate
path.  Geometry loads correctly (simple planar solid); only the tolerance numeric
value is unreachable via the OCCT 7.9 API.

Per quality policy: OCCT 8.x and compatible kernels that implement the fix will
correctly read the magnitude = 0.05 mm.  This is documented as an
"expected-valid synthesis target" — the defect is in OCCT 7.9 only.

Source: https://dev.opencascade.org/content/issue-reading-geometric-tolerance-values-nxnist-generated-step-ap242-files-occt-79

Byte assertions:
  contains(b'FLATNESS_TOLERANCE')
  contains(b'MEASURE_REPRESENTATION_ITEM')
  contains(b'PROPERTY_DEFINITION_REPRESENTATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi138",
    schema="AP242",
    defect=(
        "FLATNESS_TOLERANCE magnitude encoded via indirect "
        "MEASURE_REPRESENTATION_ITEM chain (PROPERTY_DEFINITION_REPRESENTATION "
        "→ REPRESENTATION → MEASURE_REPRESENTATION_ITEM) rather than via the "
        "direct magnitude attribute; OCCT 7.9 Magnitude() returns null handle; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: GCS so OCC yields empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain reserves #9000+:
#   #9055 = PRODUCT_DEFINITION_SHAPE
#   #9056 = LENGTH_UNIT complex (mm)
#   #9060 = GEOMETRIC_REPRESENTATION_CONTEXT complex

# ── Datum reference (needed for flatness tolerance) ────────────────────────────
shape_asp = f._emit_raw(
    "SHAPE_ASPECT('top_face','face being toleranced',#9055,.T.)"
)

# ── FLATNESS_TOLERANCE with NO direct magnitude attribute ($) ─────────────────
# The magnitude is $-null in the entity attribute; receivers that only read
# StepDimTol_GeometricTolerance::Magnitude() will get a null handle.
flat_tol = f._emit_raw(
    f"FLATNESS_TOLERANCE('flatness',$,$,#{shape_asp.eid},$)"
)

# ── Indirect magnitude chain (the alternate encoding path) ───────────────────
# MEASURE_REPRESENTATION_ITEM carries the actual tolerance value: 0.05 mm.
# References the LENGTH_UNIT from the product chain (#9056).
mri = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('flatness_magnitude',LENGTH_MEASURE(0.05),#9056)"
)

# REPRESENTATION holds the MEASURE_REPRESENTATION_ITEM.
tol_rep = f._emit_raw(
    f"REPRESENTATION('tol_value_rep',(#{mri.eid}),#9060)"
)

# PROPERTY_DEFINITION for the tolerance value.
# Its definition slot points to the FLATNESS_TOLERANCE (type-correct per AP242
# §4.12.3 tolerance-value-property encoding).
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('tolerance_value','flatness magnitude property',#{flat_tol.eid})"
)

# PROPERTY_DEFINITION_REPRESENTATION links the value representation to the
# property_definition.  This is the indirect chain that OCCT 7.9 does not
# traverse when looking up the magnitude.
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{tol_rep.eid})"
)
