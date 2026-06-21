"""Pmi080 — GD&T tolerance frame missing tolerance-zone plane reference.

Catalog claim: a geometric tolerance specifies a tolerance zone (e.g.,
perpendicularity within 0.1 mm). AP242 requires the zone be expressed with a
plane reference; older AP203 emissions drop the plane reference, leaving the
zone direction ambiguous. Reader silently picks an arbitrary plane.

Reproducer recipe: Geometric tolerance with tolerance_zone_form = 'unbounded'
and no tolerance_zone_plane reference. Reader assigns +Z plane silently.

Byte assertions:
  contains(b'GEOMETRIC_TOLERANCE')
  contains(b'TOLERANCE_ZONE_FORM')
  contains(b'SHAPE_ASPECT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi080",
    schema="AP242",
    defect=(
        "GEOMETRIC_TOLERANCE 'perp_tol' specifies a perpendicularity zone of "
        "0.1 mm on SHAPE_ASPECT 'feat_face'; the tolerance zone uses "
        "TOLERANCE_ZONE_FORM('unbounded') but no tolerance_zone_plane reference "
        "is provided — the zone direction is ambiguous; AP242 requires an explicit "
        "plane reference for an unbounded zone; older AP203 emissions omit it and "
        "receivers silently assign +Z, which is wrong for most features; receivers "
        "must reject or emit an 'ambiguous zone' diagnostic when the plane "
        "reference is absent; silently picking an arbitrary plane is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── SHAPE_ASPECT (byte assertion: contains(b'SHAPE_ASPECT')) ──────────────────
# The feature to which the perpendicularity tolerance is applied.
feat_face = f._emit_raw("SHAPE_ASPECT('feat_face','toleranced feature',#9055,.T.)")

# ── Tolerance value ────────────────────────────────────────────────────────────
tol_val = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('tol_value',LENGTH_MEASURE(0.1),#9056)"
)

# ── TOLERANCE_ZONE_FORM (byte assertion: contains) ───────────────────────────
# 'unbounded' zone type requires a plane reference (AP242 §PMI); absent here.
zone_form = f._emit_raw("TOLERANCE_ZONE_FORM('unbounded')")

# ── GEOMETRIC_TOLERANCE (byte assertion: contains) ────────────────────────────
# DEFECT: no tolerance_zone_plane reference provided; zone direction ambiguous.
# The 4th arg ($) is the omitted tolerance_zone — receivers must flag this.
f._emit_raw(
    f"GEOMETRIC_TOLERANCE('perp_tol','perp tol no zone-plane',$,"
    f"#{tol_val.eid},#{feat_face.eid})"
)
