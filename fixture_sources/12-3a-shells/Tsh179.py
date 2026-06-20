"""Tsh179 — ShapeFix_Shell.FixFaceOrientation hex-prism orientation propagation oscillation.

Catalog claim: FixFaceOrientation() on an 8-face hex prism (base + top + 6
lateral faces) propagates orientation by edge adjacency; lateral faces alternate
between correct and flipped normals, creating an oscillating fix pattern where
final state is inconsistent.

Mechanism IS the OPEN_SHELL face topology: 8 ADVANCED_FACEs forming a hexagonal
prism are wired into a single OPEN_SHELL whose lateral-face normals are built
so alternate faces point inward, exposing the propagation oscillation.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh179",
    defect=(
        "OPEN_SHELL with 8 faces (hex base, top, 6 lateral) for hexagonal prism; "
        "lateral faces alternate inward/outward normals (odd-indexed lateral normals "
        "point inward), creating FixFaceOrientation propagation oscillation; "
        "inconsistent orientation IS wired into OPEN_SHELL face topology"
    ),
)

# Regular hexagon in z=0, radius=1, 6 vertices
R = 1.0
H = 1.0  # prism height

hex_xy = [(R * math.cos(math.pi / 3 * i), R * math.sin(math.pi / 3 * i)) for i in range(6)]

# Bottom ring (z=0) and top ring (z=H) vertex points
bot_pts = [f.cartesian_point((x, y, 0.0)) for x, y in hex_xy]
top_pts = [f.cartesian_point((x, y, H))   for x, y in hex_xy]

bot_vts = [f.vertex_point(p) for p in bot_pts]
top_vts = [f.vertex_point(p) for p in top_pts]

# Bottom ring edges (i -> i+1 mod 6)
def le(xa, ya, za, xb, yb, zb, pa, pb, va, vb):
    dx = xb - xa
    dy = yb - ya
    dz = zb - za
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    d   = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln  = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

bot_edges = [le(hex_xy[i][0], hex_xy[i][1], 0.0,
                hex_xy[(i+1)%6][0], hex_xy[(i+1)%6][1], 0.0,
                bot_pts[i], bot_pts[(i+1)%6], bot_vts[i], bot_vts[(i+1)%6]) for i in range(6)]
top_edges = [le(hex_xy[i][0], hex_xy[i][1], H,
                hex_xy[(i+1)%6][0], hex_xy[(i+1)%6][1], H,
                top_pts[i], top_pts[(i+1)%6], top_vts[i], top_vts[(i+1)%6]) for i in range(6)]
vert_edges = [le(hex_xy[i][0], hex_xy[i][1], 0.0,
                 hex_xy[i][0], hex_xy[i][1], H,
                 bot_pts[i], top_pts[i], bot_vts[i], top_vts[i]) for i in range(6)]

def mk_plane(px, py, pz, nx, ny, nz):
    """Plane with normal (nx,ny,nz), origin (px,py,pz); x-axis = +X or fallback."""
    if abs(nx) < 0.9:
        xd = f.direction((1.0, 0.0, 0.0))
    else:
        xd = f.direction((0.0, 1.0, 0.0))
    orig = f.cartesian_point((px, py, pz))
    nd   = f.direction((nx, ny, nz))
    return f.plane(f.axis2_placement_3d(orig, nd, xd))

# Bottom face: normal -Z (outward from hex prism looking down)
bot_loop = f.edge_loop([f.oriented_edge(bot_edges[i], True) for i in range(6)])
bot_plane = mk_plane(0.0, 0.0, 0.0, 0.0, 0.0, -1.0)
f_bot = f.advanced_face([f.face_outer_bound(bot_loop)], bot_plane)

# Top face: normal +Z
top_loop = f.edge_loop([f.oriented_edge(top_edges[i], True) for i in range(6)])
top_plane = mk_plane(0.0, 0.0, H, 0.0, 0.0, 1.0)
f_top = f.advanced_face([f.face_outer_bound(top_loop)], top_plane)

# 6 lateral faces — alternate faces have FLIPPED normals (pointing inward)
# to create the FixFaceOrientation propagation oscillation.
lateral_faces = []
for i in range(6):
    j = (i + 1) % 6
    # Mid-edge normal: outward direction for this panel
    mx = (hex_xy[i][0] + hex_xy[j][0]) / 2.0
    my = (hex_xy[i][1] + hex_xy[j][1]) / 2.0
    nm = math.sqrt(mx*mx + my*my)
    nx_, ny_ = mx/nm, my/nm

    # DEFECT: odd-indexed lateral faces have INVERTED normals
    if i % 2 == 1:
        nx_, ny_ = -nx_, -ny_

    lateral_plane = mk_plane(mx, my, H/2.0, nx_, ny_, 0.0)

    # Loop: bottom edge (fwd), right vertical (fwd), top edge (rev), left vertical (rev)
    lat_loop = f.edge_loop([
        f.oriented_edge(bot_edges[i],  True),
        f.oriented_edge(vert_edges[j], True),
        f.oriented_edge(top_edges[i],  False),
        f.oriented_edge(vert_edges[i], False),
    ])
    lateral_faces.append(f.advanced_face([f.face_outer_bound(lat_loop)], lateral_plane))

all_faces = [f_bot, f_top] + lateral_faces
shell = f.open_shell(all_faces, name="tsh179_hex_prism")
sbsm  = f.shell_based_surface_model([shell], name="tsh179_oscillating_orient")
f.add_product_chain(sbsm, mode="surface_shape")
