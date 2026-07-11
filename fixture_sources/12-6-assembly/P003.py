"""P003 — Control characters / illegal-XML bytes in name strings.

Catalog claim: a STEP file whose PRODUCT / NEXT_ASSEMBLY_USAGE_OCCURRENCE name
fields contain bytes illegal in downstream serialization (control chars
\\x00–\\x1F, lone surrogates, unescaped </&/>, invalid UTF-8 continuation
bytes) imports without complaint, but save-and-reopen of the receiving
document fails to parse.

The defect: a NEXT_ASSEMBLY_USAGE_OCCURRENCE name field contains raw control
bytes embedded via STEP-21 \\X\\HH escapes (the Ed.2 mechanism for encoding
8-bit characters). Specifically, \\X\\01 (SOH), \\X\\08 (backspace), and
\\X\\1F (unit separator) appear in entity labels — bytes that are illegal in
XML serialization. An importing kernel must sanitize / escape these at parse
time or reject with a warning.

Byte assertions:
  matches(rb'\\\\X\\\\[0-9A-Fa-f]{2}') or matches(rb"[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f]")

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P003",
    defect=(
        "PRODUCT / NAUO name fields contain \\X\\ single-byte escape sequences "
        "encoding control characters (SOH=\\X\\01, BS=\\X\\08, US=\\X\\1F) "
        "that are illegal in XML serialization; "
        "STEP import succeeds silently but downstream save-and-reopen of the "
        "receiving document fails to parse the serialized XML; "
        "kernel must sanitize/escape names at parse time or reject with warning; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point in GEOMETRIC_CURVE_SET so that readers
# that parse past the defect still yield empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Inject defect entities via render() override.
#
# \\X\\01 is the STEP-21 Ed.2 escape for byte 0x01 (SOH) — illegal in XML.
# \\X\\08 is the STEP-21 Ed.2 escape for byte 0x08 (BS)  — illegal in XML.
# \\X\\1F is the STEP-21 Ed.2 escape for byte 0x1F (US)  — illegal in XML.
#
# In the .stp file the text appears as e.g.:
#   'part\X\01name'   (SOH embedded in a STEP string)
#
# Satisfies:
#   matches(rb'\\X\\[0-9A-Fa-f]{2}')  — the \\X\\01 / \\X\\08 / \\X\\1F sequences

_original_render = f.render


def _render_with_control_chars():
    text = _original_render()
    # NAUO with control-byte escape in name — the STEP-21 text is 'kicad\X\01part'
    # (\X\01 = SOH, 0x01, illegal in XML downstream serialization).
    nauo_line = (
        "#8997=NEXT_ASSEMBLY_USAGE_OCCURRENCE("
        "'1',"
        "'kicad\\X\\01part',"
        "'TO-92\\X\\1Ffootprint',"
        "#9054,$,$);\n"
    )
    # PRODUCT whose name embeds a backspace (0x08) via \X\08 escape.
    product_line = (
        "#8998=PRODUCT("
        "'ctrl\\X\\08name',"
        "'ctrl-char-label',"
        "'',"
        "(#9000));\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + nauo_line + product_line + text[idx:]


f.render = _render_with_control_chars  # type: ignore[method-assign]
