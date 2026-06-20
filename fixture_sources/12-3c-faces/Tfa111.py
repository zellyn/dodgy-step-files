"""Tfa111 — ShapeFix_Face.FixSmallAreaWire mixed-context.

Catalog claim: Face with small inner wire AND large inner wire; FixSmallAreaWire
removes small one but accidentally disturbs the large one's vertex references.
Mixed-context scenario tests vertex-index corruption introduced when small-wire
removal accidentally mutates large-wire edges' vertex pointers.

Mechanism: MANIFOLD_SOLID_BREP with a planar 10×10 square face at z=0 carrying
two inner FACE_BOUND holes:
  - Large hole:  2×2 square at center (area 4.0)
  - Small hole:  0.05×0.05 square at corner (area 0.0025)
FixSmallAreaWire should remove only the small hole but must preserve large-hole
edge topology intact. The defect face IS on the live CLOSED_SHELL traversal path.

Byte assertions:
  - contains(b'FACE_BOUND')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa111",
    defect=(
        "CLOSED_SHELL: planar 10×10 outer face at z=0 with two inner FACE_BOUND holes; "
        "large hole 2×2 at center (area 4.0) and small hole 0.05×0.05 at corner (area 0.0025); "
        "ShapeFix_Face::FixSmallAreaWire removes small hole but corrupts large-hole "
        "edge vertex references during removal; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

def make_rect_loop(x0, y0, x1, y1, z=0.0):
    """Build a 4-edge rectangular CCW edge loop at height z."""
    p0 = f.cartesian_point((x0, y0, z))
    p1 = f.cartesian_point((x1, y0, z))
    p2 = f.cartesian_point((x1, y1, z))
    p3 = f.cartesian_point((x0, y1, z))
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    dx = x1 - x0; dy = y1 - y0
    e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0,  0.0, 0.0)), dx)))
    e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0,  1.0, 0.0)), dy)))
    e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0,  0.0, 0.0)), dx)))
    e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0, -1.0, 0.0)), dy)))
    return f.edge_loop([
        f.oriented_edge(e0, True), f.oriented_edge(e1, True),
        f.oriented_edge(e2, True), f.oriented_edge(e3, True),
    ])

# Outer 10×10 face at z=0
outer_loop = make_rect_loop(0.0, 0.0, 10.0, 10.0, z=0.0)

# Large inner hole: 2×2 at center (x=4..6, y=4..6); CW winding (reversed) for hole
large_hole_loop = make_rect_loop(4.0, 4.0, 6.0, 6.0, z=0.0)

# Small inner hole: 0.05×0.05 at corner (x=0.1..0.15, y=0.1..0.15); CW winding for hole
small_hole_loop = make_rect_loop(0.1, 0.1, 0.15, 0.15, z=0.0)

# Plane at z=0, normal +Z
orig_z0 = f.cartesian_point((0.0, 0.0, 0.0))
plc_z0  = f.axis2_placement_3d(orig_z0, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))

# Defect face: outer bound + two inner holes (orientation .F. for inner loops = holes)
defect_face = f.advanced_face([
    f.face_outer_bound(outer_loop, True),
    f.face_bound(large_hole_loop, False),   # large hole, CW orientation
    f.face_bound(small_hole_loop, False),   # small hole, CW orientation
], f.plane(plc_z0))

# Companion flat back face at z=-1 (1×1) to close the shell as a simple solid
# For shape(1): build a thin slab. We use a simple 10×10×1 box but omit inner
# holes on the other faces (they don't have the defect).
# Bottom face at z=-1
p_b0 = f.cartesian_point((0.0,  0.0,  -1.0))
p_b1 = f.cartesian_point((10.0, 0.0,  -1.0))
p_b2 = f.cartesian_point((10.0, 10.0, -1.0))
p_b3 = f.cartesian_point((0.0,  10.0, -1.0))
vb0 = f.vertex_point(p_b0); vb1 = f.vertex_point(p_b1)
vb2 = f.vertex_point(p_b2); vb3 = f.vertex_point(p_b3)
eb0 = f.edge_curve(vb0, vb1, f.line(p_b0, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
eb1 = f.edge_curve(vb1, vb2, f.line(p_b1, f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
eb2 = f.edge_curve(vb2, vb3, f.line(p_b2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
eb3 = f.edge_curve(vb3, vb0, f.line(p_b3, f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))
bot_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
    f.oriented_edge(eb2, True), f.oriented_edge(eb3, True),
])
bot_face = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(
    f.axis2_placement_3d(p_b0, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))))

# Top corners for z=0 plane
p_t0 = f.cartesian_point((0.0,  0.0,  0.0))
p_t1 = f.cartesian_point((10.0, 0.0,  0.0))
p_t2 = f.cartesian_point((10.0, 10.0, 0.0))
p_t3 = f.cartesian_point((0.0,  10.0, 0.0))
vt0 = f.vertex_point(p_t0); vt1 = f.vertex_point(p_t1)
vt2 = f.vertex_point(p_t2); vt3 = f.vertex_point(p_t3)
et0 = f.edge_curve(vt0, vt1, f.line(p_t0, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
et1 = f.edge_curve(vt1, vt2, f.line(p_t1, f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
et2 = f.edge_curve(vt2, vt3, f.line(p_t2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
et3 = f.edge_curve(vt3, vt0, f.line(p_t3, f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))

# Vertical edges (z=0 down to z=-1)
ev0 = f.edge_curve(vt0, vb0, f.line(p_t0, f.vector(f.direction((0.0, 0.0, -1.0)), 1.0)))
ev1 = f.edge_curve(vt1, vb1, f.line(p_t1, f.vector(f.direction((0.0, 0.0, -1.0)), 1.0)))
ev2 = f.edge_curve(vt2, vb2, f.line(p_t2, f.vector(f.direction((0.0, 0.0, -1.0)), 1.0)))
ev3 = f.edge_curve(vt3, vb3, f.line(p_t3, f.vector(f.direction((0.0, 0.0, -1.0)), 1.0)))

# Side faces (4 walls)
# South (y=0): t0→t1→b1→b0
south_loop = f.edge_loop([
    f.oriented_edge(et0, True), f.oriented_edge(ev1, True),
    f.oriented_edge(eb0, False), f.oriented_edge(ev0, False),
])
south_face = f.advanced_face([f.face_outer_bound(south_loop)], f.plane(
    f.axis2_placement_3d(p_t0, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))))

# East (x=10): t1→t2→b2→b1
east_loop = f.edge_loop([
    f.oriented_edge(et1, True), f.oriented_edge(ev2, True),
    f.oriented_edge(eb1, False), f.oriented_edge(ev1, False),
])
east_face = f.advanced_face([f.face_outer_bound(east_loop)], f.plane(
    f.axis2_placement_3d(p_t1, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))))

# North (y=10): t3→t2→b2→b3 (reversed x)
north_loop = f.edge_loop([
    f.oriented_edge(ev3, True), f.oriented_edge(et2, False),
    f.oriented_edge(ev2, False), f.oriented_edge(eb2, False),
])
north_face = f.advanced_face([f.face_outer_bound(north_loop)], f.plane(
    f.axis2_placement_3d(p_t3, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))))

# West (x=0): t0→t3→b3→b0 (reversed y)
west_loop = f.edge_loop([
    f.oriented_edge(ev0, True), f.oriented_edge(et3, False),
    f.oriented_edge(ev3, False), f.oriented_edge(eb3, False),
])
west_face = f.advanced_face([f.face_outer_bound(west_loop)], f.plane(
    f.axis2_placement_3d(p_t0, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ──────────────────────────────────────────
# Note: defect_face has inner holes (FACE_BOUND) but the slab sides don't.
# The shell is topologically open around the inner hole edges, but OCC will
# load it as shape(1) since the outer brep shell is valid.
closed_sh = f.closed_shell([defect_face, bot_face, south_face, east_face, north_face, west_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa111.stp")
