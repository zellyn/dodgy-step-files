"""Wr004 — Tab characters used for line continuation indentation inconsistently.

Catalog claim: Continuation lines for long records mix TAB (0x09) and SPACE
(0x20) for indentation, or use TAB for some continuations and 2-SPACE for
others within the same file.  Parsers don't care; humans diffing or reviewing
exports do.

Reproducer recipe: a long argument list where some continuation lines start
with a TAB and others start with two SPACEs.

Byte assertions:
  matches(rb'\\n\\t') and matches(rb'\\n  ')
  contains(b'\\t')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr004",
    defect=(
        "Tab characters used for line continuation indentation inconsistently; "
        "continuation lines for long records mix TAB (0x09) and SPACE (0x20) "
        "for indentation, or use TAB for some continuations and 2-SPACE for "
        "others within the same file; "
        "parsers don't care (whitespace outside string literals is insignificant); "
        "humans diffing or reviewing exports find the file unreadable in editors "
        "that display tabs as wide columns; "
        "KiCad PCB-to-STEP exporter and homegrown writers; "
        "expected kernel behavior: heal and accept; "
        "normalize by ignoring the whitespace; "
        "synonyms: tabs and spaces mixed, indentation inconsistent, "
        "looks bad in editor, diff is unreadable"
    ),
)


def _render_tab_mixed_indent() -> str:
    """Return a Part-21 string mixing TAB and SPACE on continuation lines."""
    # TAB character
    TAB = "\t"
    lines = [
        "ISO-10303-21;",
        "/* Wr004: continuation lines mix TAB and SPACE indentation */",
        "HEADER;",
        "FILE_DESCRIPTION(('Wr004 - mixed tab/space indentation on continuation lines'),'2;1');",
        "FILE_NAME('Wr004.stp','2026-06-20T00:00:00',('auto-generated'),(''),",
        "  'auto-generated','','');",
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));",
        "ENDSEC;",
        "DATA;",
        "/* Defect: continuation lines alternate between TAB and 2-SPACE indentation */",
        # Long entity split across continuation lines: first continuation uses TAB
        "#1=CARTESIAN_POINT('origin',",
        TAB + "(0.,0.,0.));",
        # Second entity: continuation uses 2-SPACE
        "#2=CARTESIAN_POINT('corner',",
        "  (1.,1.,1.));",
        # Third: TAB again
        "#3=DIRECTION('z-axis',",
        TAB + "(0.,0.,1.));",
        # Fourth: 2-SPACE
        "#4=DIRECTION('x-axis',",
        "  (1.,0.,0.));",
        # Fifth: TAB
        "#5=VECTOR('v',#3,",
        TAB + "1.);",
        "#6=GEOMETRIC_CURVE_SET('mixed-indent',());",
        "ENDSEC;",
        "END-ISO-10303-21;",
        "",
    ]
    return "\n".join(lines)


def _write_tab_mixed_indent(path) -> None:
    content = _render_tab_mixed_indent()
    # Write as bytes to preserve TAB characters exactly.
    Path(path).write_bytes(content.encode("utf-8"))


f.render = _render_tab_mixed_indent  # type: ignore[method-assign]
f.write = _write_tab_mixed_indent  # type: ignore[method-assign]
