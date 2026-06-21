"""Wr003 — Final `END-ISO-10303-21;` without trailing newline.

Catalog claim: The closing `END-ISO-10303-21;` token is emitted without a
trailing newline. The spec does not require one, so the file is well-formed.
But concatenation of two such files produces `END-ISO-10303-21;ISO-10303-21;`
on a single line, tripping scripts that grep for `^ISO-10303-21;`.

Reproducer recipe: Part-21 file ending with the bytes `END-ISO-10303-21;`
and no `0x0A` after.

Byte assertions:
  bytes_ends_with(b'END-ISO-10303-21;')
  not bytes_ends_with(b'\\n')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr003",
    defect=(
        "Final END-ISO-10303-21; without trailing newline; "
        "the closing END-ISO-10303-21; token is emitted without a trailing newline; "
        "the spec does not require one (it requires only the closing marker), "
        "so the file is well-formed; "
        "but concatenation of two such files produces END-ISO-10303-21;ISO-10303-21; "
        "on a single line, which trips a class of crude scripts that grep for ^ISO-10303-21;; "
        "older Siemens NX export and several in-house writers; "
        "a POSIX-text-file convention (text files end with newline) "
        "but not a Part-21 requirement; "
        "expected kernel behavior: heal and accept; "
        "parsers normalize / accept this form (the spec permits it); "
        "synonyms: can't concat two STEPs, POSIX text-file rule violated, "
        "no newline at end of file, STEP file missing trailing newline"
    ),
)


def _render_no_trailing_newline() -> str:
    """Return a string that does NOT end with \\n (the defect)."""
    return (
        "ISO-10303-21;\n"
        "/* Wr003: END-ISO-10303-21; has no trailing newline */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr003 - no trailing newline after END-ISO-10303-21;'),'2;1');\n"
        "FILE_NAME('Wr003.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: the file terminates immediately after the semicolon, no 0x0A */\n"
        "#1=CARTESIAN_POINT('p0',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "#3=CARTESIAN_POINT('p2',(1.,1.,0.));\n"
        "#4=GEOMETRIC_CURVE_SET('no-newline',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;"  # NO trailing \n — this is the defect
    )


def _write_no_trailing_newline(path) -> None:
    content = _render_no_trailing_newline()
    # Write as bytes to ensure Python's universal-newline handling doesn't add one.
    Path(path).write_bytes(content.encode("utf-8"))


f.render = _render_no_trailing_newline  # type: ignore[method-assign]
f.write = _write_no_trailing_newline  # type: ignore[method-assign]
