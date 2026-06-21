"""Pmi060 — Tolerance datum description NULL on re-export.

Catalog claim: Re-exporting a model with empty datum description
NULL-dereferences inside the writer; receivers must default to empty
description rather than crash.

Reproducer recipe: XCAF document with DATUM_FEATURE whose description is
empty string; POSITION_TOLERANCE and DATUM_SYSTEM referencing it.

Byte assertions:
  contains(b'DATUM_FEATURE')
  contains(b'POSITION_TOLERANCE')
  contains(b'DATUM_SYSTEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi060",
    defect=(
        "DATUM_FEATURE has empty description (NULL-equivalent empty string); "
        "OCCT writer NULL-dereferences on re-export when datum description is "
        "empty; receivers must default the description to empty string and never "
        "crash; silently accepting or crashing is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# ── Datum feature with empty description (the defect) ────────────────────────
datum_feat = f._emit_raw(
    "DATUM_FEATURE('datum_A','',#9055,.T.)"
)

# ── Datum system referencing the datum feature ────────────────────────────────
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('datum_frame','primary datum frame',"
    f"(#{datum_feat.eid}),#9055,.T.)"
)

# ── Shape aspect for the toleranced surface ───────────────────────────────────
tol_aspect = f._emit_raw(
    "SHAPE_ASPECT('toleranced_surface','',#9055,.T.)"
)

# ── Geometric tolerance: position tolerance referencing the datum ──────────────
# TOLERANCE_VALUE_WITH_UNIT: value 0.05 mm using the length unit from chain.
tol_val = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('tol_val',LENGTH_MEASURE(0.05),#9056)"
)
pos_tol = f._emit_raw(
    f"POSITION_TOLERANCE('position','positional tolerance 0.05mm',"
    f"#{tol_val.eid},#{tol_aspect.eid})"
)
