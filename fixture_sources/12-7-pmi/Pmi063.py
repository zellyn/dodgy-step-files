"""Pmi063 — FILE_DESCRIPTION missing references to CAx-IF Recommended Practices.

Catalog claim: When the file uses datum-target / dimension / GD&T /
supplemental-geometry constructs, the FILE_DESCRIPTION header should declare
which CAx-IF RP was followed. Missing this makes RP version disambiguation
impossible.

Reproducer recipe: AP242 PMI file whose FILE_DESCRIPTION carries no RP
citation — only a plain CAD-system identifier string.

Byte assertions:
  contains(b'PLACED_DATUM_TARGET_FEATURE')
  contains(b'DATUM_SYSTEM')
  contains(b'POSITION_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi063",
    defect=(
        "FILE_DESCRIPTION header lists only the CAD system name with no "
        "CAx-IF Recommended Practice citation; AP242 PMI files that use "
        "datum-targets, tolerances, and supplemental-geometry constructs must "
        "declare the RP version (e.g. 'CAx-IF Rec.Pracs.---PMI Rep & Pres---v4.1') "
        "in FILE_DESCRIPTION so receivers can apply the correct interpretation rules; "
        "missing RP citation makes version disambiguation impossible; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Datum target (PLACED_DATUM_TARGET_FEATURE) ────────────────────────────────
datum_target = f._emit_raw(
    "PLACED_DATUM_TARGET_FEATURE('datum_target_A1','datum target A1',"
    "#9055,.T.,'point',1)"
)

# ── Datum system ──────────────────────────────────────────────────────────────
datum_feat = f._emit_raw(
    "DATUM_FEATURE('datum_A','primary datum',#9055,.T.)"
)
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('primary_datum_frame','primary datum',"
    f"(#{datum_feat.eid}),#9055,.T.)"
)

# ── Toleranced shape aspect ───────────────────────────────────────────────────
tol_aspect = f._emit_raw(
    "SHAPE_ASPECT('toleranced_face','',#9055,.T.)"
)

# ── Position tolerance ────────────────────────────────────────────────────────
tol_val = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('tol_val',LENGTH_MEASURE(0.1),#9056)"
)
f._emit_raw(
    f"POSITION_TOLERANCE('position','0.1mm position tol',"
    f"#{tol_val.eid},#{tol_aspect.eid})"
)
