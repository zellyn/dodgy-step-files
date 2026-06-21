"""Lh030 — Lower-case name field values where Recommended-Practices keywords defined.

Catalog claim: Several Recommended Practices specify lower-case keyword strings
as canonical attribute values (e.g. 'composite' on
geometric_tolerance_relationship). Producers that emit these in mixed or upper
case break receivers that string-compare strictly. Adjacent to Lh018 but
specifically about RP-defined string attribute values rather than Part-21
keywords.
Bug-reporter language: "lower-case enum value in name field", "Recommended
Practices keyword case mismatch", "composite spelled in mixed case", "STEP
attribute string-compare fails on case", "RP-defined keyword not lower-case".

Reproducer recipe:
  GEOMETRIC_TOLERANCE_RELATIONSHIP('Composite',..); instead of 'composite'.

Byte assertions:
  contains(b"GEOMETRIC_TOLERANCE_RELATIONSHIP('Composite'")
  contains(b"'Composite'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh030",
    defect=(
        "Lower-case name field values where Recommended-Practices keywords are defined; "
        "input: GEOMETRIC_TOLERANCE_RELATIONSHIP('Composite',..) emits 'Composite' in mixed case "
        "instead of the RP-canonical lower-case 'composite'; "
        "several Recommended Practices specify lower-case keyword strings as canonical attribute values; "
        "producers that emit these in mixed or upper case break receivers that string-compare strictly; "
        "this is adjacent to Lh018 but specifically about RP-defined string attribute values "
        "rather than Part-21 keywords; "
        "OCC silently accepts (no diagnostic, empty result) — outside catalog allowed set ({heal}); "
        "expected kernel behavior: heal and accept with case-insensitive match for documented "
        "RP keyword values on import; warn; emit canonical lower-case on export; "
        "see also: Lh018, Pmi043; "
        "synonyms: lower-case enum value in name field, Recommended Practices keyword case mismatch, "
        "composite spelled in mixed case, STEP attribute string-compare fails on case, "
        "RP-defined keyword not lower-case"
    ),
)


def _render_lh030() -> str:
    """Render a Part-21 with 'Composite' in mixed case where RP requires 'composite'."""
    return (
        "ISO-10303-21;\n"
        "/* Lh030: mixed-case RP keyword value — 'Composite' instead of 'composite' */\n"
        "/* DEFECT: GEOMETRIC_TOLERANCE_RELATIONSHIP uses 'Composite' (mixed case) */\n"
        "/* Recommended Practices require canonical lower-case 'composite' */\n"
        "/* Receivers that string-compare strictly fail; OCC silently accepts empty */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh030: mixed-case RP keyword Composite instead of composite'),'2;1');\n"
        "FILE_NAME('Lh030.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.5),#6);\n"
        "#6=( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );\n"
        "#7=GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE($,$,#5,#8,(#9));\n"
        "#8=GEOMETRIC_CURVE_SET('rp-case-mismatch-shape',(#1,#2));\n"
        "#9=DATUM_REFERENCE(1,'A');\n"
        "/* DEFECT: 'Composite' is mixed-case; RP canonical form is 'composite' */\n"
        "#10=GEOMETRIC_TOLERANCE_RELATIONSHIP('Composite','composite tolerance pair',#7,#7);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh030(path) -> None:
    Path(path).write_text(_render_lh030())


f.render = _render_lh030  # type: ignore[method-assign]
f.write = _write_lh030    # type: ignore[method-assign]
