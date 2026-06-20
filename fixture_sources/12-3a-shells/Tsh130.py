"""Tsh130 — ShapeAnalysis_Shell.CheckOrientedShells closed-shell-with-free-edges.

Catalog claim: CLOSED_SHELL entity marker claims closure, but topology has free
edges (5 cube faces; one missing = free boundary). Expected: CheckOrientedShells
should validate that CLOSED marker matches actual topological closure. Cube
topology missing one face (right face omitted); CLOSED_SHELL claims closure with
5 faces only.

Mechanism IS the shell structure: a CLOSED_SHELL entity wraps 5 ADVANCED_FACEs
(bottom, top, front, back, left) of a unit cube — the right face IS intentionally
absent. The 4 vertical edges on the right side of the cube are therefore free
edges (referenced by only one face each) — this IS directly wired into the 5
EDGE_LOOPs. CLOSED_SHELL IS the entity type used despite free edges existing,
because the schema entity name IS the mechanism. CheckOrientedShells must detect
that the CLOSED_SHELL marker does not match the actual topology (4 free edges).

Tier-3 assertion: n_faces_total == 5

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh130",
    defect=(
        "CLOSED_SHELL wraps 5 ADVANCED_FACEs of unit cube with right face missing — IS the mechanism; "
        "bottom face, top face, front face, back face, left face ARE wired into CLOSED_SHELL; "
        "right face (x=1) IS intentionally absent — 4 edges on right rim are free; "
        "free edges ARE wired into the 5 EDGE_LOOPs as single-face-referenced edges; "
        "CLOSED_SHELL entity type IS used despite 4 free edges existing in topology; "
        "CheckOrientedShells reads CLOSED_SHELL marker; does not verify topological closure; "
        "mismatch between CLOSED_SHELL claim and free-edge topology IS the defect; "
        "fix: verify all edges referenced by exactly 2 faces before accepting CLOSED_SHELL; "
        "emit E_CLOSED_SHELL_HAS_FREE_EDGES when free edges detected in CLOSED_SHELL"
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

# 12 edges — 4 right-rim edges (e_v1, e_v2, e_top_r, e_bot_r) will be free
e_bot_f = led(v000, v100, p000,  1, 0, 0)  # bottom-front
e_bot_b = led(v010, v110, p010,  1, 0, 0)  # bottom-back (010→110)
e_bot_l = led(v000, v010, p000,  0, 1, 0)  # bottom-left
e_bot_r = led(v100, v110, p100,  0, 1, 0)  # bottom-right (FREE — only bot+right face use it, right absent)
e_top_f = led(v001, v101, p001,  1, 0, 0)  # top-front
e_top_b = led(v011, v111, p011,  1, 0, 0)  # top-back
e_top_l = led(v001, v011, p001,  0, 1, 0)  # top-left
e_top_r = led(v101, v111, p101,  0, 1, 0)  # top-right (FREE)
e_v0    = led(v000, v001, p000,  0, 0, 1)  # vertical left-front
e_v1    = led(v100, v101, p100,  0, 0, 1)  # vertical right-front (FREE)
e_v2    = led(v110, v111, p110,  0, 0, 1)  # vertical right-back (FREE)
e_v3    = led(v010, v011, p010,  0, 0, 1)  # vertical left-back

def mk_plane(ox, oy, oz, zx, zy, zz, xx, xy, xz):
    orig = f.cartesian_point((ox, oy, oz))
    zd = dir3(zx, zy, zz); xd = dir3(xx, xy, xz)
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

# Bottom z=0, normal (0,0,-1)
f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)],
              mk_plane(0,0,0, 0,0,-1, 1,0,0))

# Top z=1, normal (0,0,1)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)],
              mk_plane(0,0,1, 0,0, 1, 1,0,0))

# Front y=0, normal (0,-1,0)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],
              mk_plane(0,0,0, 0,-1,0, 1,0,0))

# Back y=1, normal (0,1,0)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],
              mk_plane(0,1,0, 0, 1,0, 1,0,0))

# Left x=0, normal (-1,0,0)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],
              mk_plane(0,0,0,-1, 0,0, 0,1,0))

# Right face (x=1) IS intentionally ABSENT — e_bot_r, e_top_r, e_v1, e_v2 are free edges

# CLOSED_SHELL with only 5 faces — IS the mechanism (free edges contradict CLOSED claim)
shell = f.closed_shell([f_bot, f_top, f_frt, f_bck, f_lft])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
