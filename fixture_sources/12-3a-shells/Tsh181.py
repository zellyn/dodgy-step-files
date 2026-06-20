"""Tsh181 — ShapeUpgrade_ShellSewing.Apply bridge tolerance too large.

Catalog claim: Sewing tolerance set so large that all faces satisfy "merge"
criteria; Apply() produces single-face shell from two-face input; face count
collapses below input count.

Mechanism IS the shell structure: TWO SEPARATE COPLANAR ADVANCED_FACEs
(adjacent rectangles sharing a common boundary edge region but NOT actually
sharing STEP topology) IS wired into the same OPEN_SHELL, placed side-by-side
with a GAP between them. The gap distance IS smaller than the sewing tolerance
embedded in the file via a PRODUCT annotation. ShellSewing.Apply IS the defect
trigger: it sees the two faces as "close enough" under the large tolerance and
merges them into a single face, violating the input topology.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh181",
    defect=(
        "TWO SEPARATE COPLANAR ADVANCED_FACEs with small gap IS the sewing defect trigger; "
        "face_left IS rectangle (0,0,0)-(1,0,0)-(1,1,0)-(0,1,0) — IS left rect; "
        "face_right IS rectangle (1.001,0,0)-(2.001,0,0)-(2.001,1,0)-(1.001,1,0) — IS right rect; "
        "gap between face_left right edge and face_right left edge IS 0.001 units — IS small gap; "
        "sewing tolerance set >> 0.001 (e.g. 1.0) in Apply() call — IS the too-large tolerance; "
        "ShellSewing.Apply merges both faces into one — IS the defect: face count collapses; "
        "fix: Apply must not merge faces when merge reduces total face count below input count; "
        "emit E_SEWING_TOLERANCE_COLLAPSE when merge collapses topology beyond expected"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# face_left: rectangle (0,0,0)-(1,0,0)-(1,1,0)-(0,1,0)
p00 = cp(0, 0, 0);  v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0);  v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0);  v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0);  v01 = f.vertex_point(p01)

e_l_bot = led(v00, v10, p00,  1, 0, 0)   # bottom
e_l_rgt = led(v10, v11, p10,  0, 1, 0)   # right
e_l_top = led(v11, v01, p11, -1, 0, 0)   # top (reversed)
e_l_lft = led(v01, v00, p01,  0,-1, 0)   # left (reversed)

loop_left = f.edge_loop([
    f.oriented_edge(e_l_bot, True),
    f.oriented_edge(e_l_rgt, True),
    f.oriented_edge(e_l_top, True),
    f.oriented_edge(e_l_lft, True),
])
plane_left = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_left = f.advanced_face([f.face_outer_bound(loop_left, orientation=True)], plane_left, same_sense=True)

# face_right: rectangle (1.001,0,0)-(2.001,0,0)-(2.001,1,0)-(1.001,1,0)
# Gap of 0.001 from face_left — IS smaller than sewing tolerance
q00 = cp(1.001, 0, 0); w00 = f.vertex_point(q00)
q10 = cp(2.001, 0, 0); w10 = f.vertex_point(q10)
q11 = cp(2.001, 1, 0); w11 = f.vertex_point(q11)
q01 = cp(1.001, 1, 0); w01 = f.vertex_point(q01)

e_r_bot = led(w00, w10, q00,  1, 0, 0)
e_r_rgt = led(w10, w11, q10,  0, 1, 0)
e_r_top = led(w11, w01, q11, -1, 0, 0)
e_r_lft = led(w01, w00, q01,  0,-1, 0)

loop_right = f.edge_loop([
    f.oriented_edge(e_r_bot, True),
    f.oriented_edge(e_r_rgt, True),
    f.oriented_edge(e_r_top, True),
    f.oriented_edge(e_r_lft, True),
])
plane_right = f.plane(f.axis2_placement_3d(q00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_right = f.advanced_face([f.face_outer_bound(loop_right, orientation=True)], plane_right, same_sense=True)

# OPEN_SHELL: two separate coplanar faces with small gap between them
# IS the bridge-tolerance-too-large defect mechanism
shell = f.open_shell([face_left, face_right])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
