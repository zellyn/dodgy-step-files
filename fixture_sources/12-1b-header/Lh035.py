"""Lh035 — ANCHOR section publishing the same anchor name twice.

Catalog claim: Edition-3 ANCHOR sections publish a mapping from anchor-name
(a string) to instance handle. The spec is silent on whether duplicate names
are permitted; a strict implementation rejects, a lenient one takes first-wins
or last-wins (divergent across implementations). A REFERENCE in another file
pointing at the duplicated name resolves nondeterministically.
Bug-reporter language: "duplicate anchor name in ANCHOR section", "two anchors
with same name", "ANCHOR name collision", "anchor name published twice",
"ambiguous anchor in STEP".

Reproducer recipe:
  <origin>=#10; and <origin>=#11; in the ANCHOR section,
  with #10 and #11 distinct CARTESIAN_POINTs.

Byte assertions:
  contains(b'ANCHOR;')
  matches(rb'(?s)<origin>=#10;.*<origin>=#11;')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh035",
    defect=(
        "ANCHOR section publishing the same anchor name twice; "
        "input: ANCHOR section contains <origin>=#10; and <origin>=#11; "
        "where #10 and #11 are distinct CARTESIAN_POINTs; "
        "ISO 10303-21 Ed.3: ANCHOR section maps anchor-name (string) to instance handle; "
        "the spec is silent on whether duplicate names are permitted; "
        "a strict implementation rejects, a lenient one takes first-wins or last-wins "
        "(divergent across implementations); "
        "a REFERENCE in another file pointing at the duplicated name resolves nondeterministically; "
        "OCC silently accepts with diagnostic but loads empty result; "
        "expected kernel behavior: reject duplicate anchor names with a diagnostic; "
        "or if tolerant policy is chosen, document the deterministic disambiguation rule "
        "(first-wins / last-wins) and warn; "
        "see also: Lh026; "
        "synonyms: duplicate anchor name in ANCHOR section, two anchors with same name, "
        "ANCHOR name collision, anchor name published twice, ambiguous anchor in STEP"
    ),
)


def _render_lh035() -> str:
    """Render a Part-21 with ANCHOR section publishing the same anchor name twice."""
    return (
        "ISO-10303-21;\n"
        "/* Lh035: ANCHOR section with duplicate anchor name <origin> */\n"
        "/* ISO 10303-21 Ed.3: ANCHOR maps anchor-name to instance handle */\n"
        "/* DEFECT: <origin> is published twice — once for #10, once for #11 */\n"
        "/* strict receiver must reject; lenient receiver must document first-wins/last-wins */\n"
        "/* OCC silently accepts with diagnostic but loads empty result */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh035: ANCHOR section with duplicate anchor name origin'),'2;1');\n"
        "FILE_NAME('Lh035.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "ANCHOR;\n"
        "/* DEFECT: <origin> appears twice — maps to two different instances */\n"
        "<origin>=#10;\n"
        "<origin>=#11;\n"
        "<corner>=#12;\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#10=CARTESIAN_POINT('origin-a',(0.,0.,0.));\n"
        "#11=CARTESIAN_POINT('origin-b',(0.5,0.,0.));\n"
        "#12=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#13=DIRECTION('xdir',(1.,0.,0.));\n"
        "#14=DIRECTION('zdir',(0.,0.,1.));\n"
        "#15=GEOMETRIC_CURVE_SET('duplicate-anchor-shape',(#10,#12));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh035(path) -> None:
    Path(path).write_text(_render_lh035())


f.render = _render_lh035  # type: ignore[method-assign]
f.write = _write_lh035    # type: ignore[method-assign]
