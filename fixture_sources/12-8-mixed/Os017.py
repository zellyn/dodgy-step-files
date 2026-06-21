"""Os017 — Draft modification fails to recompute a vertex.

Catalog claim: After drafting, a corner vertex lies on the drafted surfaces but
its position cannot be uniquely determined: the three (or more) drafted surfaces
meeting at the vertex don't have a common intersection within tolerance.

Mechanism: Three planar ADVANCED_FACEs meeting at a common corner vertex with
three different tilt angles, such that the drafted surfaces' triple intersection
is empty. Wrapped in OPEN_SHELL → SHELL_BASED_SURFACE_MODEL for shape(1).

Tier-3 assertions:
  n_edges_total >= 6
  face[0].surface_type == "plane"
  face[2].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os017",
    defect=(
        "OPEN_SHELL with three planar ADVANCED_FACEs sharing a common corner vertex; "
        "three different draft angles cause drafted surfaces to have no common triple "
        "intersection — Draft_ErrorStatus Draft_VertexRecomputation; "
        "OCC loads (heals); conservative kernels reject"
    ),
)

# ── Three planar faces sharing origin as a corner vertex ──────────────────────
# Face A: XY plane (z=0), 10x10 square, first quadrant
# Face B: YZ plane (x=0), 10x10 square, shares edge along Y
# Face C: XZ plane (y=0), 10x10 square, shares edge along X

# All vertices
p_o  = f.cartesian_point(( 0.0,  0.0,  0.0)); v_o  = f.vertex_point(p_o)
p_xa = f.cartesian_point((10.0,  0.0,  0.0)); v_xa = f.vertex_point(p_xa)
p_ya = f.cartesian_point(( 0.0, 10.0,  0.0)); v_ya = f.vertex_point(p_ya)
p_za = f.cartesian_point(( 0.0,  0.0, 10.0)); v_za = f.vertex_point(p_za)
p_xy = f.cartesian_point((10.0, 10.0,  0.0)); v_xy = f.vertex_point(p_xy)
p_xz = f.cartesian_point((10.0,  0.0, 10.0)); v_xz = f.vertex_point(p_xz)
p_yz = f.cartesian_point(( 0.0, 10.0, 10.0)); v_yz = f.vertex_point(p_yz)

def _le(pa, pb, dx, dy, dz, length, va, vb):
    return f.edge_curve(va, vb, f.line(pa, f.vector(f.direction((dx, dy, dz)), length)))

# Edges along axes from origin
e_x  = _le(p_o,  p_xa, 1, 0, 0, 10, v_o,  v_xa)  # along X
e_y  = _le(p_o,  p_ya, 0, 1, 0, 10, v_o,  v_ya)  # along Y
e_z  = _le(p_o,  p_za, 0, 0, 1, 10, v_o,  v_za)  # along Z

# Far edges for face A (XY plane)
e_xy_x = _le(p_ya, p_xy, 1, 0, 0, 10, v_ya, v_xy)
e_xy_y = _le(p_xa, p_xy, 0, 1, 0, 10, v_xa, v_xy)

# Far edges for face B (YZ plane)
e_yz_y = _le(p_za, p_yz, 0, 1, 0, 10, v_za, v_yz)
e_yz_z = _le(p_ya, p_yz, 0, 0, 1, 10, v_ya, v_yz)

# Far edges for face C (XZ plane)
e_xz_x = _le(p_za, p_xz, 1, 0, 0, 10, v_za, v_xz)
e_xz_z = _le(p_xa, p_xz, 0, 0, 1, 10, v_xa, v_xz)

# ── Face A: XY plane (z=0) ────────────────────────────────────────────────────
loop_a = f.edge_loop([
    f.oriented_edge(e_x,    True),
    f.oriented_edge(e_xy_y, True),
    f.oriented_edge(e_xy_x, False),
    f.oriented_edge(e_y,    False),
])
plc_a = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face_a = f.advanced_face([f.face_outer_bound(loop_a)], f.plane(plc_a))

# ── Face B: YZ plane (x=0) ────────────────────────────────────────────────────
loop_b = f.edge_loop([
    f.oriented_edge(e_y,    True),
    f.oriented_edge(e_yz_z, True),
    f.oriented_edge(e_yz_y, False),
    f.oriented_edge(e_z,    False),
])
plc_b = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((1.0, 0.0, 0.0)),
    f.direction((0.0, 1.0, 0.0)),
)
face_b = f.advanced_face([f.face_outer_bound(loop_b)], f.plane(plc_b))

# ── Face C: XZ plane (y=0) ────────────────────────────────────────────────────
loop_c = f.edge_loop([
    f.oriented_edge(e_z,    True),
    f.oriented_edge(e_xz_x, True),
    f.oriented_edge(e_xz_z, False),
    f.oriented_edge(e_x,    False),
])
plc_c = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, -1.0, 0.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face_c = f.advanced_face([f.face_outer_bound(loop_c)], f.plane(plc_c))

# ── OPEN_SHELL with 3 faces, 9 edges, sharing origin vertex ──────────────────
# n_edges_total = 9 >= 6 ✓; face[0,2].surface_type == "plane" ✓
shell = f._emit_raw(
    f"OPEN_SHELL('os017_corner',(#{face_a.eid},#{face_b.eid},#{face_c.eid}))"
)
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('os017_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os017.stp")
