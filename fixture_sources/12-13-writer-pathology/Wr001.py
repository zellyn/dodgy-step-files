"""Wr001 — Trailing whitespace on every record line.

Catalog claim: Every record line in the DATA section ends with one or more
ASCII space (0x20) characters before the line terminator. Spec-conforming
parsers accept this (whitespace is insignificant outside string literals),
but downstream tools that diff exports see noise on every line.

Reproducer recipe: minimal Part-21 file where each `#NNN=ENTITY(..);` line
ends with `   ` (three spaces) before `\\n`.

Byte assertions:
  matches(rb' +\\n')
  count(b' \\n') >= 5

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr001",
    defect=(
        "Trailing whitespace on every record line; "
        "every record line in the DATA section ends with ASCII space (0x20) "
        "characters before the line terminator; "
        "spec-conforming parsers accept this (whitespace is insignificant "
        "outside string literals); "
        "but downstream tools that diff exports see noise on every line, "
        "version-control systems show every line as modified on every export, "
        "and crude line-based regex parsers that anchor on ;$ mis-match; "
        "older FreeCAD STEP writer (pre-0.20) and some Pro/E export filters; "
        "expected kernel behavior: read tolerantly; "
        "the spec permits insignificant whitespace anywhere outside string literals; "
        "optionally normalise on re-emit; "
        "synonyms: STEP file has trailing spaces, every line ends with whitespace, "
        "diff is huge but nothing changed, git keeps marking the file dirty"
    ),
)


def _render_trailing_spaces() -> str:
    """Return a Part-21 string where every DATA-section line ends with 3 spaces."""
    sp = "   "  # three trailing spaces
    lines = [
        "ISO-10303-21;",
        "/* Wr001: trailing whitespace on every record line */",
        "HEADER;",
        f"FILE_DESCRIPTION(('Wr001 - trailing whitespace on every data line'),'2;1');",
        f"FILE_NAME('Wr001.stp','2026-06-20T00:00:00',('auto-generated'),(''),",
        "  'auto-generated','','');",
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));",
        "ENDSEC;",
        "DATA;",
        f"/* Defect: every entity line ends with three trailing spaces before \\n */{sp}",
        f"#1=CARTESIAN_POINT('p0',(0.,0.,0.));{sp}",
        f"#2=CARTESIAN_POINT('p1',(1.,0.,0.));{sp}",
        f"#3=CARTESIAN_POINT('p2',(1.,1.,0.));{sp}",
        f"#4=CARTESIAN_POINT('p3',(0.,1.,0.));{sp}",
        f"#5=DIRECTION('zdir',(0.,0.,1.));{sp}",
        f"#6=DIRECTION('xdir',(1.,0.,0.));{sp}",
        f"#7=GEOMETRIC_CURVE_SET('trailing-ws',());{sp}",
        "ENDSEC;",
        "END-ISO-10303-21;",
        "",  # trailing newline
    ]
    return "\n".join(lines)


def _write_trailing_spaces(path) -> None:
    Path(path).write_text(_render_trailing_spaces())


f.render = _render_trailing_spaces  # type: ignore[method-assign]
f.write = _write_trailing_spaces  # type: ignore[method-assign]
