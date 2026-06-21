"""Lh031 — Header recognition relies on FILE_NAME originating-system substring.

Catalog claim: OCCT auto-detects I-DEAS-style non-manifold encoding by
substring-matching the FILE_NAME preprocessor_version field. Misses other
I-DEAS variants whose preprocessor string differs; flags false positives on
tools whose preprocessor mentions "I-DEAS".
Bug-reporter language: "I-DEAS auto-detect by FILE_NAME substring",
"preprocessor_version string match brittle", "false-positive non-manifold
detection", "STEP receiver inferring vendor from header",
"originating-system substring detection".

Reproducer recipe:
  FILE_NAME(..,..,(''),(''),'I-DEAS Master Series 11','','');

Byte assertions:
  contains(b'I-DEAS')
  matches(rb"FILE_NAME\\([^;]*'I-DEAS")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh031",
    defect=(
        "Header recognition relies on FILE_NAME originating-system substring (I-DEAS auto-detect); "
        "input: FILE_NAME with preprocessor_version field set to 'I-DEAS Master Series 11'; "
        "OCCT auto-detects I-DEAS-style non-manifold encoding by substring-matching "
        "the FILE_NAME preprocessor_version field; "
        "this misses I-DEAS variants whose preprocessor string differs and flags false positives "
        "on tools whose preprocessor string merely mentions 'I-DEAS'; "
        "the entity graph (e.g. presence of NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION) "
        "is the correct signal, not a header substring; "
        "OCC silently accepts (no diagnostic, empty result) — outside catalog allowed set ({heal}); "
        "expected kernel behavior: heal and accept by detecting non-manifold encoding from the "
        "entity graph, not from a substring of header metadata; "
        "see also: Lh019; "
        "synonyms: I-DEAS auto-detect by FILE_NAME substring, preprocessor_version string match brittle, "
        "false-positive non-manifold detection, STEP receiver inferring vendor from header, "
        "originating-system substring detection"
    ),
)


def _render_lh031() -> str:
    """Render a Part-21 with I-DEAS substring in FILE_NAME preprocessor_version field."""
    return (
        "ISO-10303-21;\n"
        "/* Lh031: FILE_NAME preprocessor_version contains 'I-DEAS Master Series 11' */\n"
        "/* DEFECT: OCCT auto-detects I-DEAS non-manifold mode by substring match on this field */\n"
        "/* Correct detection: inspect entity graph for NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION */\n"
        "/* This file has no non-manifold entities; auto-detect fires a false positive */\n"
        "/* OCC silently accepts (empty result); catalog requires heal and accept */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh031: I-DEAS substring in FILE_NAME preprocessor_version'),'2;1');\n"
        "/* DEFECT: preprocessor_version field contains I-DEAS substring; triggers false-positive */\n"
        "FILE_NAME('Lh031.stp','2026-06-20T00:00:00',(''),(''),'I-DEAS Master Series 11','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('ideas-false-positive-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh031(path) -> None:
    Path(path).write_text(_render_lh031())


f.render = _render_lh031  # type: ignore[method-assign]
f.write = _write_lh031    # type: ignore[method-assign]
