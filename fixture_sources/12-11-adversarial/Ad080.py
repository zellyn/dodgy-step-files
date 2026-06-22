"""Ad080 — Two DATA sections with colliding #NNN id space (token-boundary attack).

Catalog claim: two DATA;…ENDSEC; sections appear in one file (illegal in
Ed.2). Both DATA sections reuse the identical entity-id range #1..#N, so
any reader that builds a single #-keyed map silently overwrites the first
section's entities with the second. Greedy regex parsers may also match
across the section boundary.

Reproducer recipe: ISO 10303-21 file with two DATA;…ENDSEC; blocks, each
containing overlapping entity ids and terminated by ENDSEC; followed
immediately by DATA;.

Byte assertions:
  count(b'DATA;') >= 2 or count(b'ENDSEC;DATA;') >= 1
  count(b'ENDSEC;') >= 2 or count(b'DATA;') >= 2

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad080",
    defect=(
        "two DATA sections in one file: both sections reuse entity-id range #1..#N; "
        "readers with a single #-keyed map silently overwrite first section; "
        "greedy regex parsers may match across ENDSEC; boundary; "
        "illegal per ISO 10303-21 Ed.2; See also Lh024, Ls024; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: inject a second DATA section by overriding _render_footer.
# We capture the standard render, then append a second DATA…ENDSEC block
# that reuses the same entity ids (#1, #2) to demonstrate the id-collision.
#
# The standard render() produces:
#   HEADER; … ENDSEC;
#   DATA;
#   #1 = …;
#   …
#   ENDSEC;
#   END-ISO-10303-21;
#
# We override render() to insert a second DATA;…ENDSEC; before the final
# END-ISO-10303-21;, satisfying:
#   count(b'DATA;') >= 2  and  count(b'ENDSEC;') >= 2
#   count(b'ENDSEC;DATA;') >= 1  (the ENDSEC;DATA; boundary)

_original_render = f.render

def _render_with_double_data():
    text = _original_render()
    # Locate the terminal END-ISO-10303-21; and insert the second DATA block
    # immediately before it, with ids that collide with the first section.
    tail = "END-ISO-10303-21;"
    assert tail in text, f"Expected {tail!r} in rendered STEP"
    idx = text.index(tail)
    second_section = (
        "DATA;\n"
        "#1=CARTESIAN_POINT('shadow_point',(9.,9.,9.));\n"
        "#2=GEOMETRIC_CURVE_SET('shadow_gcs',(#1));\n"
        "ENDSEC;\n"
    )
    # Satisfies: count(b'ENDSEC;DATA;') >= 1 (rendered as "ENDSEC;\nDATA;" —
    # strip newlines in the byte test; the count(b'DATA;') >= 2 check covers both).
    return text[:idx] + second_section + text[idx:]

f.render = _render_with_double_data  # type: ignore[method-assign]
