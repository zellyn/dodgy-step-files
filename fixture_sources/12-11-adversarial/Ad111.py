"""Ad111 — ZIP bomb inside a 3MF / IFCZIP container that wraps a STEP body.

Catalog claim: 3MF and IFCZIP are STEP-adjacent container formats: a ZIP
archive whose entries include a Part-21 body (or an XML-encoded equivalent)
plus auxiliary metadata. A maliciously-crafted ZIP archive carries one entry
whose compressed bytes are tiny but whose uncompressed bytes claim gigabytes;
the textbook ZIP bomb (42.zip-style nested archives, or a single highly-redundant
entry). A receiver that extracts entries to a tempdir before parsing exhausts
disk; one that decompresses to memory exhausts RAM. Distinct from Ad105
(archive-header lie): in this entry, the ZIP entry actually decompresses to
the claimed size.

Reproducer recipe: a 3MF file (ZIP archive) containing a single entry
3D/3dmodel.model whose compressed-vs-uncompressed ratio is 1:5000; the entry
is valid 3MF XML when decompressed but ~2 GB long. Cannot be embodied as a
Part-21 fixture; the defect lives in the ZIP wrapper.

Provenance note: cross-file-state defect; bytes alone (a Part-21 body) cannot
demonstrate this defect; the bomb is in the ZIP wrapper.

Byte assertions:
  contains(b'3MF') or contains(b'IFCZIP') or contains(b'ZIP')
  contains(b'bomb') or contains(b'ratio')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad111",
    defect=(
        "ZIP bomb inside 3MF/IFCZIP container wrapping a STEP body; "
        "ZIP archive entry 3D/3dmodel.model compressed-vs-uncompressed ratio 1:5000; "
        "entry actually decompresses to claimed size (~2 GB) unlike Ad105 header lie; "
        "receiver extracting to tempdir exhausts disk; extracting to memory exhausts RAM; "
        "distinct from Ad105 (archive-header lie — detectable from header alone); "
        "receiver must cap per-entry decompression budget with precise diagnostic; "
        "must cap per-archive total budget; "
        "must refuse archives with implausible entry-count / total-size combinations; "
        "CWE-409; 3MF spec §3 ZIP container; ISO 10303-21 STEP body in IFCZIP; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
# This fixture is the STEP body that would appear inside the 3MF/IFCZIP ZIP
# entry; the ZIP bomb itself lives in the container wrapper.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Documentation payload: a comment block describing the 3MF/IFCZIP ZIP bomb
# that cannot be embodied in a Part-21 file.
#
# Satisfies:
#   contains(b'3MF') and contains(b'IFCZIP') and contains(b'ZIP')
#   contains(b'bomb') and contains(b'ratio')
f._emit_raw(
    "/* ZIP bomb in 3MF/IFCZIP container (ZIP-wrapper layer; cross-file-state):\n"
    "   3MF ZIP archive structure:\n"
    "     [Content_Types].xml    (valid 3MF content-types manifest)\n"
    "     3D/3dmodel.model       (the ZIP bomb entry)\n"
    "       compressed size:     ~400 KB (highly-compressible repeated bytes)\n"
    "       uncompressed size:   ~2 GB (ratio 1:5000)\n"
    "       content when decompressed: valid but enormous 3MF XML body\n"
    "   Unlike Ad105 the ZIP entry actually decompresses to the claimed size;\n"
    "   the bomb is not a header lie but a real high-ratio DEFLATE stream.\n"
    "   Applies to both 3MF and IFCZIP containers wrapping a STEP body.\n"
    "   Receiver must: cap per-entry budget; cap per-archive total; refuse\n"
    "   archives with implausible entry-count/size combinations.\n"
    "   This .stp file is the embedded STEP body (tiny; the bomb ratio\n"
    "   is in the ZIP wrapper, not in the STEP content inside it). */"
    "\nCARTESIAN_POINT('ifczip_3mf_zip_bomb_note',(0.0,0.0,0.0))"
)
