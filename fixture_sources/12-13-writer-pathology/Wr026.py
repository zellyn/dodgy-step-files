"""Wr026 — Vendor-specific FILE_DESCRIPTION strings that downstream readers special-case.

Catalog claim: producer writes FILE_DESCRIPTION(('CAD-System-X v12.4.1'),'2;1').
Some receivers contain heuristic special-casing keyed on vendor strings.
A minor wording change ("CAD-System X" with a space vs "CAD-System-X" with
a hyphen) silently disables the fix-up.

Reproducer recipe: a fixture with FILE_DESCRIPTION(('CAD-System-X v12.4.1'),'2;1')
and a comment noting the receiver special-cases the exact spelling.

Byte assertions:
  contains(b'CAD-System-X')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr026",
    defect=(
        "Vendor-specific FILE_DESCRIPTION strings that downstream readers special-case; "
        "producer writes CAD-System-X v12.4.1 in FILE_DESCRIPTION.description; "
        "some receivers contain heuristic special-casing keyed on vendor strings; "
        "they apply a fix-up filter only if the vendor string matches exactly; "
        "a minor wording change (CAD-System X with space vs CAD-System-X with hyphen) "
        "silently disables the fix-up; "
        "expected kernel behavior: normalize / avoid behaviour-altering vendor sniffing; "
        "if vendor-specific compatibility is needed, expose it as an explicit user opt-in; "
        "synonyms: STEP file behaves differently after vendor renamed product, "
        "kernel detects wrong vendor, vendor sniffing failed"
    ),
)


def _render_wr026() -> str:
    """Render a Part-21 with vendor-specific FILE_DESCRIPTION string."""
    return (
        "ISO-10303-21;\n"
        "/* Wr026: vendor-specific FILE_DESCRIPTION that downstream readers special-case */\n"
        "/* Receiver has heuristic: if description contains 'CAD-System-X', apply fix-up */\n"
        "/* A rename to 'CAD-System X' (space instead of hyphen) silently breaks the fix-up */\n"
        "HEADER;\n"
        "/* DEFECT: vendor string 'CAD-System-X v12.4.1' triggers receiver heuristics */\n"
        "FILE_DESCRIPTION(('CAD-System-X v12.4.1'),'2;1');\n"
        "FILE_NAME('Wr026.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: minimal GEOMETRIC_CURVE_SET (no product chain needed) */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('vendor-sniff-target',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr026(path) -> None:
    Path(path).write_text(_render_wr026())


f.render = _render_wr026  # type: ignore[method-assign]
f.write = _write_wr026    # type: ignore[method-assign]
