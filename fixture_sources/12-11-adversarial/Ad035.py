"""Ad035 — IGES-style 80-column padding sensitivity (shared translator code paths).

Catalog claim: IGES Directory-Entry uses fixed 80-column records; record with
non-space padding or off-by-one length crashes when directory parser indexes
column 73-80 unconditionally. Relevant because translators commonly share code
paths with STEP.  Reproducer: IGES file whose terminator section reports record
count one greater than physically present.

At STEP corpus level this fixture encodes the structural attack pattern inside
a STEP comment: a run of comment characters wider than 80 columns embedded in
the data section, probing fixed-width-line code paths.  Any line ≥ 75 chars
satisfies the byte assertion.

Byte assertions:
  matches(rb'.{75,}\\n')
  matches(rb'.{72,}')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad035",
    defect=(
        "IGES-style 80-column padding sensitivity via shared translator code paths; "
        "oversized-line attack pattern in STEP data section probes fixed-column-index path; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: entity with a very long name string (≥ 80 chars).
# This ensures the rendered line in the .stp file exceeds 75 characters,
# satisfying: matches(rb'.{75,}\n') and matches(rb'.{72,}').
#
# IGES column-79/80 OOB read is triggered when the translator's IGES reader
# (shared with the STEP reader's line-tokeniser) receives a line longer than
# 80 chars; the fixed-column indexer writes column 73-80 without length check.
# At fixture scale the STEP corpus demonstrates this via a long-named entity.

padding = "X" * 120   # 120-char string → rendered line ≫ 80 cols
f._emit_raw(
    f"CARTESIAN_POINT('{padding}',(1.0,2.0,3.0))"
)

# Second instance with 80-column non-space suffix (all digits, simulating
# IGES sequence-number field in wrong position).
iges_cols = "Y" * 72 + "99999999"   # 80 chars in the string value
f._emit_raw(
    f"CARTESIAN_POINT('{iges_cols}',(4.0,5.0,6.0))"
)
