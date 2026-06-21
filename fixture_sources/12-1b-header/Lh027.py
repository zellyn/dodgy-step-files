"""Lh027 — Malformed entity ID inside an ANCHOR entry (non-numeric `#`).

Catalog claim: ANCHOR entries reference #NNN form; entries using non-numeric
tokens after # (e.g. <#42@x>='product';) violate the grammar. The kernel
must reject the entry with a precise diagnostic; do not abort the whole file.
Bug-reporter language: "non-numeric # in ANCHOR entry", "ANCHOR with bad
instance ID syntax", "malformed entity reference in ANCHOR", "ANCHOR section
grammar violation", "anchor target ID not a number".

Reproducer recipe:
  ANCHOR; <part_anchor>=#42@x; ENDSEC;

Byte assertions:
  contains(b'#42@x') or matches(rb'#\\d+@[a-zA-Z]')
  contains(b'#42@x')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh027",
    defect=(
        "Malformed entity ID inside an ANCHOR entry (non-numeric # after digits); "
        "input: ANCHOR section contains <part_anchor>=#42@x; where #42@x is not a "
        "valid entity-instance reference (the @x suffix makes it non-conformant); "
        "ANCHOR entries must reference the pure #NNN form; "
        "entries using non-numeric tokens after # violate the ISO 10303-21 Ed.3 grammar; "
        "OCC silently accepts with diagnostic but loads empty result; "
        "expected kernel behavior: reject the entry with a precise diagnostic; "
        "do not abort the whole file; "
        "see also: Lh026, Lh028; "
        "synonyms: non-numeric # in ANCHOR entry, ANCHOR with bad instance ID syntax, "
        "malformed entity reference in ANCHOR, ANCHOR section grammar violation, "
        "anchor target ID not a number"
    ),
)


def _render_lh027() -> str:
    """Render a Part-21 with an ANCHOR entry containing malformed #42@x reference."""
    return (
        "ISO-10303-21;\n"
        "/* Lh027: malformed entity ID in ANCHOR entry — #42@x is not a valid #NNN reference */\n"
        "/* ISO 10303-21 Ed.3: ANCHOR entries must use pure #NNN integer form */\n"
        "/* DEFECT: <part_anchor>=#42@x has non-numeric suffix @x after digits */\n"
        "/* OCC silently accepts (empty result); catalog requires reject with diagnostic */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh027: malformed entity ID in ANCHOR entry'),'2;1');\n"
        "FILE_NAME('Lh027.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "/* DEFECT: ANCHOR section with malformed reference #42@x */\n"
        "ANCHOR;\n"
        "/* DEFECT: #42@x is not a valid entity-instance reference; @x suffix violates grammar */\n"
        "<part_anchor>=#42@x;\n"
        "<valid_anchor>=#1;\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('malformed-anchor-id-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh027(path) -> None:
    Path(path).write_text(_render_lh027())


f.render = _render_lh027  # type: ignore[method-assign]
f.write = _write_lh027    # type: ignore[method-assign]
