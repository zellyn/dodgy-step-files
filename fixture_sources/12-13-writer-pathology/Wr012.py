"""Wr012 — Random `#N` numbering with no monotonic structure.

Catalog claim: Instance numbers in the DATA section follow no monotonic
pattern: `#1`, then `#1000`, then `#5`, then `#1003`, then `#7`.  The spec
does not mandate monotonic numbering, so the file is well-formed; but human
reviewers, line-based diff tools, and forward-reference-detecting linters all
stumble.

Reproducer recipe: a Part-21 file in which the order of `#NNN` in the DATA
section is `#1, #1000, #5, #1003, #7, #1006`.

Byte assertions:
  matches(rb'(?s)#1=.*#1000=.*#5=')
  count(b'#') >= 6

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr012",
    defect=(
        "Random hash-N numbering with no monotonic structure; "
        "instance numbers in the DATA section follow no monotonic pattern: "
        "#1, then #1000, then #5, then #1003, then #7; "
        "writers that allocate instance numbers from a hashed pool keyed on "
        "entity-identity rather than emit-order; observed in some Java-based exporters; "
        "the spec does not mandate monotonic numbering, so the file is well-formed; "
        "but human reviewers, line-based diff tools, and forward-reference-detecting "
        "linters all stumble; "
        "expected kernel behavior: heal and accept; "
        "parse normally; numbering is content-addressable, not order-bearing; "
        "a re-emit policy may normalize or renumber sequentially; "
        "synonyms: STEP instance numbers are random, file numbering jumps, "
        "can't follow refs visually, instance numbers jump around"
    ),
)


def _render_random_numbering() -> str:
    """Return a Part-21 file with non-monotonic instance numbers: #1,#1000,#5,#1003,#7,#1006."""
    return (
        "ISO-10303-21;\n"
        "/* Wr012: non-monotonic instance numbering in DATA section */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr012 - random instance numbering with no monotonic structure'),'2;1');\n"
        "FILE_NAME('Wr012.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: instance numbers jump: #1, #1000, #5, #1003, #7, #1006 — not monotonic */\n"
        "/* The spec permits any positive integer; a conforming kernel must accept these */\n"
        "#1=DIRECTION('zdir',(0.,0.,1.));\n"
        "#1000=DIRECTION('xdir',(1.,0.,0.));\n"
        "#5=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#1003=CARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "#7=CARTESIAN_POINT('p2',(1.,1.,0.));\n"
        "#1006=GEOMETRIC_CURVE_SET('random-ids',(#5,#1003,#7));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_random_numbering(path) -> None:
    Path(path).write_bytes(_render_random_numbering().encode("utf-8"))


f.render = _render_random_numbering  # type: ignore[method-assign]
f.write = _write_random_numbering  # type: ignore[method-assign]
