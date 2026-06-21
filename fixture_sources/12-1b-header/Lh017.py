"""Lh017 — User-defined entity name with `!` prefix in DATA section.

Catalog claim: ISO 10303-21 §11 reserves names beginning with `!` for user-defined entities.
Schema-driven readers whose keyword regex is `[A-Z][0-9A-Z_]*` reject them outright instead
of treating them as opaque user types.
Bug-reporter language: "bang-prefixed entity in DATA section",
"user-defined entity rejected by regex", "!FOO entity in DATA",
"schema reader rejects ! prefix", "STEP entity name with exclamation mark".

Reproducer recipe: #12=!MYCURVE(0.0,0.0,0.0,1.0,$,$,$);

Byte assertions:
  matches(rb'#\\d+\\s*=\\s*!')
  matches(rb'#\\d+\\s*=\\s*!\\w+\\(')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh017",
    defect=(
        "User-defined entity name with ! prefix in DATA section rejected by schema-driven readers; "
        "input: DATA section contains #12=!MYCURVE(0.0,0.0,0.0,1.0,$,$,$) where the ! prefix "
        "designates a user-defined entity per ISO 10303-21 §11; "
        "schema-driven readers whose keyword regex is [A-Z][0-9A-Z_]* reject ! -prefixed "
        "identifiers outright instead of treating them as opaque user-defined type placeholders; "
        "cross-oracle: pure-Python Part-21 validator rejects (reject E_UNRESOLVED_REFS); "
        "OCCT silently accepts (load is empty); OCC auto-heals a spec-level violation; "
        "expected kernel behavior: lex !-prefixed identifiers as keywords; reject by schema "
        "validation OR pass through as a generic-entity placeholder; "
        "see also: Lh015; "
        "synonyms: bang-prefixed entity in DATA section, user-defined entity rejected by regex, "
        "!FOO entity in DATA, schema reader rejects ! prefix, STEP entity name with exclamation mark"
    ),
)


def _render_lh017() -> str:
    """Render a Part-21 with a !-prefixed user-defined entity name in the DATA section."""
    return (
        "ISO-10303-21;\n"
        "/* Lh017: user-defined entity with ! prefix in DATA section */\n"
        "/* ISO 10303-21 §11: ! prefix designates user-defined entity types */\n"
        "/* DEFECT: schema readers with regex [A-Z][0-9A-Z_]* reject ! identifiers */\n"
        "/* Cross-oracle: pure Python rejects E_UNRESOLVED_REFS; OCCT silently accepts */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh017: user-defined entity with ! prefix in DATA section'),'2;1');\n"
        "FILE_NAME('Lh017.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: !MYCURVE uses the ! prefix for user-defined entity — breaks schema readers */\n"
        "#12=!MYCURVE(0.0,0.0,0.0,1.0,$,$,$);\n"
        "#5=GEOMETRIC_CURVE_SET('bang-prefixed-entity-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh017(path) -> None:
    Path(path).write_text(_render_lh017())


f.render = _render_lh017  # type: ignore[method-assign]
f.write = _write_lh017    # type: ignore[method-assign]
