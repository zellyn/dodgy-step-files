"""Twi275 — CheckLoop Multi-Vertex Self-Loop

Catalog claim: Three self-loop edges at V1. Tests double-append binding and
multi-vertex gate. Extent=6 after appends triggers loop detection.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with three edges
'mvsloop_e1', 'mvsloop_e2', 'mvsloop_e3', all self-loops at V1 (each connects
V1 to V1). The CheckLoop algorithm accumulates vertex extent by double-appending
each edge endpoint to a vertex occurrence list; three self-loops at V1 produce
extent=6 for V1 (2 appends per edge × 3 edges). When extent exceeds the
multi-vertex gate threshold, loop detection triggers IS the double-append
binding defect. GEOMETRIC_CURVE_SET yields empty on import.

Byte assertions:
  - contains(b'mvsloop_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi275",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with three self-loop edges all at V1; "
        "mvsloop_e1: V1->V1 self-loop at (0,0,0); "
        "mvsloop_e2: V1->V1 self-loop at (0,0,0); "
        "mvsloop_e3: V1->V1 self-loop at (0,0,0); "
        "CheckLoop double-appends each endpoint: extent=6 for V1 after three edges triggers multi-vertex gate; "
        "double-append binding IS the loop detection defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Single vertex V1 — all three edges are self-loops at V1
vV1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))

# mvsloop_e1: V1 -> V1 self-loop (direction X)
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('mvsloop_e1',#{vV1.eid},#{vV1.eid},#{ln1.eid},.T.)"
)

# mvsloop_e2: V1 -> V1 self-loop (direction Y)
d2  = f.direction((0.0, 1.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('mvsloop_e2',#{vV1.eid},#{vV1.eid},#{ln2.eid},.T.)"
)

# mvsloop_e3: V1 -> V1 self-loop (direction Z)
d3  = f.direction((0.0, 0.0, 1.0))
v3  = f.vector(d3, 1.0)
ln3 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v3)
ec3 = f._emit_raw(
    f"EDGE_CURVE('mvsloop_e3',#{vV1.eid},#{vV1.eid},#{ln3.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# EDGE_LOOP: three self-loops at V1 — extent=6 triggers multi-vertex gate IS defect
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi275.stp")
