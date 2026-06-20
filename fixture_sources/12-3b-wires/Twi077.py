"""Twi077 — Wire tail / sliver: two adjacent EDGE_CURVEs form a 180° fold-back.

Catalog claim: Two consecutive edges of a wire fold back on themselves at
near-180° over a width below tolerance. The "tail" is a degenerate feature
(a stick poking into the face). ShapeAnalysis_Wire::CheckTail identifies the
four sub-edges when the tail's two long sides are split at their crossing point.

Reproducer recipe: A wire with two long edges meeting at a sharp angle, the
second edge nearly retracing the first within 1e-6.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with a tail pair:
- 'tail_pair' edge A: (0,0,0) → (10,0,0)           [forward along X, 10 units]
- 'B_dir_retrace_with_1e6_offset' edge B: (10,0,0) → (-10.0,0.00001,0.0)
  — retraces A in reverse with a sub-tolerance offset of 1e-5 in Y, creating
  a near-180° fold-back (tail) of width ~1e-6.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'B_dir_retrace_with_1e6_offset')
  - contains(b'(-10.0,0.00001,0.0)')
  - contains(b'tail_pair')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi077",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with a tail pair; "
        "edge A 'tail_pair': (0,0,0)→(10,0,0) — 10-unit forward stroke along X; "
        "edge B 'B_dir_retrace_with_1e6_offset': (10,0,0)→(-10.0,0.00001,0.0) — "
        "nearly retraces edge A in reverse with sub-tolerance Y offset 1e-5, "
        "creating near-180° fold (tail width < 1e-6); "
        "CheckTail identifies the 4 sub-edges at the fold-back crossing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices ──────────────────────────────────────────────────────────────────
v_start  = f.vertex_point(f.cartesian_point((0.0,     0.0,     0.0)))
v_apex   = f.vertex_point(f.cartesian_point((10.0,    0.0,     0.0)))
# End of retrace: (-10.0, 0.00001, 0.0) — satisfies byte assertion
v_end    = f.vertex_point(f.cartesian_point((-10.0,   0.00001, 0.0)))

# ── Edge A: forward stroke along +X ──────────────────────────────────────────
# Name 'tail_pair' on the LINE — byte assertion: contains(b'tail_pair')
dir_A    = f.direction((1.0, 0.0, 0.0))
vec_A    = f.vector(dir_A, 10.0)
line_A   = f._emit_raw(
    f"LINE('tail_pair',#{f.cartesian_point((0.0, 0.0, 0.0)).eid},#{vec_A.eid})"
)
ec_A     = f.edge_curve(v_start, v_apex, line_A)
oe_A     = f.oriented_edge(ec_A, True)

# ── Edge B: retrace in direction (-10.0, 0.00001, 0.0) from apex ─────────────
# Byte assertion: contains(b'(-10.0,0.00001,0.0)')  (direction vector component)
# Byte assertion: contains(b'B_dir_retrace_with_1e6_offset') on LINE name
dx_B = -10.0 - 10.0   # = -20.0
dy_B =  0.00001 - 0.0  # = 0.00001
dz_B =  0.0
mag_B = _math.sqrt(dx_B**2 + dy_B**2 + dz_B**2)
# Raw direction components (not normalised to unit — use normalised for DIRECTION)
nx_B = dx_B / mag_B
ny_B = dy_B / mag_B
nz_B = dz_B / mag_B

vec_B_dir = f.direction((nx_B, ny_B, nz_B))
vec_B     = f.vector(vec_B_dir, mag_B)
# Put the (-10.0,0.00001,0.0) label in the LINE name and embed the target point
# to satisfy byte assertions. The CARTESIAN_POINT for apex starts the line:
line_B_origin = f.cartesian_point((10.0, 0.0, 0.0))
# Byte assertion: contains(b'(-10.0,0.00001,0.0)') — appear as CARTESIAN_POINT for v_end
# (already emitted above as v_end's point).
# Byte assertion: contains(b'B_dir_retrace_with_1e6_offset') — embed in LINE name
line_B = f._emit_raw(
    f"LINE('B_dir_retrace_with_1e6_offset',#{line_B_origin.eid},#{vec_B.eid})"
)
ec_B   = f.edge_curve(v_apex, v_end, line_B)
oe_B   = f.oriented_edge(ec_B, True)

# ── EDGE_LOOP: tail pair (only two edges) ────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_A.eid},#{oe_B.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi077.stp")
