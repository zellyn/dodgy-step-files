"""Lh005 — FILE_DESCRIPTION/FILE_NAME/FILE_SCHEMA arity mismatch (extra or missing attributes).

Catalog claim: FILE_NAME requires 7 attributes; FILE_DESCRIPTION 2; FILE_SCHEMA 1 (a list).
This fixture emits a FILE_NAME with 8 arguments (one extra) — a common exporter bug where
an extra metadata field is appended to the end of FILE_NAME. Bug-reporter language:
"FILE_NAME wrong number of attributes", "FILE_SCHEMA arity mismatch",
"FILE_DESCRIPTION extra attribute", "header record with too few parameters".

Reproducer recipe: FILE_NAME('a','b',('c'),('d'),'e','f','g','h'); (8 args; expected 7).

Byte assertions:
  matches(rb'FILE_NAME\\([^;]*\\);')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh005",
    defect=(
        "FILE_NAME arity mismatch (extra attribute appended beyond the required 7); "
        "input: FILE_NAME record carries 8 arguments instead of the required 7; "
        "ISO 10303-21 §8 specifies FILE_NAME with exactly 7 attributes: "
        "name, time_stamp, author(list), organization(list), "
        "preprocessor_version, originating_system, authorisation; "
        "a common exporter bug appends an extra metadata string (e.g. a build-tag or "
        "file-format-version) as an 8th argument, causing strict parsers to fail attribute "
        "counting and reject the header record; "
        "produced by minimalist exporters and hand-rolled writers that add non-standard "
        "tracking fields to FILE_NAME; "
        "expected kernel behavior: reject with a precise 'attribute count mismatch' diagnostic "
        "naming the field (FILE_NAME expects 7, got 8); "
        "see also: Lh004; "
        "synonyms: FILE_NAME wrong number of attributes, FILE_SCHEMA arity mismatch, "
        "FILE_DESCRIPTION extra attribute, header record with too few parameters, "
        "FILE_SCHEMA single string instead of list"
    ),
)


def _render_lh005() -> str:
    """Render a Part-21 where FILE_NAME has 8 arguments instead of the required 7."""
    return (
        "ISO-10303-21;\n"
        "/* Lh005: FILE_NAME arity mismatch — 8 attributes supplied, spec requires exactly 7 */\n"
        "/* ISO 10303-21 §8: FILE_NAME(name,timestamp,author,org,preprocessor,system,auth) */\n"
        "/* DEFECT: an extra 8th argument 'build-tag-extra' is appended beyond the 7 required */\n"
        "/* Strict parsers reject; lenient parsers ignore the trailing extra attribute */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh005: FILE_NAME arity mismatch — 8 args instead of 7'),'2;1');\n"
        "/* DEFECT: FILE_NAME has 8 arguments; the 8th 'build-tag-extra' is non-standard */\n"
        "FILE_NAME('Lh005.stp','2026-06-20T00:00:00',('cad-research'),('suite'),"
        "'cad-research-suite','test-system','','build-tag-extra');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('file-name-arity-mismatch-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh005(path) -> None:
    Path(path).write_text(_render_lh005())


f.render = _render_lh005  # type: ignore[method-assign]
f.write = _write_lh005    # type: ignore[method-assign]
