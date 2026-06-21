"""Wr029 — FILE_DESCRIPTION strings containing newlines or unescaped control characters.

Catalog claim: FILE_DESCRIPTION(('first line\\nsecond line'),'2;1') where the literal
\\n is an embedded newline (actual 0x0A byte), not the two-character escape. Terminates
the string for crude line-based parsers. Spec violation per ISO 10303-21 §6.4.
Bug-reporter language: "STEP file string has line break", "FILE_DESCRIPTION corrupt".

Reproducer recipe: literal FILE_DESCRIPTION(('first line<LF>second line'),'2;1').

Byte assertions:
  matches(rb"FILE_DESCRIPTION\\(\\('[^']*\\n[^']*'")
  matches(rb"FILE_DESCRIPTION\\(\\(\\s*'[^']*\\n")

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr029",
    defect=(
        "FILE_DESCRIPTION strings containing newlines or unescaped control characters; "
        "input: FILE_DESCRIPTION(('first line<LF>second line'),'2;1') where the <LF> "
        "is an actual 0x0A byte embedded inside the string literal (not two-character escape); "
        "terminates the string for crude line-based parsers; "
        "spec violation per ISO 10303-21 §6.4 (control characters in string literals forbidden); "
        "produced by writers that paste user-entered description text into FILE_DESCRIPTION "
        "without escaping line breaks; "
        "expected kernel behavior: reject as malformed per spec; do not silently splice "
        "the broken string back together because the splice point is undefined; "
        "synonyms: STEP file string has line break, FILE_DESCRIPTION corrupt, "
        "string wraps mid-line, embedded newline in STEP string"
    ),
)


def _render_wr029() -> str:
    """Render a Part-21 with embedded literal newline in FILE_DESCRIPTION.

    The 0x0A is injected into the Python string via \\n (Python escape),
    which becomes an actual newline byte when written to disk.
    """
    # The FILE_DESCRIPTION line contains an actual embedded LF (0x0A) byte
    # inside the string literal.  This is the defect.
    header_before = (
        "ISO-10303-21;\n"
        "/* Wr029: FILE_DESCRIPTION with embedded literal newline (0x0A) in string */\n"
        "/* Writers that paste user text into FILE_DESCRIPTION without escaping LF */\n"
        "/* Crude line-based parsers terminate the string at the embedded newline */\n"
        "/* Spec violation: ISO 10303-21 §6.4 forbids control characters in strings */\n"
        "HEADER;\n"
        "/* DEFECT: the FILE_DESCRIPTION string contains a real 0x0A byte mid-string */\n"
        "FILE_DESCRIPTION(('first line\nsecond line'),'2;1');\n"
        "FILE_NAME('Wr029.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('pt',(1.,0.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('newline-header-shape',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )
    return header_before


def _write_wr029(path) -> None:
    # Write as text; the \n in FILE_DESCRIPTION(('first line\nsecond line')...) is a
    # real LF (0x0A) embedded in the string literal on disk.
    Path(path).write_text(_render_wr029())


f.render = _render_wr029  # type: ignore[method-assign]
f.write = _write_wr029    # type: ignore[method-assign]
