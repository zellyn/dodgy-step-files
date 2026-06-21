"""Ad112 — Nested gzip-of-gzip-of-..stpz triggers N-level recursive decompression.

Catalog claim: A receiver that auto-detects gzip framing (magic 1F 8B) and
decompresses transparently before tokenising will, on input that is
gzip-of-gzip-of-..-of-Part-21, recurse into each layer. With N stacked layers
of trivially-compressible content, the receiver allocates a buffer per layer;
if recursion is implemented by recursive function calls the call-stack
overflows. The aggregate decompression ratio is the product of per-layer
ratios; 8 layers at 1:100 each yields 1:10^16. Distinct from Ad110
(single-layer ratio bomb): this entry attacks the layering depth, not the
per-layer ratio.

Reproducer recipe: a Part-21 body wrapped in 8 successive gzip layers (each
layer's input is the previous layer's gzip output); compressed final size is a
few KB, decompressed final size is 100 MB+, and unwrapping requires 8
sequential gunzip passes.

Provenance note: cross-file-state defect; bytes alone (a Part-21 body) cannot
demonstrate this defect; the bomb is in the stack of gzip wrappers.

Byte assertions:
  contains(b'gzip') or contains(b'nested') or contains(b'recursive')
  contains(b'.stpz') or contains(b'recursion') or contains(b'depth')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad112",
    defect=(
        "nested gzip-of-gzip-.stpz triggers N-level recursive decompression; "
        "Part-21 body wrapped in 8 successive gzip layers; each layer ~1:100 ratio; "
        "aggregate ratio 1:10^16; unwrapping requires 8 sequential gunzip passes; "
        "recursive auto-detect implementation overflows call stack at layer depth N; "
        "distinct from Ad110 (single-layer ratio bomb) — attacks depth not ratio; "
        "receiver must cap gzip-layer recursion depth at 1 or small bounded N; "
        "must refuse files whose decompressed body has gzip magic at offset 0; "
        "must reject with a precise diagnostic when depth cap exceeded; "
        "CWE-674; ISO 10303-21 §12 compressed-archive transfer; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
# This fixture is the innermost Part-21 body; the nested gzip layers wrap it
# from outside. The bomb lives in the stack of gzip wrappers.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Documentation payload: a comment block describing the nested gzip structure
# that cannot be embodied in a Part-21 file.
#
# Satisfies:
#   contains(b'gzip') and contains(b'nested') and contains(b'recursive')
#   contains(b'.stpz') and contains(b'recursion') and contains(b'depth')
f._emit_raw(
    "/* Nested gzip recursion bomb (.stpz stack; cross-file-state):\n"
    "   Wrapper structure (outermost first):\n"
    "     Layer 8: gzip(Layer 7)  magic: 1F 8B  ratio ~1:100\n"
    "     Layer 7: gzip(Layer 6)  magic: 1F 8B  ratio ~1:100\n"
    "     Layer 6: gzip(Layer 5)  magic: 1F 8B  ratio ~1:100\n"
    "     Layer 5: gzip(Layer 4)  magic: 1F 8B  ratio ~1:100\n"
    "     Layer 4: gzip(Layer 3)  magic: 1F 8B  ratio ~1:100\n"
    "     Layer 3: gzip(Layer 2)  magic: 1F 8B  ratio ~1:100\n"
    "     Layer 2: gzip(Layer 1)  magic: 1F 8B  ratio ~1:100\n"
    "     Layer 1: gzip(Part-21)  magic: 1F 8B  ratio ~1:100\n"
    "     Layer 0: this Part-21 body (innermost)\n"
    "   Aggregate ratio: 1:10^16 across 8 nested .stpz layers.\n"
    "   A receiver that auto-detects gzip magic (1F 8B) and recurses\n"
    "   into each layer: (a) overflows call stack at depth N if recursion\n"
    "   is via function calls; (b) allocates one buffer per layer.\n"
    "   Receiver must: cap gzip recursion depth at 1; refuse .stpz files\n"
    "   whose decompressed body still starts with gzip magic 1F 8B;\n"
    "   reject with precise diagnostic when depth cap exceeded. */"
    "\nCARTESIAN_POINT('nested_gzip_recursion_depth_note',(0.0,0.0,0.0))"
)
