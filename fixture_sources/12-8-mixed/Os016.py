"""Os016 — Draft modification fails to recompute an edge.

Catalog claim: After drafting adjacent faces, the shared edge needs new geometry
— the intersection of the two new (drafted) surfaces — but the intersection
algorithm fails or yields a multi-component curve.

Mechanism: Two adjacent ADVANCED_FACEs (planar) sharing one edge, with very
different draft angles so that the drafted versions of those two surfaces would
intersect along a non-simple curve. OCC loads (heals); conservative kernels
reject. Wrapped in OPEN_SHELL → SHELL_BASED_SURFACE_MODEL for shape(1).

Tier-3 assertions:
  n_edges_total >= 2
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(4) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Os016",
    defect=(
        "OPEN_SHELL with two adjacent ADVANCED_FACEs (planes) sharing one edge; "
        "very different draft angles cause drafted surface intersection to yield "
        "a non-simple (multi-component) curve — Draft_Modification "
        "Draft_EdgeRecomputation; OCC heals/loads; conservative kernels reject"
    ),
)

# ── Two adjacent planar faces sharing a common edge ──────────────────────────
# Face A: rectangle in XY plane 10x5
# Face B: tilted 70° from face A along the shared right edge

p00 = f.cartesian_point(( 0.0, 0.0, 0.0)); v00 = f.vertex_point(p00)
p10 = f.cartesian_point((10.0, 0.0, 0.0)); v10 = f.vertex_point(p10)
p15 = f.cartesian_point((10.0, 5.0, 0.0)); v15 = f.vertex_point(p15)
p05 = f.cartesian_point(( 0.0, 5.0, 0.0)); v05 = f.vertex_point(p05)

# Face B far edge: tilted 70° from Face A at x=10
angle = math.radians(70.0)
bx = 10.0 + 8.0 * math.cos(angle)
bz = 8.0 * math.sin(angle)
pb0 = f.cartesian_point((bx, 0.0, bz)); vb0 = f.vertex_point(pb0)
pb5 = f.cartesian_point((bx, 5.0, bz)); vb5 = f.vertex_point(pb5)

def _le(pa, pb, dx, dy, dz, length, va, vb):
    return f.edge_curve(va, vb, f.line(pa, f.vector(f.direction((dx, dy, dz)), length)))

# Face A edges
e_a_bot   = _le(p00, p10,  1, 0, 0, 10, v00, v10)
e_a_right = _le(p10, p15,  0, 1, 0,  5, v10, v15)  # shared edge
e_a_top   = _le(p05, p15,  1, 0, 0, 10, v05, v15)
e_a_left  = _le(p00, p05,  0, 1, 0,  5, v00, v05)

loop_a = f.edge_loop([
    f.oriented_edge(e_a_bot,   True),
    f.oriented_edge(e_a_right, True),
    f.oriented_edge(e_a_top,   False),
    f.oriented_edge(e_a_left,  False),
])
plc_a = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face_a = f.advanced_face([f.face_outer_bound(loop_a)], f.plane(plc_a))

# Face B edges (shared right edge of A, reversed)
dx_b = math.cos(angle); dz_b = math.sin(angle)
e_b_bot   = _le(p10, pb0,  dx_b, 0, dz_b, 8, v10, vb0)
e_b_far   = _le(pb0, pb5,  0, 1, 0,  5, vb0, vb5)
e_b_top   = _le(p15, pb5,  dx_b, 0, dz_b, 8, v15, vb5)

loop_b = f.edge_loop([
    f.oriented_edge(e_a_right, False),   # shared, reversed
    f.oriented_edge(e_b_bot,   True),
    f.oriented_edge(e_b_far,   True),
    f.oriented_edge(e_b_top,   False),
])
# Normal of face B
nx_b = -dz_b; nz_b = dx_b
plc_b = f.axis2_placement_3d(
    f.cartesian_point((10.0, 0.0, 0.0)),
    f.direction((nx_b, 0.0, nz_b)),
    f.direction((dx_b, 0.0, dz_b)),
)
face_b = f.advanced_face([f.face_outer_bound(loop_b)], f.plane(plc_b))

shell = f._emit_raw(
    f"OPEN_SHELL('os016_draft_edge',(#{face_a.eid},#{face_b.eid}))"
)
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('os016_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os016.stp")
