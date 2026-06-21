"""Lh010 — FileImplementationLevel non-canonical value.

Catalog claim: FILE_DESCRIPTION's implementation_level must be one of the canonical conformance
codes '1;1', '2;1', '3;1', '4;1', '4;2', '4;3'. Real files contain '1.0', '2;1;1', '2.1',
the empty string, or vendor branding strings ('Simulia 2018').
Bug-reporter language: "non-canonical implementation_level in FILE_DESCRIPTION",
"STEP conformance code wrong format", "vendor branding in implementation_level",
"1.0 instead of 1;1 in header", "implementation_level overflow".

Reproducer recipe: FILE_DESCRIPTION((''),'Simulia 2018');

Byte assertions:
  contains(b"'Simulia 2018'") or matches(rb"FILE_DESCRIPTION\\([^;]*'1\\.0'")
  contains(b'Simulia') or contains(b"'1.0'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh010",
    defect=(
        "FileImplementationLevel non-canonical value in FILE_DESCRIPTION; "
        "input: FILE_DESCRIPTION implementation_level attribute contains a vendor branding string "
        "'Simulia 2018' instead of one of the canonical conformance codes "
        "('1;1', '2;1', '3;1', '4;1', '4;2', '4;3'); "
        "ISO 10303-21 §8 specifies implementation_level as a conformance class code "
        "in the form MAJOR;MINOR; receivers that parse this field to branch on schema version "
        "or conformance class will fail or produce incorrect results; "
        "vendor branding strings additionally risk fixed-buffer overflow in legacy translators "
        "that assume a short implementation_level field; "
        "produced by exporters that substitute version strings for conformance codes; "
        "expected kernel behavior: warn-and-tolerate when the value is recognizable; "
        "reject overlong values; default to class 1 with a warning if unparseable; "
        "validate length before copy into any fixed-size buffer; "
        "see also: Le020; "
        "synonyms: non-canonical implementation_level in FILE_DESCRIPTION, "
        "STEP conformance code wrong format, vendor branding in implementation_level, "
        "1.0 instead of 1;1 in header, implementation_level overflow"
    ),
)


def _render_lh010() -> str:
    """Render a Part-21 where FILE_DESCRIPTION has a vendor branding string as implementation_level."""
    return (
        "ISO-10303-21;\n"
        "/* Lh010: FILE_DESCRIPTION implementation_level is a vendor branding string */\n"
        "/* ISO 10303-21 §8: implementation_level must be a canonical conformance code */\n"
        "/* Valid codes: '1;1' '2;1' '3;1' '4;1' '4;2' '4;3' */\n"
        "/* DEFECT: 'Simulia 2018' is not a conformance code; receivers cannot parse it */\n"
        "/* Legacy translators with fixed-size buffers risk overflow on long vendor strings */\n"
        "HEADER;\n"
        "/* DEFECT: implementation_level is a vendor branding string, not a conformance code */\n"
        "FILE_DESCRIPTION(('Lh010: non-canonical implementation_level vendor branding string'),'Simulia 2018');\n"
        "FILE_NAME('Lh010.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('non-canonical-impl-level-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh010(path) -> None:
    Path(path).write_text(_render_lh010())


f.render = _render_lh010  # type: ignore[method-assign]
f.write = _write_lh010    # type: ignore[method-assign]
