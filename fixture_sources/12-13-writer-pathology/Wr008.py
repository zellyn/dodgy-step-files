"""Wr008 — Excessive trailing zeros in numeric output.

Catalog claim: Every numeric coordinate is emitted with 17 or more decimal
digits, padded with trailing zeros where the underlying value has fewer
significant digits (`1.0` is emitted as `1.00000000000000000`). The file
inflates 2-3× over what minimal-form output would produce. Spec-conforming,
but bandwidth- and storage-hostile.

Reproducer recipe: CARTESIAN_POINTs with coordinates such as
`(1.00000000000000000,2.50000000000000000,0.00000000000000000)`.

Byte assertions:
  matches(rb'\\d\\.0{15,}')
  matches(rb'\\.0{14,}')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr008",
    defect=(
        "Excessive trailing zeros in numeric output; "
        "every numeric coordinate is emitted with 17 or more decimal digits, "
        "padded with trailing zeros where the underlying value has fewer significant digits "
        "(1.0 is emitted as 1.00000000000000000); "
        "the file inflates 2-3 times over what minimal-form output would produce; "
        "writers using printf(\"%.20f\", ..) or printf(\"%.17g\", ..) indiscriminately "
        "on every coordinate; "
        "spec-conforming, but bandwidth- and storage-hostile; "
        "cousin of Wr006 from the opposite direction; "
        "expected kernel behavior: heal and accept; "
        "parse normally; a re-emit policy may normalize / shorten to minimal "
        "round-trip-safe form (%.17g shortened to the smallest digit-count that round-trips); "
        "synonyms: STEP file unnecessarily huge, 20 digits for every zero, "
        "compresses 95 percent, exchange file size grew 3x without geometry change"
    ),
)


def _render_excessive_trailing_zeros() -> str:
    """Return a Part-21 string where every coordinate has 17+ decimal places."""
    return (
        "ISO-10303-21;\n"
        "/* Wr008: excessive trailing zeros — 17 decimal digits on every coordinate */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr008 - excessive trailing zeros in numeric output'),'2;1');\n"
        "FILE_NAME('Wr008.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: printf(\"%.17g\") pads every coord with trailing zeros */\n"
        "#1=CARTESIAN_POINT('origin',(0.00000000000000000,0.00000000000000000,0.00000000000000000));\n"
        "#2=CARTESIAN_POINT('unit-corner',(1.00000000000000000,2.50000000000000000,0.50000000000000000));\n"
        "#3=CARTESIAN_POINT('half',(0.50000000000000000,0.25000000000000000,0.12500000000000000));\n"
        "#4=DIRECTION('z-axis',(0.00000000000000000,0.00000000000000000,1.00000000000000000));\n"
        "#5=GEOMETRIC_CURVE_SET('trailing-zeros',(#1,#2,#3));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_excessive_trailing_zeros(path) -> None:
    Path(path).write_bytes(_render_excessive_trailing_zeros().encode("utf-8"))


f.render = _render_excessive_trailing_zeros  # type: ignore[method-assign]
f.write = _write_excessive_trailing_zeros  # type: ignore[method-assign]
