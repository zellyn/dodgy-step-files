"""Pmi071 — PROJECTED_ZONE_DEFINITION with zero offset.

Catalog claim: PROJECTED_ZONE_DEFINITION carries projection_length (a positive
offset above the surface). A zero offset is geometrically degenerate — the
projected zone collapses onto the original feature, identical to having no
projected zone at all.

Reproducer recipe: PROJECTED_ZONE_DEFINITION with LENGTH_MEASURE(0.0).

Byte assertions:
  contains(b'PROJECTED_ZONE_DEFINITION')
  contains(b'GEOMETRIC_TOLERANCE_WITH_DEFINED_UNIT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi071",
    schema="AP242",
    defect=(
        "PROJECTED_ZONE_DEFINITION carries projection_length LENGTH_MEASURE(0.0); "
        "a zero offset is geometrically degenerate — the projected zone collapses "
        "onto the original feature and is identical to having no projected zone; "
        "receivers must reject zero-length projected zones or treat as 'no projection' "
        "with a warning; silently accepting zero is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Feature aspect to attach the tolerance to.
asp_tol = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")

# Tolerance magnitude for GEOMETRIC_TOLERANCE_WITH_DEFINED_UNIT.
tol_val = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.05),#9056)"
)

# TOLERANCE_ZONE_FORM (cylindrical — typical for position with projected zone).
zone_form = f._emit_raw("TOLERANCE_ZONE_FORM('cylindrical')")

# Defect: projection_length is 0.0 — geometrically degenerate.
proj_zone = f._emit_raw(
    f"PROJECTED_ZONE_DEFINITION(LENGTH_MEASURE(0.0),#{zone_form.eid},$)"
)

# GEOMETRIC_TOLERANCE_WITH_DEFINED_UNIT wraps the projected zone definition.
# Byte assertion: contains(b'GEOMETRIC_TOLERANCE_WITH_DEFINED_UNIT').
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_WITH_DEFINED_UNIT(#{asp_tol.eid},#{tol_val.eid},"
    f"#{proj_zone.eid},#{tol_val.eid})"
)
