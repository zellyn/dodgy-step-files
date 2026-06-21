"""Lh015 — User-defined HEADER entity not prefixed with `!`.

Catalog claim: ISO 10303-21 reserves header keywords without `!` for the standard.
Vendor-specific HEADER entities must begin with `!` to avoid collision with future
spec entities. Files appear with bare `VENDOR_INFO(..)` or similar.
Bug-reporter language: "vendor HEADER entity without bang prefix",
"user-defined header missing exclamation mark", "VENDOR_INFO bare without !",
"non-spec header entity collides with future spec", "custom HEADER record name not prefixed".

Reproducer recipe:
  HEADER; FILE_DESCRIPTION((''),'2;1'); FILE_NAME(..); FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));
  VENDOR_INFO('SolidWorks 2024'); ENDSEC;

Byte assertions:
  matches(rb"FILE_SCHEMA\\([^;]*\\);\\s*VENDOR_INFO\\(")
  contains(b'VENDOR_INFO')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh015",
    defect=(
        "User-defined HEADER entity not prefixed with ! (bang); "
        "input: HEADER section contains a bare VENDOR_INFO('SolidWorks 2024') record "
        "after FILE_SCHEMA without the required ! prefix; "
        "ISO 10303-21 reserves header keywords without ! for standardized entities; "
        "vendor-specific or user-defined HEADER entities must begin with ! to avoid "
        "collision with future spec entities (e.g. !VENDOR_INFO instead of VENDOR_INFO); "
        "strict readers reject any HEADER keyword they do not recognize; "
        "lenient readers may treat unknown header keywords as ignorable with a warning "
        "but the ! prefix is the specified disambiguation mechanism; "
        "produced by SolidWorks and other CAD tools that inject proprietary HEADER records "
        "without the required bang prefix; "
        "expected kernel behavior: reject the bare keyword; lenient mode may treat unknown "
        "header keywords as ignorable with a warning; "
        "see also: Lh017; "
        "synonyms: vendor HEADER entity without bang prefix, user-defined header missing "
        "exclamation mark, VENDOR_INFO bare without !, non-spec header entity collides "
        "with future spec, custom HEADER record name not prefixed"
    ),
)


def _render_lh015() -> str:
    """Render a Part-21 with a bare VENDOR_INFO entity in the HEADER section (missing ! prefix)."""
    return (
        "ISO-10303-21;\n"
        "/* Lh015: user-defined HEADER entity VENDOR_INFO without required ! prefix */\n"
        "/* ISO 10303-21: vendor/user-defined HEADER records must start with ! */\n"
        "/* Standard reserves unprefixed HEADER keywords for future specification use */\n"
        "/* DEFECT: VENDOR_INFO appears without ! prefix after FILE_SCHEMA */\n"
        "/* Strict readers reject unrecognized unprefixed header keywords */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh015: user-defined HEADER entity without ! prefix'),'2;1');\n"
        "FILE_NAME('Lh015.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "VENDOR_INFO('SolidWorks 2024');\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('bare-vendor-header-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh015(path) -> None:
    Path(path).write_text(_render_lh015())


f.render = _render_lh015  # type: ignore[method-assign]
f.write = _write_lh015    # type: ignore[method-assign]
