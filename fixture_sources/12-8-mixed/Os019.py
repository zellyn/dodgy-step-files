"""Os019 — Middle-path computation between two wires fails.

Catalog claim: A medial-axis-style "middle path" between two boundary wires
of a thin region cannot be computed because the wires diverge (fan shape).
The region is not strip-like; the algorithm cannot find a centerline.

Mechanism IS a GEOMETRIC_CURVE_SET containing two EDGE_LOOPs representing
two diverging open wires (fan shape).  OCC sees a GEOMETRIC_CURVE_SET and
returns empty.

Wire 1: horizontal segment along X axis from (0,0,0) to (10,0,0).
Wire 2: diverging segment from (0,0,0) to (10,5,0) — fan angle ~27 deg.

Byte assertions:
  - contains(b'EDGE_LOOP')
  - contains(b'EDGE_CURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Os019",
    defect=(
        "GEOMETRIC_CURVE_SET containing two open EDGE_LOOPs (fan shape); "
        "wire 1: horizontal from (0,0,0) to (10,0,0); "
        "wire 2: diverging from (0,0,0) to (10,5,0); "
        "wires diverge — region is not strip-like; "
        "BRepOffsetAPI_MiddlePath non-strip-region; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Wire 1: horizontal segment from (0,0,0) to (10,0,0) ─────────────────────
p1_a = f.cartesian_point((0.0, 0.0, 0.0))
p1_b = f.cartesian_point((10.0, 0.0, 0.0))
v1_a = f.vertex_point(p1_a)
v1_b = f.vertex_point(p1_b)

dir1  = f.direction((1.0, 0.0, 0.0))
vec1  = f.vector(dir1, 10.0)
ln1   = f.line(p1_a, vec1)
ec1   = f.edge_curve(v1_a, v1_b, ln1, True, name="wire1_edge")   # EDGE_CURVE ✓
oe1   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
loop1 = f._emit_raw(f"EDGE_LOOP('wire1',(#{oe1.eid}))")            # EDGE_LOOP ✓

# ── Wire 2: diverging segment from (0,0,0) to (10,5,0) ──────────────────────
p2_a = f.cartesian_point((0.0, 0.0, 0.0))
p2_b = f.cartesian_point((10.0, 5.0, 0.0))
v2_a = f.vertex_point(p2_a)
v2_b = f.vertex_point(p2_b)

length2 = math.sqrt(100.0 + 25.0)   # sqrt(125)
dx2, dy2 = 10.0 / length2, 5.0 / length2
dir2  = f.direction((dx2, dy2, 0.0))
vec2  = f.vector(dir2, length2)
ln2   = f.line(p2_a, vec2)
ec2   = f.edge_curve(v2_a, v2_b, ln2, True, name="wire2_edge")   # EDGE_CURVE ✓
oe2   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
loop2 = f._emit_raw(f"EDGE_LOOP('wire2',(#{oe2.eid}))")            # EDGE_LOOP ✓

# ── GEOMETRIC_CURVE_SET wrapping both wires ──────────────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop1.eid},#{loop2.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os019.stp")
