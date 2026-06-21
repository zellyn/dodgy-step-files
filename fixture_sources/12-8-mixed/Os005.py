"""Os005 — Offset edge-trim step fails (edges don't trim cleanly against neighbours).

Catalog claim: After offsetting each face independently, the edges between
neighbouring offset faces don't intersect cleanly to produce shared trim curves.

Mechanism: Two adjacent planar ADVANCED_FACEs sharing one edge but with very
different tilt angles (making the offset surfaces diverge). The faces share an
edge in the OPEN_SHELL but their outward normals point in directions that would
cause offset edges to miss each other.  Wrapped in SHELL_BASED_SURFACE_MODEL so
OCC loads (heals); conservative kernels should reject.

Tier-3 assertions:
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Os005",
    defect=(
        "OPEN_SHELL with two adjacent ADVANCED_FACEs sharing one edge; "
        "face A: XY plane 10x8; face B: steeply-tilted (80-degree dihedral) plane "
        "sharing the bottom edge of A; offset distances large enough that offset "
        "surfaces miss each other — BRepOffset_MakeOffset CannotTrimEdges; "
        "OCC heals/loads; conservative kernels must reject"
    ),
)

# ── Shared edge vertices ──────────────────────────────────────────────────────
# Face A: 10x8 rectangle in the XY plane (z=0)
# Face B: shares the right edge of A (x=10, y=0..8) and tilts backward (high dihedral)

# All 3D point + vertex pairs we need
p00 = f.cartesian_point(( 0.0,  0.0, 0.0)); v00 = f.vertex_point(p00)
p10 = f.cartesian_point((10.0,  0.0, 0.0)); v10 = f.vertex_point(p10)
p18 = f.cartesian_point((10.0,  8.0, 0.0)); v18 = f.vertex_point(p18)
p08 = f.cartesian_point(( 0.0,  8.0, 0.0)); v08 = f.vertex_point(p08)

# Face B is tilted at 80° up from face A along the shared right edge (x=10)
# The far edge of B is at x=10+10*cos(80°), z=10*sin(80°)
angle_rad = math.radians(80.0)
bx = 10.0 + 10.0 * math.cos(angle_rad)
bz = 10.0 * math.sin(angle_rad)

pb0 = f.cartesian_point((bx, 0.0, bz)); vb0 = f.vertex_point(pb0)
pb8 = f.cartesian_point((bx, 8.0, bz)); vb8 = f.vertex_point(pb8)

# ── Face A edges ──────────────────────────────────────────────────────────────
def _line_edge(pa, pb, dx, dy, dz, length, va, vb):
    return f.edge_curve(va, vb, f.line(pa, f.vector(f.direction((dx, dy, dz)), length)))

e_a_bot  = _line_edge(p00, p10, 1, 0, 0, 10, v00, v10)   # bottom  0→10
e_a_rght = _line_edge(p10, p18, 0, 1, 0,  8, v10, v18)   # right   shared
e_a_top  = _line_edge(p08, p18, 1, 0, 0, 10, v08, v18)   # top     (reversed)
e_a_left = _line_edge(p00, p08, 0, 1, 0,  8, v00, v08)   # left

loop_a = f.edge_loop([
    f.oriented_edge(e_a_bot,  True),
    f.oriented_edge(e_a_rght, True),
    f.oriented_edge(e_a_top,  False),
    f.oriented_edge(e_a_left, False),
])
fob_a = f.face_outer_bound(loop_a)
plc_a = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face_a = f.advanced_face([fob_a], f.plane(plc_a))

# ── Face B edges (shares e_a_rght reversed) ──────────────────────────────────
# Face B normal: perpendicular to B's surface (tilted 80° from XY)
# B: v10→pb0 (far bottom), pb0→pb8 (far side), vb8→v18 (far top reversed), e_a_rght reversed
bdir_x = math.cos(angle_rad)
bdir_z = math.sin(angle_rad)
e_b_bot  = _line_edge(p10, pb0, bdir_x, 0, bdir_z, 10, v10, vb0)
e_b_far  = _line_edge(pb0, pb8, 0, 1, 0, 8, vb0, vb8)
e_b_top  = _line_edge(p18, pb8, bdir_x, 0, bdir_z, 10, v18, vb8)

loop_b = f.edge_loop([
    f.oriented_edge(e_a_rght, False),   # shared edge reversed
    f.oriented_edge(e_b_bot,  True),
    f.oriented_edge(e_b_far,  True),
    f.oriented_edge(e_b_top,  False),
])
fob_b = f.face_outer_bound(loop_b)
# Normal for face B: perpendicular to both Y-axis and the tilt direction
bn_x = -bdir_z  # normal points "outward" (away from face A)
bn_z =  bdir_x
plc_b = f.axis2_placement_3d(
    f.cartesian_point((10.0, 0.0, 0.0)),
    f.direction((bn_x, 0.0, bn_z)),
    f.direction((bdir_x, 0.0, bdir_z)),
)
face_b = f.advanced_face([fob_b], f.plane(plc_b))

# ── OPEN_SHELL wrapping both faces ───────────────────────────────────────────
shell = f._emit_raw(
    f"OPEN_SHELL('os005_tilted',(#{face_a.eid},#{face_b.eid}))"
)
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('os005_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os005.stp")
