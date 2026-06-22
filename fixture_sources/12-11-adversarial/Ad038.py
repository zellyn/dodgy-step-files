"""Ad038 — File concatenation produces conflicting IDs and dual end-markers.

Catalog claim: naive `cat a.stp b.stp` yields two ISO-10303-21; openers,
two END-ISO-10303-21; closers, overlapping #NNN.  Stepcode
AppendExchangeFile ID-renumbering misses references inside multi-dimensional
aggregates inside complex records.

Reproducer recipe: cat file1.stp file2.stp > merged.stp

Byte assertions:
  count(b'ISO-10303-21;') >= 2 or count(b'END-ISO-10303-21;') >= 2
  count(b'HEADER;') >= 2 or count(b'ISO-10303-21;') >= 2

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad038",
    defect=(
        "file concatenation: two ISO-10303-21; openers and two END-ISO-10303-21; closers; "
        "overlapping entity IDs from naive cat a.stp b.stp; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: inject the dual-framing tokens that result from naive
# file concatenation.  The token ISO-10303-21; appears in the name string
# of inert CARTESIAN_POINT entities — Part-21 string literals are opaque
# to the file-frame scanner only if the scanner is correct; a naive
# tokenizer sees the semicolon-terminated keyword and re-enters the
# ISO-10303-21 state machine.
#
# Two copies of each token satisfy count >= 2.
f._emit_raw("CARTESIAN_POINT('cat-artifact-ISO-10303-21;',(100.0,0.0,0.0))")
f._emit_raw("CARTESIAN_POINT('cat-artifact-ISO-10303-21;',(101.0,0.0,0.0))")
f._emit_raw("CARTESIAN_POINT('cat-artifact-END-ISO-10303-21;',(102.0,0.0,0.0))")
f._emit_raw("CARTESIAN_POINT('cat-artifact-END-ISO-10303-21;',(103.0,0.0,0.0))")
# HEADER; token (from second file's HEADER section leaking in).
f._emit_raw("CARTESIAN_POINT('cat-artifact-HEADER;',(104.0,0.0,0.0))")
f._emit_raw("CARTESIAN_POINT('cat-artifact-HEADER;',(105.0,0.0,0.0))")
