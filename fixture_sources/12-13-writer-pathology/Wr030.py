"""Wr030 — FILE_SCHEMA listing schemas the file does not actually use.

Catalog claim: FILE_SCHEMA(('AUTOMOTIVE_DESIGN','CONFIG_CONTROL_DESIGN',
'AP242_MANAGED_MODEL_BASED_3D_ENGINEERING')); three schemas declared, but the DATA
section uses only AP203 entities. Bug-reporter language: "STEP claims AP242 but uses
AP203 only", "FILE_SCHEMA over-declared", "AP242 listed but not used".

Reproducer recipe: standard AP203 entity body with FILE_SCHEMA listing both
'AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }' and 'AP242_MANAGED_MODEL_BASED_3D_ENGINEERING'.

Byte assertions:
  matches(rb"FILE_SCHEMA\\(\\(\\s*'[^']+'\\s*,\\s*'[^']+'")
  count(b"','") >= 2

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr030",
    defect=(
        "FILE_SCHEMA listing schemas the file does not actually use; "
        "input: FILE_SCHEMA declares AUTOMOTIVE_DESIGN, CONFIG_CONTROL_DESIGN, "
        "and AP242_MANAGED_MODEL_BASED_3D_ENGINEERING; "
        "but the DATA section uses only AP203-compatible entities; "
        "any AP242-specific validation passes vacuously because the AP242 entities are absent; "
        "produced by writers that hard-code a schema list rather than computing "
        "the minimal set actually referenced by the DATA section entities; "
        "expected kernel behavior: warn and accept — normalize by validating against "
        "any one declared schema under which the DATA-section entities are well-formed; "
        "emit a warning on over-declaration; "
        "synonyms: STEP claims AP242 but uses AP203 only, FILE_SCHEMA over-declared, "
        "AP242 listed but not used, STEP claims multiple schemas"
    ),
)


def _render_wr030() -> str:
    """Render a Part-21 with FILE_SCHEMA over-declaring multiple schemas."""
    return (
        "ISO-10303-21;\n"
        "/* Wr030: FILE_SCHEMA over-declares schemas the DATA section does not use */\n"
        "/* Three schemas declared; DATA section contains only AP203-compatible entities */\n"
        "/* Writer hard-coded schema list instead of computing minimal referenced set */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr030'),'2;1');\n"
        "FILE_NAME('Wr030.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "/* DEFECT: three schemas declared; only AP203 entities appear in DATA section */\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }','CONFIG_CONTROL_DESIGN','AP242_MANAGED_MODEL_BASED_3D_ENGINEERING'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Only AP203-compatible entities: GEOMETRIC_CURVE_SET, CARTESIAN_POINT, DIRECTION */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('ap203-only-body',());\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr030(path) -> None:
    Path(path).write_text(_render_wr030())


f.render = _render_wr030  # type: ignore[method-assign]
f.write = _write_wr030    # type: ignore[method-assign]
