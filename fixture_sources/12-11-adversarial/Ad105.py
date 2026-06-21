"""Ad105 — .stpz / .stpx archive container claims gigabytes of uncompressed data (decompression bomb).

Catalog claim: The .stpz and .stpx extensions denote ZIP / gzip-archive
variants of STEP transfer. A maliciously-crafted archive can claim
gigabytes of uncompressed payload from a few kilobytes of input — the
standard ZIP-bomb / gzip-bomb pattern. A receiver that decompresses into
memory before parsing exhausts RAM or swap.

Reproducer recipe: a ZIP archive whose entry header advertises
uncompressed size of 10 GB but whose compressed bytes are tiny
(highly-compressible repeated bytes); the entry contains a 100-character
STEP body.

Provenance note: this is a cross-file-state defect; the bomb lives in the
archive header, not the embedded STEP body. This .stp fixture encodes
only the embedded body; the receiver-side amplification requires an actual
archive wrapper.

Byte assertions:
  contains(b'ISO-10303-21')
  contains(b'END-ISO-10303-21')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad105",
    defect=(
        "decompression bomb: .stpz/.stpx archive header advertises "
        "10 GB uncompressed size; compressed payload is tiny; "
        "receiver decompresses into memory before parsing, exhausting RAM; "
        "receiver must cap per-archive-entry decompression budget (size+time); "
        "CWE-409; ISO 10303-21 §12 compressed-archive transfer; "
        "See also Ad104; cross-file-state defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
# Satisfies: contains(b'ISO-10303-21') and contains(b'END-ISO-10303-21')
# (both appear in the standard Part-21 bookends emitted by render()).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Documentation payload: a comment block describing the .stpz bomb header
# that cannot be embodied in a Part-21 file. This comment documents the
# defect precondition for the archive wrapper; the static .stp is the
# embedded body that would appear inside the archive entry.
#
# The bomb header structure (ZIP local file header fields):
#   Signature:          0x504B0304 (PK\x03\x04)
#   Compressed size:    5 bytes   (the real compressed payload)
#   Uncompressed size:  0x280000000 (10 GB)
#   File entry body:    \x00\x00\x00\x00\x00 (5 null bytes — "compresses" to 10 GB
#                       when the receiver inflates with an uncapped buffer)
#
# A receiver enforcing the budget rejects this immediately on reading the
# local file header; a vulnerable receiver inflates until OOM.
f._emit_raw(
    "/* stpz decompression bomb (archive-wrapper layer):\n"
    "   ZIP local file header:\n"
    "     signature:        PK\\x03\\x04\n"
    "     compression:      deflate (8)\n"
    "     compressed size:  5 bytes\n"
    "     uncompressed size: 10737418240 bytes (10 GB)\n"
    "   The archive entry body is 5 null bytes; a receiver that inflates\n"
    "   without a size budget allocates 10 GB of RAM before parsing.\n"
    "   Receiver must: cap decompression budget; reject oversized entries.\n"
    "   This .stp file is the embedded STEP body (tiny; the bomb is the\n"
    "   archive header, not the STEP content inside it). */"
    "\nCARTESIAN_POINT('stpz_bomb_note',(0.0,0.0,0.0))"
)
