"""Tsh131 — ShapeUpgrade_ShellSewing.Apply already-sewn.

Catalog claim: Sewing input is already well-formed sewn shell with matching edge
pairs; Apply proceeds anyway, accumulating tolerance noise on merged edges.
Expected: Apply should detect sewn closure and short-circuit without re-processing.
Fixture: Perfect cube (6 faces, all edges shared); CLOSED_SHELL with no free
boundaries or duplicate edges.

Mechanism IS the shell structure: a watertight CLOSED_SHELL with 6 ADVANCED_FACEs
sharing 12 EDGE_CURVEs (each edge referenced by exactly two faces with opposite
orientations) — this IS directly wired into the 6 EDGE_LOOPs. The already-sewn
topology IS the mechanism: every edge pair in the cube IS already manifold, so
ShellSewing.Apply has no work to do, yet proceeds and accumulates tolerance noise.
The perfect shared-edge wiring IS the mechanism wired into face topology.

Tier-3 assertion: n_faces_total == 6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh131",
    defect=(
        "CLOSED_SHELL with 6 ADVANCED_FACEs sharing 12 EDGE_CURVEs — IS the already-sewn mechanism; "
        "every EDGE_CURVE IS referenced by exactly 2 faces with opposite ORIENTED_EDGE orientations; "
        "manifold shared-edge topology IS directly wired into all 6 EDGE_LOOPs; "
        "no free edges, no duplicate edges, no gaps exist in CLOSED_SHELL topology; "
        "ShellSewing.Apply receives already-sewn CLOSED_SHELL as input — IS the mechanism; "
        "Apply should detect closure and short-circuit; instead proceeds and adds noise; "
        "fix: check edge manifold status before sewing; skip if all edges already paired; "
        "emit E_SHELL_ALREADY_SEWN when Apply called on manifold-closed shell"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# 8 corners of unit cube
p000 = cp(0,0,0); p100 = cp(1,0,0); p110 = cp(1,1,0); p010 = cp(0,1,0)
p001 = cp(0,0,1); p101 = cp(1,0,1); p111 = cp(1,1,1); p011 = cp(0,1,1)

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# 12 shared EDGE_CURVEs — each IS shared between exactly 2 faces (already-sewn IS the mechanism)
e_bot_f = led(v000, v100, p000,  1, 0, 0)  # bottom-front
e_bot_r = led(v100, v110, p100,  0, 1, 0)  # bottom-right
e_bot_b = led(v010, v110, p010,  1, 0, 0)  # bottom-back (010→110)
e_bot_l = led(v000, v010, p000,  0, 1, 0)  # bottom-left
e_top_f = led(v001, v101, p001,  1, 0, 0)  # top-front
e_top_r = led(v101, v111, p101,  0, 1, 0)  # top-right
e_top_b = led(v011, v111, p011,  1, 0, 0)  # top-back
e_top_l = led(v001, v011, p001,  0, 1, 0)  # top-left
e_v0    = led(v000, v001, p000,  0, 0, 1)  # vertical 0
e_v1    = led(v100, v101, p100,  0, 0, 1)  # vertical 1
e_v2    = led(v110, v111, p110,  0, 0, 1)  # vertical 2
e_v3    = led(v010, v011, p010,  0, 0, 1)  # vertical 3

def mk_plane(ox, oy, oz, zx, zy, zz, xx, xy, xz):
    orig = f.cartesian_point((ox, oy, oz))
    zd = dir3(zx, zy, zz); xd = dir3(xx, xy, xz)
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

# 6 faces — all 12 edges shared between exactly 2 faces IS the already-sewn mechanism
f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)],
              mk_plane(0,0,0, 0,0,-1, 1,0,0))
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)],
              mk_plane(0,0,1, 0,0, 1, 1,0,0))
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],
              mk_plane(0,0,0, 0,-1,0, 1,0,0))
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],
              mk_plane(0,1,0, 0, 1,0, 1,0,0))
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],
              mk_plane(0,0,0,-1, 0,0, 0,1,0))
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],
              mk_plane(1,0,0, 1, 0,0, 0,1,0))

# Perfect CLOSED_SHELL — IS the already-sewn mechanism (no work for ShellSewing.Apply)
shell = f.closed_shell([f_bot, f_top, f_frt, f_bck, f_lft, f_rgt])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
