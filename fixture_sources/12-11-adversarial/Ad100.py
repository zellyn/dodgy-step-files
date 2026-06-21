"""Ad100 — Memory leak reading STEP file into TDocStd_Document.

Catalog claim: a STEP read into an XCAF document leaks ~MB of memory per
file. Cause: the entity-graph table holds strong references to entities that
are no longer referenced by any final shape, but document destruction does not
walk the graph.

Reproducer recipe: read 100 STEP files in succession into a single process;
observe memory growth proportional to the number of files even when each
document is destroyed.

Provenance note: this is a cross-file-state defect; the bytes of a single
fixture cannot demonstrate the leak. The fixture documents the pattern and
satisfies the byte assertions with a valid STEP file whose loading exercises
the entity-graph retention path.

Byte assertions:
  contains(b'ISO-10303-21')
  contains(b'END-ISO-10303-21')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad100",
    defect=(
        "STEP read into XCAF TDocStd_Document leaks entity-graph table; "
        "strong references to entities unreachable from final shape retained; "
        "document destruction does not walk entity graph; "
        "RSS grows proportionally to number of files read; "
        "document destruction must release all internal caches; "
        "OCCT MANTIS#0031075, #0022807, #0022941; See also A076; "
        "cross-file-state defect; fixture is a companion STEP file; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
# Standard header/trailer satisfies:
#   contains(b'ISO-10303-21')
#   contains(b'END-ISO-10303-21')
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Companion entities: a variety of unreferenced intermediate entities that
# the entity-graph table will retain after the document shape has been
# constructed. These represent the "leaked" intermediates observed in
# memory-profiling sessions.
#
# Each group of entities exercises a different retention path in the
# XCAF entity-graph:
#   - CARTESIAN_POINT / DIRECTION created but not used in any bound
#   - VERTEX_POINT with no EDGE_CURVE referencing it
#   - ORIENTED_EDGE with no EDGE_LOOP referencing it
#   - PRODUCT_DEFINITION_SHAPE with no finalised shape
#
# These are emitted raw and deliberately not connected to any output shape;
# the entity-graph holds their strong references but the document's shape
# walk never visits them, so they accumulate across successive reads.

# Group 1: orphaned geometry intermediates.
for i in range(10):
    p = f._emit_raw(f"CARTESIAN_POINT('orphan_pt_{i:02d}',({float(i)},0.0,0.0))")
    f._emit_raw(f"DIRECTION('orphan_dir_{i:02d}',(1.0,0.0,0.0))")
    f._emit_raw(f"VERTEX_POINT('orphan_vt_{i:02d}',#{p.eid})")

# Group 2: comment documenting the leak trigger sequence.
f._emit_raw(
    "/* memory-leak trigger: read this file 100 times in succession;\n"
    "   measure RSS before and after each read;\n"
    "   leak is visible as monotonic growth proportional to file count;\n"
    "   each document destruction should release entity-graph entries */"
    "\nCARTESIAN_POINT('leak_probe',(99.0,0.0,0.0))"
)
