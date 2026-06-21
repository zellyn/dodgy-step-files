"""Wr015 — Duplicate `#N` instance numbers in the same DATA section.

Catalog claim: Two entities in the same DATA section share the same `#N`.
Spec violation.  Receivers diverge: first-wins, last-wins,
both-loaded-and-randomly-resolved, reject.

Reproducer recipe: `#10 = CARTESIAN_POINT('a',(0.,0.,0.));` and later
`#10 = CARTESIAN_POINT('b',(1.,1.,1.));` in the same DATA section.

Byte assertions:
  matches(rb'(?s)#10\\s*=\\s*CARTESIAN_POINT.*#10\\s*=\\s*CARTESIAN_POINT')
  count(b'#10=') >= 2

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr015",
    defect=(
        "Duplicate hash-N instance numbers in the same DATA section; "
        "two entities in the same DATA section share the same instance number; "
        "spec violation — ISO 10303-21 mandates unique instance numbers per DATA section; "
        "writers with broken counter logic when emitting multi-section or multi-pass files "
        "(collision between sections or passes); "
        "receivers diverge: first-wins, last-wins, both-loaded-and-randomly-resolved, reject; "
        "the two entities sharing an instance number race for back-references; "
        "the resulting model attaches each cross-reference to whichever the resolver picks "
        "(often last-wins), so structurally identical files load with different topology; "
        "expected kernel behavior: reject as malformed; "
        "spec mandates unique instance numbers per DATA section; "
        "document the resolution policy if the kernel chooses tolerant first-wins or last-wins; "
        "synonyms: duplicate instance number, two entities with same hash-N, "
        "STEP file has collision, same instance number twice, duplicate #5"
    ),
)


def _render_duplicate_instance_numbers() -> str:
    """Return a Part-21 file where #10 is defined twice in the same DATA section."""
    return (
        "ISO-10303-21;\n"
        "/* Wr015: two entities share instance number #10 in the same DATA section */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr015 - duplicate instance number in DATA section'),'2;1');\n"
        "FILE_NAME('Wr015.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: #10 appears twice — duplicate instance number, spec violation */\n"
        "#1=DIRECTION('zdir',(0.,0.,1.));\n"
        "#2=DIRECTION('xdir',(1.,0.,0.));\n"
        "#5=CARTESIAN_POINT('ref-point',(0.5,0.5,0.));\n"
        "/* First definition of #10 */\n"
        "#10=CARTESIAN_POINT('a',(0.,0.,0.));\n"
        "#11=CARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "#12=CARTESIAN_POINT('p2',(0.,1.,0.));\n"
        "/* Second definition of #10 — duplicate, spec violation */\n"
        "#10=CARTESIAN_POINT('b',(1.,1.,1.));\n"
        "#20=GEOMETRIC_CURVE_SET('dup-id',(#5,#11,#12));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_duplicate_instance_numbers(path) -> None:
    Path(path).write_bytes(_render_duplicate_instance_numbers().encode("utf-8"))


f.render = _render_duplicate_instance_numbers  # type: ignore[method-assign]
f.write = _write_duplicate_instance_numbers  # type: ignore[method-assign]
