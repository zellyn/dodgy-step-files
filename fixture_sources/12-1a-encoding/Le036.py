"""Le036 — Round-trip loss of \\X2\\ content through XML / DB layer.

Catalog claim: A toolchain that decodes \\X2\\…\\X0\\ into UTF-8 internally and
re-encodes for export must round-trip the original Unicode characters. Several
vendors lost backslashes (OCCT 7.5 regression) or replaced rare code points
with '?' when the storage layer (XML, SQL VARCHAR(..)) silently truncated.

Reproducer recipe:
  PRODUCT name containing literal backslashes ('C:\\path\\file') or rare CJK
  code points; export and re-import.

Byte assertions:
  contains(b'\\\\X4\\\\')
  contains(b'\\\\X2\\\\')
  contains(b'\\\\\\\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le036",
    defect=(
        "Round-trip loss of \\X2\\ Unicode content through XML / DB storage layer; "
        "ISO 10303-21 §6.4.3.3: \\X2\\…\\X0\\ encodes UTF-16BE code units; "
        "OCCT 7.5 regression (commit 475da0f) dropped backslashes during re-export; "
        "SQL VARCHAR or XML attribute storage silently truncates rare CJK/SMP code points, "
        "replacing them with '?' or dropping bytes beyond the column width; "
        "this fixture represents the corrupted re-export: PRODUCT name originally carried "
        "backslash path 'C:\\\\path\\\\file' and rare SMP character via \\X4\\; "
        "corrupted output: backslashes lost, \\X4\\ supplementary plane character "
        "replaced with '?' — the re-exported file differs from the original content; "
        "kernel must preserve exact Unicode through encode/decode/storage cycles; "
        "heal and accept: do not silently lose Unicode content on round-trip; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject PERSON entities that demonstrate the round-trip
# loss scenario.  The file represents the *corrupted* re-export output:
#
# PERSON #8997: name uses \\X2\\ to encode a CJK character (U+4E2D, Chinese 中)
#   alongside a literal backslash sequence — the original had 'C:\\path\\中' but
#   after the XML layer the backslashes were dropped, leaving '\\X2\\4E2D\\X0\\'.
#   The double-backslash (\\\\) represents a literal backslash character in STEP.
#
# PERSON #8998: name uses \\X4\\ to encode a supplementary-plane character
#   (U+1F4C4, DOCUMENT emoji) that was partially corrupted by a VARCHAR(255)
#   column; the \\X4\\0001F4C4\\X0\\ sequence exercises the \\X4\\ assertion.
#
# PERSON #8999: name with literal backslash '\\\\' (double-backslash in STEP
#   represents a single backslash) — exercises the contains(b'\\\\') assertion.
#
# Satisfies:
#   contains(b'\\X4\\')  — PERSON #8998
#   contains(b'\\X2\\')  — PERSON #8997
#   contains(b'\\\\')    — PERSON #8997 and #8999

_original_render = f.render


def _render_with_roundtrip_loss() -> str:
    text = _original_render()
    person_lines = (
        # \\X2\\ CJK + literal backslash — backslash = \\\\ in STEP encoding
        "#8997=PERSON('C:\\\\\\X2\\4E2D\\X0\\path','x2-cjk-with-backslash','');\n"
        # \\X4\\ supplementary plane character (U+1F4C4) — 8-hex-digit form
        "#8998=PERSON('\\X4\\0001F4C4\\X0\\','x4-supplementary-plane','');\n"
        # Literal backslash only — double-backslash in STEP
        "#8999=PERSON('C:\\\\path\\\\file','literal-backslash-path','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_roundtrip_loss  # type: ignore[method-assign]
