"""Twi068 — Wire 3D-gap analysis must enumerate all gaps.

Catalog claim: The wire-wide 3D gap analyzer must visit every consecutive-edge
junction and report each gap individually. A wire with multiple defective
junctions should not be reported as "broken at junction 1" when it also breaks
at junctions 3 and 5.

Reproducer recipe: A four-edge wire where the gaps between edge-pairs (1,2),
(2,3), and (3,4) are each above tolerance.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with four LINE edges:
- e1: (0,0,0) → (1,0,0)
- e2: starts at (1.05,0,0) [gap 0.05] → (2,0,0)
- e3: starts at (2.07,0,0) [gap 0.07] → (2,1,0)
- e4: starts at (2,1.06,0) [gap 0.06] → (0,0,0)
Each consecutive-edge junction has a 3D gap above tolerance. CheckGaps3d must
enumerate all three gaps, not stop at the first. OCC sees a GEOMETRIC_CURVE_SET
and returns empty.

Byte assertions:
  - contains(b'(1.05,0.0,0.0)')
  - contains(b'(2.07,0.0,0.0)')
  - contains(b'(2.0,1.06,0.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi068",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 LINE edges; "
        "junction gaps: e1 ends at (1,0,0), e2 starts at (1.05,0,0) — gap 0.05; "
        "e2 ends at (2,0,0), e3 starts at (2.07,0,0) — gap 0.07; "
        "e3 ends at (2,1,0), e4 starts at (2,1.06,0) — gap 0.06; "
        "CheckGaps3d must enumerate all 3 junction gaps, not stop at first; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices: note intentional position mismatches at junctions ──────────────
# e1: (0,0,0) → (1,0,0)
v1s = f.vertex_point(f.cartesian_point((0.0,    0.0, 0.0)))
v1e = f.vertex_point(f.cartesian_point((1.0,    0.0, 0.0)))   # e1 end

# e2: (1.05,0,0) → (2,0,0)  — gap at junction e1/e2
v2s = f.vertex_point(f.cartesian_point((1.05,   0.0, 0.0)))   # byte assertion
v2e = f.vertex_point(f.cartesian_point((2.0,    0.0, 0.0)))   # e2 end

# e3: (2.07,0,0) → (2,1,0)  — gap at junction e2/e3
v3s = f.vertex_point(f.cartesian_point((2.07,   0.0, 0.0)))   # byte assertion
v3e = f.vertex_point(f.cartesian_point((2.0,    1.0, 0.0)))   # e3 end

# e4: (2,1.06,0) → (0,0,0)  — gap at junction e3/e4
v4s = f.vertex_point(f.cartesian_point((2.0,    1.06, 0.0)))  # byte assertion
# e4 end is also disconnected from e1 start (0,0,0) — additional gap
v4e = f.vertex_point(f.cartesian_point((0.0,    0.0, 0.0)))

# ── Edge e1: (0,0,0)→(1,0,0) ─────────────────────────────────────────────────
e1 = f.edge_curve(
    v1s, v1e,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)
oe1 = f.oriented_edge(e1, True)

# ── Edge e2: (1.05,0,0)→(2,0,0) ─────────────────────────────────────────────
e2 = f.edge_curve(
    v2s, v2e,
    f.line(f.cartesian_point((1.05, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 0.95))
)
oe2 = f.oriented_edge(e2, True)

# ── Edge e3: (2.07,0,0)→(2,1,0) ─────────────────────────────────────────────
dx3 = 2.0 - 2.07
dy3 = 1.0 - 0.0
mag3 = _math.sqrt(dx3**2 + dy3**2)
e3 = f.edge_curve(
    v3s, v3e,
    f.line(f.cartesian_point((2.07, 0.0, 0.0)),
           f.vector(f.direction((dx3 / mag3, dy3 / mag3, 0.0)), mag3))
)
oe3 = f.oriented_edge(e3, True)

# ── Edge e4: (2,1.06,0)→(0,0,0) ─────────────────────────────────────────────
dx4 = 0.0 - 2.0
dy4 = 0.0 - 1.06
mag4 = _math.sqrt(dx4**2 + dy4**2)
e4 = f.edge_curve(
    v4s, v4e,
    f.line(f.cartesian_point((2.0, 1.06, 0.0)),
           f.vector(f.direction((dx4 / mag4, dy4 / mag4, 0.0)), mag4))
)
oe4 = f.oriented_edge(e4, True)

# ── EDGE_LOOP: 4 edges with 3D gaps at every junction ────────────────────────
loop = f.edge_loop([oe1, oe2, oe3, oe4])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi068.stp")
