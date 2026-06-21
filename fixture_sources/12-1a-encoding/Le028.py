"""Le028 — Stray NUL bytes / DOS \\r\\n line endings inside the file.

Catalog claim: Files transmitted through Windows-aware tools accumulate
stray NUL bytes or CR LF line terminators. Naive scanners that only handle
bare \\n mis-count line numbers or misread tokens.

Reproducer recipe:
  file with CR LF line endings throughout; or stray \\x00 bytes injected
  between tokens.

Byte assertions:
  contains(b'\\r\\n')
  contains(b'\\x00')
  matches(rb'\\x00')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=reject
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le028",
    defect=(
        "Stray NUL bytes and DOS CR LF line endings inside STEP file; "
        "ISO 10303-21 §6.1: line terminators are implementation-defined but "
        "most parsers assume bare LF (0x0A) only; "
        "OCCT lex grammar (StepFile/step.lex:118-119 e3i fix) handles CR; "
        "naive scanners that only handle bare LF mis-count lines on CR LF files; "
        "stray NUL bytes (0x00) between tokens cause lexer abort or token misread; "
        "cross-oracle: pure-Python Part-21 validator rejects with E_NO_MAGIC; "
        "OCCT silently heals CR LF but may reject NUL; "
        "file uses CR LF throughout AND contains stray NUL between tokens; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: override render() to:
#   1. Replace all LF (\n) line endings with CR LF (\r\n) throughout the file.
#   2. Inject a stray NUL byte (0x00) between two tokens in the DATA section.
#
# The NUL byte is placed inside a PERSON entity name to make it clearly
# visible and attributable to the defect class, not a random corruption.
#
# Satisfies:
#   contains(b'\r\n')       — CR LF throughout (step 1)
#   contains(b'\x00')       — NUL in PERSON name (step 2)
#   matches(rb'\x00')       — same NUL byte

_original_render = f.render


def _render_with_crlf_and_nul() -> str:
    text = _original_render()

    # Step 1: inject a stray NUL between PERSON name tokens before converting
    # line endings, so the NUL lands in the DATA section.
    # Place NUL inside a PERSON name to demonstrate mid-token NUL handling.
    nul = "\x00"
    person_line = f"#8997=PERSON('name{nul}with-nul','nul-byte-demo','');\n"

    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    text = text[:idx] + "\n" + person_line + text[idx:]

    # Step 2: replace all bare LF with CR LF to simulate DOS/Windows line endings
    text = text.replace("\n", "\r\n")

    return text


f.render = _render_with_crlf_and_nul  # type: ignore[method-assign]
