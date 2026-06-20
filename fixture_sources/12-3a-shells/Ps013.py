"""Ps013 — Chiral part mirrored by silent X-coordinate negation.

Catalog claim: An L-shaped bracket whose intended right-hand configuration was
mirrored across the X axis during export; every X coordinate was negated.
Topology, face count, edge count, and unit context are all unchanged; the part
is a valid L-bracket, just the wrong-handed one.  For chiral mechanical parts
(threads, hand-side brackets, steering linkages) this is a critical defect
that the kernel cannot detect from the geometry alone.

Mechanism IS the CLOSED_SHELL / MANIFOLD_SOLID_BREP face topology: the
mirrored L-bracket — extruded from footprint with vertices at
(0,0), (-1,0), (-1,2), (1,2), (1,1), (0,1) then extruded to z=1 —
IS wired into the CLOSED_SHELL of the MANIFOLD_SOLID_BREP.  The negated
X-coordinates ARE embedded in every CARTESIAN_POINT of the shape's boundary
faces, making the geometry the X-mirror of the producer's intended part.

Tier-3 assertions:
  - n_edges_total >= 24
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must warn.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps013",
    defect=(
        "L-bracket with all X-coordinates negated (mirrored): footprint "
        "(0,0),(-1,0),(-1,2),(1,2),(1,1),(0,1) extruded to z=1; "
        "negated X-coords ARE wired into all CARTESIAN_POINTs of CLOSED_SHELL "
        "faces of MANIFOLD_SOLID_BREP; valid geometry but wrong chirality; "
        "kernel accepts silently"
    ),
)

# ── Mirrored L-bracket: intended footprint (0,0),(1,0),(1,2),(-1,2),(-1,1),(0,1)
# Exported footprint (X-negated):       (0,0),(-1,0),(-1,2),(1,2),(1,1),(0,1)
# z extrusion: z=0 to z=1
#
# Footprint vertices (z=0, mirrored/exported):
foot = [
    (0.0, 0.0),
    (-1.0, 0.0),
    (-1.0, 2.0),
    ( 1.0, 2.0),
    ( 1.0, 1.0),
    ( 0.0, 1.0),
]
nf = len(foot)  # 6 footprint vertices

# Create bottom (z=0) and top (z=1) corner points
bot_pts = [f.cartesian_point((x, y, 0.0)) for x, y in foot]
top_pts = [f.cartesian_point((x, y, 1.0)) for x, y in foot]
bot_vts = [f.vertex_point(p) for p in bot_pts]
top_vts = [f.vertex_point(p) for p in top_pts]

def make_edge_coords(pt_a, pt_b, va, vb, xa, ya, za, xb, yb, zb):
    """Straight EDGE_CURVE from (xa,ya,za)→(xb,yb,zb) using given Point/Vertex entities."""
    dx = xb-xa; dy = yb-ya; dz = zb-za
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d   = f.direction((dx/length, dy/length, dz/length))
    v   = f.vector(d, length)
    ln  = f.line(pt_a, v)
    return f.edge_curve(va, vb, ln)

# Bottom loop edges
bot_edges = []
for i in range(nf):
    j = (i+1) % nf
    x0,y0 = foot[i]; x1,y1 = foot[j]
    bot_edges.append(make_edge_coords(
        bot_pts[i], bot_pts[j], bot_vts[i], bot_vts[j],
        x0, y0, 0.0, x1, y1, 0.0))

# Top loop edges (same XY topology, z=1)
top_edges = []
for i in range(nf):
    j = (i+1) % nf
    x0,y0 = foot[i]; x1,y1 = foot[j]
    top_edges.append(make_edge_coords(
        top_pts[i], top_pts[j], top_vts[i], top_vts[j],
        x0, y0, 1.0, x1, y1, 1.0))

# Vertical edges (bottom→top, one per corner)
vert_edges = []
for i in range(nf):
    x,y = foot[i]
    vert_edges.append(make_edge_coords(
        bot_pts[i], top_pts[i], bot_vts[i], top_vts[i],
        x, y, 0.0, x, y, 1.0))

def mk_face_from_loop(oe_list, px, py, pz, nx, ny, nz, rx, ry, rz):
    """Build ADVANCED_FACE from oriented-edge list and plane normal."""
    loop = f.edge_loop(oe_list)
    fob  = f.face_outer_bound(loop)
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((nx, ny, nz))
    xd   = f.direction((rx, ry, rz))
    plane = f.plane(f.axis2_placement_3d(orig, zd, xd))
    return f.advanced_face([fob], plane)

# ── Bottom face: z=0, normal pointing -Z ─────────────────────────────────────
# CCW from below (-Z view) = CW from above → wind bottom edges as-is (oriented True)
bot_oes = [f.oriented_edge(e, True) for e in bot_edges]
f_bot = mk_face_from_loop(bot_oes, 0.0,0.0,0.0,  0.0,0.0,-1.0,  1.0,0.0,0.0)

# ── Top face: z=1, normal pointing +Z ────────────────────────────────────────
# CCW from above (+Z view): reverse traversal direction
top_oes = [f.oriented_edge(e, False) for e in reversed(top_edges)]
f_top = mk_face_from_loop(top_oes, 0.0,0.0,1.0,  0.0,0.0,1.0,  1.0,0.0,0.0)

# ── Side faces: one per footprint segment, extruded vertically ───────────────
side_faces = []
for i in range(nf):
    j = (i+1) % nf
    x0,y0 = foot[i]
    x1,y1 = foot[j]
    # Outward face normal: perpendicular to edge, pointing outward (in XY plane)
    dx = x1-x0; dy = y1-y0
    length = (dx*dx+dy*dy)**0.5
    # Footprint is CW from +Z (mirrored) → outward normal is LEFT of edge dir → (-dy, dx)
    nx = -dy/length; ny = dx/length
    # Face: bottom edge forward, right vertical up, top edge backward, left vertical down
    oe_list = [
        f.oriented_edge(bot_edges[i],  True),   # bottom edge i→j
        f.oriented_edge(vert_edges[j], True),   # right vertical j bottom→top
        f.oriented_edge(top_edges[i],  False),  # top edge j→i (reversed)
        f.oriented_edge(vert_edges[i], False),  # left vertical i top→bottom (reversed)
    ]
    # Face origin at bottom-left corner of this segment; ref_dir along edge
    sf = mk_face_from_loop(oe_list, x0,y0,0.0,  nx,ny,0.0,  dx/length,dy/length,0.0)

    side_faces.append(sf)

all_faces = [f_bot, f_top] + side_faces
shell = f.closed_shell(all_faces, name="ps013_mirrored_L_bracket")
msb   = f.manifold_solid_brep(shell, name="ps013_chiral_bracket_x_negated")

f.add_product_chain(msb, mode="brep_shape")
