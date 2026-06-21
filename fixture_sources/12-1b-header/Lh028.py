"""Lh028 — Forward reference inside ANCHOR section to undefined data instance.

Catalog claim: ANCHOR may reference data instances, but every #NNN it names
must eventually resolve in some DATA section of the same file. Generators emit
anchors for instances that were filtered out of the DATA section. The kernel must
reject as undefined reference after the two-pass declare/resolve phase; tolerant
mode may keep the file but mark the anchor as broken.
Bug-reporter language: "ANCHOR points at undefined #NNN", "anchor references
missing instance", "filtered instance still in ANCHOR", "ANCHOR forward
reference unresolved", "STEP anchor names ghost entity".

Reproducer recipe:
  ANCHOR; <part_anchor>=#100; ENDSEC; DATA; #1=PRODUCT(..); ENDSEC;
  (no #100 defined)

Byte assertions:
  contains(b'ANCHOR;')
  matches(rb'<[^>]+>=#100;')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh028",
    defect=(
        "Forward reference inside ANCHOR section to undefined data instance; "
        "input: ANCHOR section contains <part_anchor>=#100; but #100 is never defined "
        "in any DATA section of the same file; "
        "ISO 10303-21 Ed.3: every #NNN referenced in ANCHOR must eventually resolve "
        "in some DATA section of the same file; "
        "generators emit anchors for instances that were filtered out of the DATA section; "
        "pure-Python Part-21 validator rejects (reject(E_UNRESOLVED_REFS)); "
        "OCC silently accepts with diagnostic but loads empty result; "
        "expected kernel behavior: reject as undefined reference after two-pass declare/resolve phase; "
        "tolerant mode may keep file but must mark the anchor as broken; "
        "see also: Lh026, Lh027; "
        "synonyms: ANCHOR points at undefined #NNN, anchor references missing instance, "
        "filtered instance still in ANCHOR, ANCHOR forward reference unresolved, "
        "STEP anchor names ghost entity"
    ),
)


def _render_lh028() -> str:
    """Render a Part-21 with an ANCHOR entry pointing at #100 which is never defined."""
    return (
        "ISO-10303-21;\n"
        "/* Lh028: forward reference in ANCHOR section to undefined instance #100 */\n"
        "/* ISO 10303-21 Ed.3: every #NNN in ANCHOR must resolve in a DATA section */\n"
        "/* DEFECT: <part_anchor>=#100; but #100 is absent from all DATA sections */\n"
        "/* pure-Python validator rejects (E_UNRESOLVED_REFS); OCC silently accepts empty */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh028: ANCHOR forward reference to undefined #100'),'2;1');\n"
        "FILE_NAME('Lh028.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "ANCHOR;\n"
        "/* DEFECT: #100 is not defined anywhere in the DATA section below */\n"
        "<part_anchor>=#100;\n"
        "<valid_anchor>=#1;\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('anchor-ghost-shape',(#1,#2));\n"
        "/* NOTE: #100 referenced in ANCHOR above is intentionally absent */\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh028(path) -> None:
    Path(path).write_text(_render_lh028())


f.render = _render_lh028  # type: ignore[method-assign]
f.write = _write_lh028    # type: ignore[method-assign]
