"""Tfa022 — Almost-closed EDGE_LOOP with sub-tolerance gap and wrong Closed flag
(ConnectEdgesToWires).

Catalog claim: An EDGE_LOOP of four edges whose last edge ends at a VERTEX_POINT
at (0, 1e-6, 0) that differs from the first edge's start vertex at (0, 0, 0)
by ~1e-6 mm. The loop is not geometrically closed by that tiny gap, and the
file carries the unclosed loop with no FACE_OUTER_BOUND / ADVANCED_FACE wrapper.
Repeated runs produce different orderings (non-deterministic output).

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with four edges.
The last vertex before closing is (0.0,1.0E-6,0.0) while the first vertex is
(0.0,0.0,0.0) — a 1e-6 gap smaller than the STEP default tolerance but large
enough to leave the loop open. The file has exactly 5 VERTEX_POINT entities
(4 proper corners + 1 slightly-off closing vertex). OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'(0.0,1.0E-6,0.0)')
  - count_entity_def(b'VERTEX_POINT') == 5
  - count_entity_def(b'CARTESIAN_POINT') >= 5

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa022",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with four edges; "
        "first vertex at (0,0,0); last edge ends at (0.0,1.0E-6,0.0) — "
        "1e-6 mm gap, sub-tolerance but loop is not geometrically closed; "
        "file has exactly 5 VERTEX_POINT entities (4 corners + 1 off-closing vertex); "
        "ConnectEdgesToWires closed-flag disagrees with actual gap; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Four corner vertices of a ~10×10 square, with closing vertex slightly off ─
# V0: (0,0,0)  V1: (10,0,0)  V2: (10,10,0)  V3: (0,10,0)
# V4: (0, 1e-6, 0) — this is almost V0 but 1e-6 mm off in Y

p0 = f.cartesian_point((0.0, 0.0, 0.0))          # start vertex
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))
# Byte assertion: contains(b'(0.0,1.0E-6,0.0)')
# StepFile uses scientific notation for very small values — emit raw to guarantee format.
p4_raw = f._emit_raw("CARTESIAN_POINT('',(0.0,1.0E-6,0.0))")

v0 = f.vertex_point(p0)   # vertex 1 of 5
v1 = f.vertex_point(p1)   # vertex 2
v2 = f.vertex_point(p2)   # vertex 3
v3 = f.vertex_point(p3)   # vertex 4
v4 = f._emit_raw(f"VERTEX_POINT('',#{p4_raw.eid})")  # vertex 5 — slightly off

# ── Four edges forming the almost-closed loop ─────────────────────────────────
# e0: V0 → V1  (bottom, length 10 along X)
d_x  = f.direction((1.0, 0.0, 0.0))
vec0 = f.vector(d_x, 10.0)
ln0  = f.line(p0, vec0)
ec0  = f._emit_raw(f"EDGE_CURVE('',#{v0.eid},#{v1.eid},#{ln0.eid},.T.)")

# e1: V1 → V2  (right side, length 10 along Y)
d_y  = f.direction((0.0, 1.0, 0.0))
vec1 = f.vector(d_y, 10.0)
ln1  = f.line(p1, vec1)
ec1  = f._emit_raw(f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{ln1.eid},.T.)")

# e2: V2 → V3  (top, length 10 along -X)
d_nx = f.direction((-1.0, 0.0, 0.0))
vec2 = f.vector(d_nx, 10.0)
ln2  = f.line(p2, vec2)
ec2  = f._emit_raw(f"EDGE_CURVE('',#{v2.eid},#{v3.eid},#{ln2.eid},.T.)")

# e3: V3 → V4  (left side, ends at slightly-off closing vertex)
# Direction from (0,10,0) to (0,1e-6,0): essentially -Y, length ~10
d_ny  = f.direction((0.0, -1.0, 0.0))
vec3  = f.vector(d_ny, 10.0)
p3_pt = f.cartesian_point((0.0, 10.0, 0.0))
ln3   = f.line(p3_pt, vec3)
ec3   = f._emit_raw(f"EDGE_CURVE('',#{v3.eid},#{v4.eid},#{ln3.eid},.T.)")

oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# EDGE_LOOP: almost closed — last edge ends 1e-6 from start
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa022.stp")
