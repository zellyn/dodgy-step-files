"""Twi099 — EDGE_CURVE whose start and end vertex point at the same VERTEX_POINT.

Catalog claim: An EDGE_CURVE references the same VERTEX_POINT instance for
both its start and end vertex slots. This makes the edge a single-point
self-loop; a degenerate edge with zero arc length. The producer is OCCT
itself, so the same kernel that emits the file is the only one that fully
accepts it; strict downstream readers flag it as an invariant violation.

Reproducer recipe: #10=VERTEX_POINT('',#11); followed by
#20=EDGE_CURVE('',#10,#10,#15,.T.); referencing the same vertex twice —
start and end both #10.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. The EDGE_CURVE
references vertex #10 for BOTH start and end (self-loop degenerate edge).
The underlying curve is a LINE so the edge is not a full closed circle.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'EDGE_CURVE')
  - matches(rb'EDGE_CURVE\\([^)]*#10,#10')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi099",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with one EDGE_CURVE; "
        "EDGE_CURVE references the SAME VERTEX_POINT for both start and end (self-loop); "
        "underlying curve is a LINE (not a closed curve) so edge is degenerate zero-length; "
        "OCCT itself generates this when two endpoint vertices fall within tolerance and merge; "
        "strict readers flag E_DEGENERATE_EDGE; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Build entities manually so vertex #10 is referenced twice in EDGE_CURVE ───
# We use _emit_raw to control the exact entity IDs that appear in the byte
# assertion: matches(rb'EDGE_CURVE\([^)]*#10,#10')

# Emit some geometry first so the vertex gets an early low ID (≤10).
# StepFile allocates IDs sequentially from 1, so emit 9 dummy geometry
# entities then the vertex on the 10th slot.

# We need entity IDs to be predictable. Let's just use _emit_raw for the key
# entities and rely on the regex matching whatever IDs appear as long as
# start==end vertex in the EDGE_CURVE line.

# Approach: use _emit_raw for all defect-relevant entities, embedding
# forward references. We'll pre-compute IDs we need.
# vertex = ID 1, cartesian_point for it = first entity.

pt = f.cartesian_point((5.0, 5.0, 0.0))   # #1 — the single vertex location

# Line from the same point in direction X (non-null so it's geometrically
# valid as a curve, but start==end makes it degenerate)
ldir = f.direction((1.0, 0.0, 0.0))       # #2
lvec = f.vector(ldir, 1.0)                 # #3
line = f.line(f.cartesian_point((5.0, 5.0, 0.0)), lvec)  # #5 (pt for line is #4)

# VERTEX_POINT referencing pt (#1)
# We want the vertex to have a known ID. Let's just record whatever ID it gets.
vp = f._emit("VERTEX_POINT", pt, name="")   # gets next ID, e.g. #6

# Now emit EDGE_CURVE with same vertex for start AND end.
# Byte assertions: contains(b'EDGE_CURVE') and matches start==end
# We use _emit_raw so we can hard-code the same entity ref twice.
ec = f._emit_raw(
    f"EDGE_CURVE('',#{vp.eid},#{vp.eid},#{line.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi099.stp")
