"""Lh046 — HEADER section contains only block comments and no required records.

Catalog claim: ISO 10303-21 mandates that HEADER contain at minimum
FILE_DESCRIPTION, FILE_NAME, and FILE_SCHEMA records (in that order). A
pathological writer emits a HEADER section consisting of only /* */ block
comments; the required records are absent. Spec-conforming readers cannot
determine the file's edition, encoding declaration, or schema name; they must
reject. Lenient readers may invent default metadata and proceed, hiding the
producer-side failure.
Bug-reporter language: "STEP file has empty header", "no FILE_SCHEMA in file",
"header is just comments", "schema unknown".

Reproducer recipe:
  HEADER; /* exported by build pipeline */ /* metadata unavailable */ ENDSEC;
  followed by a normal DATA section.

Byte assertions:
  contains(b'HEADER;') and contains(b'ENDSEC;')
  not_contains(b'FILE_DESCRIPTION(')
  not_contains(b'FILE_NAME(') and not_contains(b'FILE_SCHEMA(')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=reject
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh046",
    defect=(
        "HEADER section contains only /* */ block comments and no required records; "
        "input: HEADER; /* exported by build pipeline */ /* metadata unavailable */ ENDSEC; "
        "followed by a normal DATA section; "
        "ISO 10303-21 §6.2: HEADER must contain FILE_DESCRIPTION, FILE_NAME, and FILE_SCHEMA "
        "records in that order as minimum required content; "
        "a pathological writer emits a HEADER section consisting only of block comments — "
        "all three required records are absent; "
        "spec-conforming readers cannot determine the file edition, encoding, or schema name "
        "and must reject; "
        "lenient readers may invent default metadata (assume Edition-2, ISO-8859-1, AP203) "
        "and proceed, hiding the producer-side failure; "
        "expected kernel behavior: reject the file with a diagnostic naming each missing "
        "required record; do not invent default metadata to allow downstream import; "
        "see also: Lh037, Lh042; "
        "synonyms: HEADER contains only comments, STEP header missing required records, "
        "FILE_DESCRIPTION absent from header, comment-only HEADER section, "
        "empty HEADER with /* */ only"
    ),
)


def _render_lh046() -> str:
    """Render a Part-21 with HEADER section containing only /* */ block comments."""
    return (
        "ISO-10303-21;\n"
        "/* Lh046: HEADER section contains only block comments — no required records */\n"
        "/* ISO 10303-21 §6.2: HEADER must contain FILE_DESCRIPTION, FILE_NAME, FILE_SCHEMA */\n"
        "/* DEFECT: all three required records are absent; only block comments appear in HEADER */\n"
        "/* lenient readers may invent default metadata; strict readers must reject */\n"
        "HEADER;\n"
        "/* exported by build pipeline */\n"
        "/* metadata unavailable — placeholder header inserted by partial export */\n"
        "/* FILE_DESCRIPTION: intentionally omitted */\n"
        "/* FILE_NAME: intentionally omitted */\n"
        "/* FILE_SCHEMA: intentionally omitted */\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('comment-only-header-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh046(path) -> None:
    Path(path).write_text(_render_lh046())


f.render = _render_lh046  # type: ignore[method-assign]
f.write = _write_lh046    # type: ignore[method-assign]
