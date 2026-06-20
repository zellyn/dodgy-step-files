"""Tsh160 — ShapeAnalysis_Shell.CheckOrientedShells inverted-trace.

Catalog claim: A shell where all faces are consistently inverted (inward-facing normals)
forms a topologically valid cycle but has globally reversed orientation. Implicit
orientation trace yields a closed loop but travels the "inside-out" direction.

Mechanism IS the shell structure: UNIT CUBE — SIX ADVANCED_FACEs all wired with
same_sense=.F. (inverted) into a CLOSED_SHELL. Every shared edge IS consistently
oriented so that face adjacency IS topologically valid (no free edges, consistent
winding locally). The global inversion IS wired into ALL six faces simultaneously
by setting same_sense=False on each. CheckOrientedShells traces orientation and
finds a consistent cycle (no relative inconsistency) but the absolute orientation
is inside-out; the defect is whether the algorithm detects absolute vs. relative
inversion.

Tier-3 assertion: n_faces_total == 6

live oracle: occt=shape(1)/shape(1) gmsh=shape(26)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh160",
    defect=(
        "SIX ADVANCED_FACEs forming unit cube in CLOSED_SHELL, all same_sense=.F. — "
        "IS the inverted-trace mechanism; "
        "Bottom face (z=0) IS wired with same_sense=.F. — normal points inward (+z); "
        "Top face (z=1) IS wired with same_sense=.F. — normal points inward (-z); "
        "Front face (y=0) IS wired with same_sense=.F. — normal points inward (+y); "
        "Back face (y=1) IS wired with same_sense=.F. — normal points inward (-y); "
        "Left face (x=0) IS wired with same_sense=.F. — normal points inward (+x); "
        "Right face (x=1) IS wired with same_sense=.F. — normal points inward (-x); "
        "shared edges between all 6 faces ARE consistently oriented — no free edges; "
        "global inversion IS wired as same_sense=False on every face — IS the mechanism; "
        "CheckOrientedShells traces orientation and finds locally consistent cycle; "
        "absolute inside-out inversion is NOT detected by relative consistency check; "
        "fix: compute outward normal direction from solid centroid; detect globally inverted shells; "
        "emit E_CHECK_ORIENTED_GLOBALLY_INVERTED when all face normals point inward"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit cube vertices
p000 = cp(0,0,0); p100 = cp(1,0,0); p110 = cp(1,1,0); p010 = cp(0,1,0)
p001 = cp(0,0,1); p101 = cp(1,0,1); p111 = cp(1,1,1); p011 = cp(0,1,1)

v000=f.vertex_point(p000); v100=f.vertex_point(p100)
v110=f.vertex_point(p110); v010=f.vertex_point(p010)
v001=f.vertex_point(p001); v101=f.vertex_point(p101)
v111=f.vertex_point(p111); v011=f.vertex_point(p011)

# Bottom face edges (z=0): 000-100-110-010
e_b0 = led(v000, v100, p000,  1, 0, 0)
e_b1 = led(v100, v110, p100,  0, 1, 0)
e_b2 = led(v010, v110, p010,  1, 0, 0)
e_b3 = led(v000, v010, p000,  0, 1, 0)

# Top face edges (z=1): 001-101-111-011
e_t0 = led(v001, v101, p001,  1, 0, 0)
e_t1 = led(v101, v111, p101,  0, 1, 0)
e_t2 = led(v011, v111, p011,  1, 0, 0)
e_t3 = led(v001, v011, p001,  0, 1, 0)

# Vertical edges (z direction)
e_v0 = led(v000, v001, p000,  0, 0, 1)
e_v1 = led(v100, v101, p100,  0, 0, 1)
e_v2 = led(v110, v111, p110,  0, 0, 1)
e_v3 = led(v010, v011, p010,  0, 0, 1)

# Bottom face (z=0): plane normal points +z, same_sense=.F. → effective normal -z (inward)
plane_bot = f.plane(f.axis2_placement_3d(p000, dir3(0,0,1), dir3(1,0,0)))
loop_bot = f.edge_loop([
    f.oriented_edge(e_b0, True),
    f.oriented_edge(e_b1, True),
    f.oriented_edge(e_b2, False),
    f.oriented_edge(e_b3, False),
])
face_bot = f.advanced_face([f.face_outer_bound(loop_bot, orientation=True)], plane_bot, same_sense=False)

# Top face (z=1): plane normal points -z, same_sense=.F. → effective normal +z (inward)
plane_top = f.plane(f.axis2_placement_3d(p001, dir3(0,0,-1), dir3(1,0,0)))
loop_top = f.edge_loop([
    f.oriented_edge(e_t0, True),
    f.oriented_edge(e_t1, True),
    f.oriented_edge(e_t2, False),
    f.oriented_edge(e_t3, False),
])
face_top = f.advanced_face([f.face_outer_bound(loop_top, orientation=True)], plane_top, same_sense=False)

# Front face (y=0): plane normal points -y, same_sense=.F. → effective normal +y (inward)
plane_frt = f.plane(f.axis2_placement_3d(p000, dir3(0,-1,0), dir3(1,0,0)))
loop_frt = f.edge_loop([
    f.oriented_edge(e_b0, True),
    f.oriented_edge(e_v1, True),
    f.oriented_edge(e_t0, False),
    f.oriented_edge(e_v0, False),
])
face_frt = f.advanced_face([f.face_outer_bound(loop_frt, orientation=True)], plane_frt, same_sense=False)

# Back face (y=1): plane normal points +y, same_sense=.F. → effective normal -y (inward)
plane_bck = f.plane(f.axis2_placement_3d(p010, dir3(0,1,0), dir3(1,0,0)))
loop_bck = f.edge_loop([
    f.oriented_edge(e_b2, True),
    f.oriented_edge(e_v2, True),
    f.oriented_edge(e_t2, False),
    f.oriented_edge(e_v3, False),
])
face_bck = f.advanced_face([f.face_outer_bound(loop_bck, orientation=True)], plane_bck, same_sense=False)

# Left face (x=0): plane normal points -x, same_sense=.F. → effective normal +x (inward)
plane_lft = f.plane(f.axis2_placement_3d(p000, dir3(-1,0,0), dir3(0,1,0)))
loop_lft = f.edge_loop([
    f.oriented_edge(e_b3, True),
    f.oriented_edge(e_v3, True),
    f.oriented_edge(e_t3, False),
    f.oriented_edge(e_v0, False),
])
face_lft = f.advanced_face([f.face_outer_bound(loop_lft, orientation=True)], plane_lft, same_sense=False)

# Right face (x=1): plane normal points +x, same_sense=.F. → effective normal -x (inward)
plane_rgt = f.plane(f.axis2_placement_3d(p100, dir3(1,0,0), dir3(0,1,0)))
loop_rgt = f.edge_loop([
    f.oriented_edge(e_b1, True),
    f.oriented_edge(e_v2, True),
    f.oriented_edge(e_t1, False),
    f.oriented_edge(e_v1, False),
])
face_rgt = f.advanced_face([f.face_outer_bound(loop_rgt, orientation=True)], plane_rgt, same_sense=False)

# CLOSED_SHELL: 6 faces all same_sense=.F. — consistent locally, globally inverted IS the mechanism
shell = f.closed_shell([face_bot, face_top, face_frt, face_bck, face_lft, face_rgt])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
