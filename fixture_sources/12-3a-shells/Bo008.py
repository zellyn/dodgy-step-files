"""Bo008 — Sub-shape attached at the wrong topological level.

Catalog claim: A VERTEX_POINT listed as an endpoint of an EDGE_CURVE is not
actually walked-to from the edge's geometry: the edge's start/end parameter
evaluation yields a different point. The vertex was attached at the wrong
topological level by the producer.

Mechanism IS the EDGE_CURVE/VERTEX_POINT topology: the EDGE_CURVE
references vertex #V1 at (0,0,0) as its start, but the LINE geometry begins
at (5,5,5) — V1 does NOT lie on the edge's curve. The stray vertex IS wired
into the edge entity, which IS wired into the FACE_OUTER_BOUND → EDGE_LOOP
→ ADVANCED_FACE → CLOSED_SHELL → MANIFOLD_SOLID_BREP shell topology.

Byte assertions:
  - contains(b'EDGE_CURVE')
  - contains(b'VERTEX_POINT')
  - contains(b'LINE')

Tier-3 assertion: shape_null == True
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo008",
    defect=(
        "EDGE_CURVE start VERTEX_POINT at (0,0,0) does not lie on LINE starting "
        "at (5,5,5); stray vertex IS wired into EDGE_CURVE→EDGE_LOOP→ADVANCED_FACE"
        "→CLOSED_SHELL→MANIFOLD_SOLID_BREP shell topology; strict kernel must reject"
    ),
)

# ── Correct geometry: a single planar square face 1×1 at z=0 ─────────────────
# We build a real face so the shell structure is fully wired in.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Good vertices (used by the other 3 edges)
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0)); p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

# ── CATALOG MECHANISM: stray vertex ─────────────────────────────────────────
# v_stray is at (5,5,5) — not on the bottom edge (which runs along y=z=0).
# The bottom EDGE_CURVE will declare v_stray as its start vertex, yet the
# LINE geometry starts at p0=(0,0,0). The vertex does NOT lie on the curve.
p_stray = f.cartesian_point((5.0, 5.0, 5.0))
v_stray = f.vertex_point(p_stray)  # Byte: VERTEX_POINT at wrong coordinates

# Byte: LINE — the edge curve geometry
d_bot = f.direction((1.0, 0.0, 0.0)); vec_bot = f.vector(d_bot, 1.0)
line_bot = f.line(p0, vec_bot)  # line starts at (0,0,0) — contradicts v_stray

# Byte: EDGE_CURVE — v_stray declared as start, v1 as end; topology vs geometry mismatch
e_bot = f.edge_curve(v_stray, v1, line_bot)  # stray vertex IS wired into edge

# Normal edges for the remaining three sides
d_rgt = f.direction((0.0, 1.0, 0.0)); vec_rgt = f.vector(d_rgt, 1.0)
e_rgt = f.edge_curve(v1, v2, f.line(p1, vec_rgt))

d_top = f.direction((-1.0, 0.0, 0.0)); vec_top = f.vector(d_top, 1.0)
e_top = f.edge_curve(v2, v3, f.line(p2, vec_top))

d_lft = f.direction((0.0, -1.0, 0.0)); vec_lft = f.vector(d_lft, 1.0)
e_lft = f.edge_curve(v3, v0, f.line(p3, vec_lft))

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)

# Stray-vertex edge IS wired: face → loop → EDGE_CURVE with v_stray start vertex
shell = f._emit_raw(f"CLOSED_SHELL('bo008_stray_vertex',(#{face.eid}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('bo008_solid',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
