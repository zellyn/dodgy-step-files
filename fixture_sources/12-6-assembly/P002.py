"""P002 — Non-UTF-8 (GB18030 / locale code page) in string literals.

Catalog claim: files from SolidWorks on a Chinese-locale Windows install write
STEP-21 string literals like SHAPE_REPRESENTATION ('海绵2', ..) using GB18030
bytes directly instead of the `\\X2\\…\\X0\\` Unicode escape sequences mandated
by the spec. Readers assuming UTF-8 produce mojibake in object labels;
round-tripping then corrupts the saved project document.

The defect: a NEXT_ASSEMBLY_USAGE_OCCURRENCE name field carries a
`\\X2\\6D77\\X0\\\\X2\\7EF5\\X0\\2` escape sequence (the STEP-21 encoding of
Chinese "海绵2" = "sponge 2"). A compliant reader must decode this correctly;
a reader that passes raw bytes through without decoding will mojibake the label.
A second PRODUCT entity uses raw Unicode chars (which encode to multibyte UTF-8),
simulating a producer that wrote raw locale bytes instead of \\X2\\ sequences.

Byte assertions:
  contains(b'\\\\X2\\\\') or matches(rb"[\\x80-\\xff]")

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P002",
    defect=(
        "NAUO name field carries \\X2\\ STEP-21 Unicode escapes for Chinese '海绵2'; "
        "additional PRODUCT entity uses raw Unicode (multi-byte UTF-8) to simulate "
        "GB18030 locale bytes written without \\X2\\ escaping; "
        "readers assuming UTF-8 pass-through produce mojibake in object labels; "
        "round-trip corrupts project document; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point in GEOMETRIC_CURVE_SET so that readers
# that somehow parse past the encoding defect still yield empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Inject defect entities via render() override.
#
# NAUO name: '\\X2\\6D77\\X0\\\\X2\\7EF5\\X0\\2'
#   In the STEP file this is the literal text:  \X2\6D77\X0\\X2\7EF5\X0\2
#   which is the STEP-21 encoding of U+6D77 U+7EF5 '2' = "海绵2" (sponge 2).
#   satisfies: contains(b'\\X2\\')
#
# PRODUCT name: '海绵2' written as raw UTF-8 multi-byte bytes (0xE6 0xB5 0xB7
#   0xE7 0xBB 0xB5 0x32) — simulates a SolidWorks Chinese-locale export that
#   wrote GB18030 bytes directly.
#   satisfies: matches(rb"[\x80-\xff]")  (UTF-8 multibyte bytes ≥ 0x80)

_original_render = f.render


def _render_with_gb18030():
    text = _original_render()
    # NAUO with \X2\ escapes (correct STEP-21 form).
    # In Python the string '\\X2\\6D77\\X0\\\\X2\\7EF5\\X0\\2' renders as the
    # STEP-21 text:  \X2\6D77\X0\\X2\7EF5\X0\2
    nauo_line = (
        "#8998=NEXT_ASSEMBLY_USAGE_OCCURRENCE("
        "'1',"
        "'\\X2\\6D77\\X0\\\\X2\\7EF5\\X0\\2',"
        "'',"
        "#9054,$,$);\n"
    )
    # PRODUCT whose name is the Chinese characters 海绵 written directly as
    # Unicode (encodes to raw UTF-8 multibyte bytes ≥ 0x80 in the .stp file).
    product_line = "#8999=PRODUCT('海绵2','sponge2','',(#9000));\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + nauo_line + product_line + text[idx:]


f.render = _render_with_gb18030  # type: ignore[method-assign]
