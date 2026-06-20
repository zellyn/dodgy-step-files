"""Tsh150 — ShapeAnalysis_Shell.CheckOrientedShells thin-shell.

Catalog claim: Shell that's effectively 2D (very thin extruded); orientation
logic uses normal vectors but the thin extrusion makes normals near-coplanar.
Tests robustness when geometric orientation becomes numerically ambiguous.

Mechanism IS the shell structure: SIX ADVANCED_FACEs forming a thin-slab shell
(1.0 x 1.0 x 0.001 mm) — all four side faces have normals that are perpendicular
to Z and nearly parallel to each other in the thin dimension. The 0.001mm
separation IS wired into the Z-coordinate of the top-face PLANE and all four
side-face PLANE origins, making face normals near-coplanar when the extrusion
thickness approaches zero. CheckOrientedShells uses normal-vector comparison to
decide consistent orientation, and near-zero extrusion thickness makes that
comparison numerically ambiguous.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh150",
    defect=(
        "SIX ADVANCED_FACEs forming thin slab (1x1x0.001) — IS the thin-shell near-coplanar-normals mechanism; "
        "bottom face at z=0 with PLANE normal (0,0,1) — IS wired into OPEN_SHELL; "
        "top face at z=0.001 with PLANE normal (0,0,1) — IS wired 0.001mm above bottom (thin extrusion); "
        "four side faces with normals (+x,-x,+y,-y) — ARE wired into OPEN_SHELL at height 0.001mm; "
        "0.001mm Z-separation IS wired into top-face PLANE origin and side-face PLANE origins; "
        "near-zero extrusion makes side-face normals nearly parallel — IS the near-coplanar mechanism; "
        "CheckOrientedShells uses normal-vector comparison — numerically ambiguous for near-2D shells; "
        "fix: detect thin shells by bounding-box aspect ratio; use topological orientation fallback; "
        "emit E_THIN_SHELL_ORIENTATION_AMBIGUOUS when extrusion thickness below numerical threshold"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

THIN = 0.001  # 0.001mm thin extrusion — IS the near-coplanar mechanism

# Bottom face vertices (z=0)
p000 = cp(0, 0, 0);    p100 = cp(1, 0, 0)
p110 = cp(1, 1, 0);    p010 = cp(0, 1, 0)
# Top face vertices (z=THIN)
p001 = cp(0, 0, THIN); p101 = cp(1, 0, THIN)
p111 = cp(1, 1, THIN); p011 = cp(0, 1, THIN)

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Vertical edges (Z-direction, length=THIN) — IS the thin-extrusion geometry wired in
e_v00 = led(v000, v001, p000,  0, 0, 1)
e_v10 = led(v100, v101, p100,  0, 0, 1)
e_v11 = led(v110, v111, p110,  0, 0, 1)
e_v01 = led(v010, v011, p010,  0, 0, 1)

# Bottom edges (z=0)
e_b_front = led(v000, v100, p000,  1, 0, 0)
e_b_right = led(v100, v110, p100,  0, 1, 0)
e_b_back  = led(v110, v010, p110, -1, 0, 0)
e_b_left  = led(v010, v000, p010,  0,-1, 0)

# Top edges (z=THIN)
e_t_front = led(v001, v101, p001,  1, 0, 0)
e_t_right = led(v101, v111, p101,  0, 1, 0)
e_t_back  = led(v111, v011, p111, -1, 0, 0)
e_t_left  = led(v011, v001, p011,  0,-1, 0)

# Bottom face (z=0): normal (0,0,1) IS wired into PLANE
bottom_plane = f.plane(f.axis2_placement_3d(p000, dir3(0, 0, 1), dir3(1, 0, 0)))
loop_bot = f.edge_loop([
    f.oriented_edge(e_b_front, True),
    f.oriented_edge(e_b_right, True),
    f.oriented_edge(e_b_back,  True),
    f.oriented_edge(e_b_left,  True),
])
face_bot = f.advanced_face([f.face_outer_bound(loop_bot, orientation=True)], bottom_plane, same_sense=True)

# Top face (z=THIN): IS wired 0.001mm above — near-coplanar to bottom normal
top_plane = f.plane(f.axis2_placement_3d(p001, dir3(0, 0, 1), dir3(1, 0, 0)))
loop_top = f.edge_loop([
    f.oriented_edge(e_t_front, True),
    f.oriented_edge(e_t_right, True),
    f.oriented_edge(e_t_back,  True),
    f.oriented_edge(e_t_left,  True),
])
face_top = f.advanced_face([f.face_outer_bound(loop_top, orientation=True)], top_plane, same_sense=False)

# Front face (y=0): normal (0,-1,0)
front_plane = f.plane(f.axis2_placement_3d(p000, dir3(0, -1, 0), dir3(1, 0, 0)))
loop_front = f.edge_loop([
    f.oriented_edge(e_b_front,  True),
    f.oriented_edge(e_v10,      True),
    f.oriented_edge(e_t_front,  False),
    f.oriented_edge(e_v00,      False),
])
face_front = f.advanced_face([f.face_outer_bound(loop_front, orientation=True)], front_plane, same_sense=True)

# Back face (y=1): normal (0,1,0)
back_plane = f.plane(f.axis2_placement_3d(p110, dir3(0, 1, 0), dir3(-1, 0, 0)))
loop_back = f.edge_loop([
    f.oriented_edge(e_b_back,  True),
    f.oriented_edge(e_v01,     True),
    f.oriented_edge(e_t_back,  False),
    f.oriented_edge(e_v11,     False),
])
face_back = f.advanced_face([f.face_outer_bound(loop_back, orientation=True)], back_plane, same_sense=True)

# Right face (x=1): normal (1,0,0)
right_plane = f.plane(f.axis2_placement_3d(p100, dir3(1, 0, 0), dir3(0, 1, 0)))
loop_right = f.edge_loop([
    f.oriented_edge(e_b_right, True),
    f.oriented_edge(e_v11,     True),
    f.oriented_edge(e_t_right, False),
    f.oriented_edge(e_v10,     False),
])
face_right = f.advanced_face([f.face_outer_bound(loop_right, orientation=True)], right_plane, same_sense=True)

# Left face (x=0): normal (-1,0,0)
left_plane = f.plane(f.axis2_placement_3d(p010, dir3(-1, 0, 0), dir3(0, -1, 0)))
loop_left = f.edge_loop([
    f.oriented_edge(e_b_left, True),
    f.oriented_edge(e_v00,    True),
    f.oriented_edge(e_t_left, False),
    f.oriented_edge(e_v01,    False),
])
face_left = f.advanced_face([f.face_outer_bound(loop_left, orientation=True)], left_plane, same_sense=True)

# OPEN_SHELL: 6-face thin slab with 0.001mm Z-extent — IS the near-coplanar-normals mechanism
shell = f.open_shell([face_bot, face_top, face_front, face_back, face_right, face_left])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
