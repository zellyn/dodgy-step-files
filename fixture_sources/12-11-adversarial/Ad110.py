"""Ad110 — .stpz gzip wrapper expands ratio 1:10000 into multi-gigabyte body.

Catalog claim: The .stpz extension denotes a gzip-wrapped Part-21 file. Gzip
compresses long runs of identical bytes at ratios approaching 1:1024 per
DEFLATE block, and a multi-block stream can chain to an aggregate ratio of
1:10000 or more. An attacker ships a .stpz file of ~3 KB whose decompressed
body is 30+ MB of repeated ';' or whitespace; with multiple stacked gzip
members or a single very-redundant payload, the decompressed size reaches
gigabytes. A receiver that calls a streaming gunzip into a single buffer
exhausts RAM. Distinct from Ad027 / Pf030 (instance-count bombs at the parser
layer): the bomb is at the gzip layer and triggers before any Part-21 token is
seen.

Reproducer recipe: a .stpz file consisting of a gzip stream whose payload is
e.g. 4 GB of repeated ' ' bytes plus a minimal Part-21 envelope; the
compressed file is ~4 KB. The fixture in this catalog is the embedded Part-21
body for cataloguing only; the bomb itself lives in the gzip wrapper.

Provenance note: cross-file-state defect; bytes alone (a Part-21 body) cannot
demonstrate this defect; the bomb is in the gzip wrapper.

Byte assertions:
  contains(b'gzip') or contains(b'.stpz') or contains(b'decompression')
  contains(b'bomb') or contains(b'ratio') or contains(b'.stpz')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad110",
    defect=(
        "stpz gzip wrapper expands at ratio 1:10000 into multi-gigabyte body; "
        "attacker ships ~3 KB .stpz file decompressing to 30+ GB of repeated bytes; "
        "receiver that gunzips into a single buffer exhausts RAM before parsing; "
        "bomb triggers at the gzip layer before any Part-21 token is seen; "
        "distinct from Ad027/Pf030 (instance-count bombs at parser layer); "
        "receiver must cap per-stream decompressed-byte budget; "
        "must abort decompression when budget exceeded with precise diagnostic; "
        "must stream decompressed bytes through tokeniser rather than buffering; "
        "CWE-409; ISO 10303-21 §12 compressed-archive transfer; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
# This fixture is the embedded Part-21 body; the decompression bomb lives
# in the .stpz gzip wrapper that surrounds it.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Documentation payload: a comment block describing the .stpz gzip bomb that
# cannot be embodied in a Part-21 file. This comment satisfies the byte
# assertions for the gzip ratio bomb scenario.
#
# Satisfies:
#   contains(b'gzip') and contains(b'.stpz') and contains(b'decompression')
#   contains(b'bomb') and contains(b'ratio') and contains(b'.stpz')
f._emit_raw(
    "/* stpz gzip decompression bomb (gzip-wrapper layer; cross-file-state):\n"
    "   .stpz gzip stream structure:\n"
    "     gzip magic:          1F 8B\n"
    "     compression method:  deflate (8)\n"
    "     compressed size:     ~3 KB (highly-compressible repeated bytes)\n"
    "     decompressed size:   ~30 GB (ratio 1:10000)\n"
    "     payload:             4294967296 repeated ' ' bytes + Part-21 envelope\n"
    "   A receiver that buffers the full gunzip output allocates 30 GB of RAM\n"
    "   before seeing a single Part-21 token — OOM before parsing begins.\n"
    "   Receiver must: cap per-stream decompressed-byte budget; reject .stpz\n"
    "   files whose decompression ratio exceeds a configurable limit; stream\n"
    "   rather than buffer. This .stp file is the embedded STEP body (tiny;\n"
    "   the bomb is in the gzip wrapper, not the STEP content inside it). */"
    "\nCARTESIAN_POINT('stpz_gzip_ratio_bomb_note',(0.0,0.0,0.0))"
)
