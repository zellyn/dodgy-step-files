"""Lh037 — User-defined HEADER entity (`!FOO`) emitted before required HEADER records.

Catalog claim: Edition-3 permits user-defined header entities prefixed with `!`
(e.g. `!COMPANY_INFO`). The order, duplication, and unknown-record rules are
weakly specified. Producers occasionally place `!FOO` before FILE_DESCRIPTION
(the spec mandates FILE_DESCRIPTION first) or use `!FOO` names colliding with
EXPRESS schema entity names.
Bug-reporter language: "user-defined HEADER entity before required records",
"!COMPANY_INFO before FILE_DESCRIPTION", "vendor header out of order",
"bang-prefix header at wrong position", "STEP header order violated by !FOO".

Reproducer recipe:
  HEADER opens with !COMPANY_INFO('ACME','release-2026',..) followed by
  FILE_DESCRIPTION/FILE_NAME/FILE_SCHEMA, then a second
  !INTERNAL_ROUTING_TAG(..) after FILE_SCHEMA.

Byte assertions:
  contains(b'!COMPANY_INFO')
  count(b'!') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=reject
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh037",
    defect=(
        "User-defined HEADER entity (!FOO) emitted before required HEADER records; "
        "input: HEADER opens with !COMPANY_INFO('ACME','release-2026') before FILE_DESCRIPTION, "
        "then FILE_DESCRIPTION/FILE_NAME/FILE_SCHEMA in correct order, "
        "then !INTERNAL_ROUTING_TAG after FILE_SCHEMA; "
        "ISO 10303-21 Ed.3 §6.2: permits user-defined header entities prefixed with ! "
        "but mandates FILE_DESCRIPTION first; "
        "producers occasionally place !FOO before FILE_DESCRIPTION, "
        "violating the required record ordering; "
        "OCC rejects under one heal mode and silently accepts under the other; "
        "IFC rejects; "
        "expected kernel behavior: skip unknown !NAME entities with a warning; "
        "tolerate them in any header position; "
        "require the three standard records to be present in spec-mandated order "
        "independent of unknown-entity placement; "
        "see also: Lh016; "
        "synonyms: user-defined HEADER entity before required records, "
        "!COMPANY_INFO before FILE_DESCRIPTION, vendor header out of order, "
        "bang-prefix header at wrong position, STEP header order violated by !FOO"
    ),
)


def _render_lh037() -> str:
    """Render a Part-21 with !COMPANY_INFO user-defined header entity before FILE_DESCRIPTION."""
    return (
        "ISO-10303-21;\n"
        "/* Lh037: user-defined !FOO header entity placed before FILE_DESCRIPTION */\n"
        "/* ISO 10303-21 Ed.3 §6.2: FILE_DESCRIPTION must be the first HEADER record */\n"
        "/* DEFECT: !COMPANY_INFO appears before FILE_DESCRIPTION — violates required order */\n"
        "/* OCC rejects under strict mode; expected: skip !FOO with warning, tolerate any position */\n"
        "HEADER;\n"
        "!COMPANY_INFO('ACME','release-2026','contact@acme.example');\n"
        "/* DEFECT: standard records follow the !FOO entity, not precede it */\n"
        "FILE_DESCRIPTION(('Lh037: !COMPANY_INFO vendor header before FILE_DESCRIPTION'),'2;1');\n"
        "FILE_NAME('Lh037.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "!INTERNAL_ROUTING_TAG('dept=CAD','priority=low');\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('vendor-header-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh037(path) -> None:
    Path(path).write_text(_render_lh037())


f.render = _render_lh037  # type: ignore[method-assign]
f.write = _write_lh037    # type: ignore[method-assign]
