"""Pmi074 — Hole feature whose depth exceeds host-part bounding-box thickness.

Catalog claim: AP242 ROUND_HOLE carries a depth attribute. A producer that
copies a hole feature from a thicker design without updating the depth emits a
hole deeper than the material thickness; geometrically the hole exits the back
face but is encoded as a blind hole.

Reproducer recipe: SHAPE_ASPECT 'round_hole' with DIMENSIONAL_SIZE('distance')
of 50.0mm in a host part 5mm thick.

Byte assertions:
  count_entity_def(b'DIMENSIONAL_SIZE') == 2
  count_entity_def(b'MEASURE_REPRESENTATION_ITEM') == 2
  contains(b'SHAPE_ASPECT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi074",
    schema="AP242",
    defect=(
        "ROUND_HOLE 'round_hole' has hole depth DIMENSIONAL_SIZE('distance') "
        "50.0mm but host part 'host_part' is only 5mm thick; the blind hole is "
        "encoded as 50mm deep, which exceeds the local material thickness by 10x; "
        "receivers must validate hole depth against host-part topology and warn "
        "when depth exceeds thickness; in tolerant mode, coerce to a through-hole "
        "with a diagnostic; silently accepting is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Two SHAPE_ASPECTs: the hole feature and the host part reference ───────────
asp_hole = f._emit_raw("SHAPE_ASPECT('round_hole','blind hole feature',#9055,.T.)")
asp_host = f._emit_raw("SHAPE_ASPECT('host_part','host part reference',#9055,.T.)")

# ── Two DIMENSIONAL_SIZEs (byte assertion: count == 2) ───────────────────────
# Defect: hole depth 50mm far exceeds host part thickness 5mm.
ds_depth = f._emit_raw(f"DIMENSIONAL_SIZE(#{asp_hole.eid},'distance')")
ds_thickness = f._emit_raw(f"DIMENSIONAL_SIZE(#{asp_host.eid},'thickness')")

# ── Two MEASURE_REPRESENTATION_ITEMs (byte assertion: count == 2) ─────────────
# Hole depth: 50.0mm — DEFECT: host part is only 5mm thick.
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('hole_depth',LENGTH_MEASURE(50.0),#9056)"
)
# Host part thickness: 5.0mm.
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('part_thickness',LENGTH_MEASURE(5.0),#9056)"
)
