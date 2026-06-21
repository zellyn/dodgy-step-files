"""Lh024 — Reuse of #NNN across different DATA sections (Ed.3 multi-section).

Catalog claim: Edition 3 allows multiple DATA;...ENDSEC; sections, each with
its own #NNN namespace; cross-section references use @section_name#N syntax.
Tools targeting Edition 1 either fail at the second DATA; or silently flatten
namespaces, causing collisions when #10 appears in both sections. Kernel must
heal and accept N>=1 DATA sections; scope #N IDs per-section; resolve
cross-section references via the proper Ed.3 syntax; never flatten namespaces
across sections. Must not silently flatten.
Bug-reporter language: "#NNN reused across DATA sections", "Ed.3 multi-section
ID collision", "two DATA sections share #10", "namespace flattened across
sections", "STEP multi-section reference broken".

Reproducer recipe:
  HEADER;..ENDSEC;DATA;#10=PRODUCT(..);ENDSEC;
  DATA('extra',('AUTOMOTIVE_DESIGN'));#10=APPLICATION_CONTEXT('..');ENDSEC;
  END-ISO-10303-21;

Byte assertions:
  count(b'DATA;') + count(b"DATA('") >= 2
  count(b'DATA') >= 2

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh024",
    defect=(
        "Reuse of #NNN instance IDs across different DATA sections (Ed.3 multi-section); "
        "input: file contains two DATA sections each defining #10; "
        "Edition 3 allows multiple DATA;...ENDSEC; sections each with its own #NNN namespace; "
        "cross-section references use @section_name#N syntax; "
        "tools targeting Edition 1 either fail at the second DATA; keyword or silently "
        "flatten namespaces, causing collisions when #10 appears in both sections; "
        "OCC silently accepts with diagnostic but loads empty result; "
        "expected kernel behavior: heal and accept N>=1 DATA sections; "
        "scope #N IDs per-section; resolve cross-section references via Ed.3 syntax; "
        "never flatten namespaces across sections; "
        "see also: Ad080, Lh022; "
        "synonyms: #NNN reused across DATA sections, Ed.3 multi-section ID collision, "
        "two DATA sections share #10, namespace flattened across sections, "
        "STEP multi-section reference broken"
    ),
)


def _render_lh024() -> str:
    """Render a Part-21 with two DATA sections each defining #10 (namespace collision)."""
    return (
        "ISO-10303-21;\n"
        "/* Lh024: two DATA sections each define #10 — Ed.3 namespace collision */\n"
        "/* ISO 10303-21 Ed.3: each DATA section has its own #NNN namespace */\n"
        "/* DEFECT: Ed.1/2 readers flatten namespaces; #10 collides across sections */\n"
        "/* Cross-section references should use @section_name#N syntax in Ed.3 */\n"
        "/* OCC: silently accepts (empty result); catalog requires heal or reject */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh024: #NNN reused across two DATA sections'),'2;1');\n"
        "FILE_NAME('Lh024.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "/* First DATA section: defines #10 as PRODUCT */\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#10=PRODUCT('part-a','Part A','',(#11));\n"
        "#11=APPLICATION_CONTEXT('automotive design');\n"
        "#12=GEOMETRIC_CURVE_SET('section1-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "/* DEFECT: second DATA section reuses #10 — collides with #10 from first section */\n"
        "DATA('supplemental',('AUTOMOTIVE_DESIGN'));\n"
        "#10=APPLICATION_CONTEXT('supplemental context');\n"
        "#20=CARTESIAN_POINT('extra',(2.,2.,0.));\n"
        "#21=GEOMETRIC_CURVE_SET('section2-shape',(#20));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh024(path) -> None:
    Path(path).write_text(_render_lh024())


f.render = _render_lh024  # type: ignore[method-assign]
f.write = _write_lh024    # type: ignore[method-assign]
