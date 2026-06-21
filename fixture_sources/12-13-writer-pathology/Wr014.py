"""Wr014 — Sparse instance numbering with huge gaps.

Catalog claim: A file with a handful of entities uses instance numbers like
`#42`, `#9876543`, `#21000000`; the maximum number is many orders of magnitude
larger than the entity count.  Spec-conforming, but a class of receivers
naïvely pre-allocates an array of size `max(#N)`, blowing up memory.

Reproducer recipe: a 5-entity file where the highest instance number is
`#999999999`.

Byte assertions:
  matches(rb'#\\d{7,}=')
  matches(rb'#\\d{6,}=')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr014",
    defect=(
        "Sparse instance numbering with huge gaps; "
        "a file with a handful of entities uses instance numbers where the maximum "
        "is many orders of magnitude larger than the entity count; "
        "writers that hash entity identity to a wide integer space and use the hash "
        "as the instance number directly; "
        "spec-conforming, but a class of receivers naively pre-allocates an array "
        "of size max(#N), blowing up memory; "
        "ISO 10303-21 Ed.3 section 5 defines instance numbers as unbounded positive integers; "
        "expected kernel behavior: use a sparse map (hashtable) for instance lookup; "
        "never assume hash-N is a dense array index; "
        "reject only if hash-N exceeds 32-bit signed integer range and the kernel uses "
        "int32 indices internally; "
        "synonyms: STEP file with huge instance numbers, out of memory loading small file, "
        "instance number overflow, memory blows up loading STEP"
    ),
)


def _render_sparse_numbering() -> str:
    """Return a Part-21 with 5 entities but instance numbers reaching into the hundreds of millions."""
    return (
        "ISO-10303-21;\n"
        "/* Wr014: sparse instance numbering — 5 entities but #N reaches 999999999 */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr014 - sparse instance numbering with huge gaps'),'2;1');\n"
        "FILE_NAME('Wr014.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: only 5 entities but instance numbers are hash-derived and huge */\n"
        "/* Naive receivers pre-allocate array[max_id] and OOM on these 5 entities */\n"
        "#42=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#9876543=DIRECTION('zdir',(0.,0.,1.));\n"
        "#21000000=DIRECTION('xdir',(1.,0.,0.));\n"
        "#500000001=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#999999999=GEOMETRIC_CURVE_SET('sparse-ids',(#42,#500000001));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_sparse_numbering(path) -> None:
    Path(path).write_bytes(_render_sparse_numbering().encode("utf-8"))


f.render = _render_sparse_numbering  # type: ignore[method-assign]
f.write = _write_sparse_numbering  # type: ignore[method-assign]
