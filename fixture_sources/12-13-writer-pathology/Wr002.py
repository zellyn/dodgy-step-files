"""Wr002 — Mixed CRLF and LF line endings within one file.

Catalog claim: The HEADER section uses CRLF (`0x0D 0x0A`) line terminators
while the DATA section uses bare LF (`0x0A`), or any other inconsistent mix
within one file.

Reproducer recipe: HEADER section terminated with `\\r\\n`, DATA section
terminated with `\\n`.

Byte assertions:
  contains(b'\\r\\n') and contains(b'\\n')
  count(b'\\r') >= 1

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr002",
    defect=(
        "Mixed CRLF and LF line endings within one file; "
        "the HEADER section uses CRLF (0x0D 0x0A) line terminators "
        "while the DATA section uses bare LF (0x0A); "
        "Windows-hosted writers that build the HEADER block in-memory (CRLF) "
        "and append the DATA block from a streamed buffer (LF), or vice versa; "
        "spec-conforming parsers ignore line-ending choice (whitespace); "
        "but tools that count lines for diagnostics report misleading line numbers, "
        "some text editors display the file as binary, "
        "and content-hash-based caches see the file as different from a normalised copy; "
        "expected kernel behavior: read tolerantly; "
        "treat any of \\n, \\r\\n, or \\r (classic Mac) as a line terminator; "
        "synonyms: line numbers in error messages are wrong, "
        "file shows up as binary in editor, STEP from Windows opens weird on Mac, "
        "weird line endings, mixed CRLF LF in STEP file"
    ),
)


def _render_mixed_line_endings() -> str:
    """Return string with CRLF in HEADER, LF in DATA (will be encoded to bytes)."""
    # We return a plain str but the write method will encode raw bytes.
    # This render is not byte-accurate; write() is the source of truth.
    return (
        "ISO-10303-21;\r\n"
        "/* Wr002: HEADER uses CRLF, DATA uses LF */\r\n"
        "HEADER;\r\n"
        "FILE_DESCRIPTION(('Wr002 - mixed CRLF/LF line endings'),'2;1');\r\n"
        "FILE_NAME('Wr002.stp','2026-06-20T00:00:00',('auto-generated'),(''),\r\n"
        "  'auto-generated','','');\r\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\r\n"
        "ENDSEC;\r\n"
        "DATA;\n"
        "/* Defect: DATA section switches to LF-only line endings */\n"
        "#1=CARTESIAN_POINT('p0',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "#3=CARTESIAN_POINT('p2',(1.,1.,0.));\n"
        "#4=CARTESIAN_POINT('p3',(0.,1.,0.));\n"
        "#5=GEOMETRIC_CURVE_SET('mixed-endings',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_mixed_line_endings(path) -> None:
    content = _render_mixed_line_endings()
    # Write as raw bytes to preserve the mixed CRLF/LF exactly.
    Path(path).write_bytes(content.encode("utf-8"))


f.render = _render_mixed_line_endings  # type: ignore[method-assign]
f.write = _write_mixed_line_endings  # type: ignore[method-assign]
