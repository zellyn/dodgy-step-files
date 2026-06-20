"""Bo022 — Shell is internally disconnected (two face groups never share an edge).

Catalog claim: A CLOSED_SHELL (or OPEN_SHELL) lists faces in two disconnected
components; there is no chain of shared edges connecting them. The "shell" is
really two shells stuffed into one wrapper.

Mechanism IS the CLOSED_SHELL face-list topology: twelve ADVANCED_FACEs from
two disjoint unit-cube vertex sets (cubeA at origin, cubeB offset by 10 units)
are listed together in a single CLOSED_SHELL. The two groups share no edge
and no vertex — the disconnection IS wired into the shell's cfs_faces list.
OCCT splits on load or reports a disconnected shell.

Tier-3 assertions: face[0].surface_type == "plane", face[1].surface_type == "plane"
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo022",
    defect=(
        "CLOSED_SHELL cfs_faces contains 12 ADVANCED_FACEs from two disjoint "
        "unit-cube vertex sets (cubeA at origin, cubeB at x+10); no shared edge "
        "between them IS wired into shell face-list — two disconnected components "
        "in one shell wrapper; OCCT splits or flags DisconnectedShell"
    ),
)

# ── helper: build 6 ADVANCED_FACEs for an axis-aligned box ───────────────────
def make_box_faces(ox, oy, oz, sx, sy, sz):
    """Return a list of 6 ADVANCED_FACEs for a box; no CLOSED_SHELL wrapper."""
    pts = [
        f.cartesian_point((ox,    oy,    oz   )),  # 0 BLL
        f.cartesian_point((ox+sx, oy,    oz   )),  # 1 BRL
        f.cartesian_point((ox+sx, oy+sy, oz   )),  # 2 BRR
        f.cartesian_point((ox,    oy+sy, oz   )),  # 3 BLR
        f.cartesian_point((ox,    oy,    oz+sz)),  # 4 TLL
        f.cartesian_point((ox+sx, oy,    oz+sz)),  # 5 TRL
        f.cartesian_point((ox+sx, oy+sy, oz+sz)),  # 6 TRR
        f.cartesian_point((ox,    oy+sy, oz+sz)),  # 7 TLR
    ]
    vts = [f.vertex_point(p) for p in pts]

    def le(ia, ib, dx, dy, dz, length):
        d = f.direction((dx, dy, dz)); v = f.vector(d, length)
        return f.edge_curve(vts[ia], vts[ib], f.line(pts[ia], v))

    e_bot_f = le(0, 1,  1, 0, 0, sx)
    e_bot_r = le(1, 2,  0, 1, 0, sy)
    e_bot_b = le(3, 2,  1, 0, 0, sx)
    e_bot_l = le(0, 3,  0, 1, 0, sy)
    e_top_f = le(4, 5,  1, 0, 0, sx)
    e_top_r = le(5, 6,  0, 1, 0, sy)
    e_top_b = le(7, 6,  1, 0, 0, sx)
    e_top_l = le(4, 7,  0, 1, 0, sy)
    e_v0    = le(0, 4,  0, 0, 1, sz)
    e_v1    = le(1, 5,  0, 0, 1, sz)
    e_v2    = le(2, 6,  0, 0, 1, sz)
    e_v3    = le(3, 7,  0, 0, 1, sz)

    def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
        orig2 = f.cartesian_point((px, py, pz))
        zd = f.direction((zx, zy, zz)); xd = f.direction((xx, xy, xz))
        return f.plane(f.axis2_placement_3d(orig2, zd, xd))

    def face4(edges_with_ori, plane):
        loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
        return f.advanced_face([f.face_outer_bound(loop)], plane)

    pl_bot = mk_plane(ox,    oy,    oz,    0, 0,-1, 1, 0, 0)
    pl_top = mk_plane(ox,    oy,    oz+sz, 0, 0, 1, 1, 0, 0)
    pl_frt = mk_plane(ox,    oy,    oz,    0,-1, 0, 1, 0, 0)
    pl_bck = mk_plane(ox,    oy+sy, oz,    0, 1, 0, 1, 0, 0)
    pl_lft = mk_plane(ox,    oy,    oz,   -1, 0, 0, 0, 1, 0)
    pl_rgt = mk_plane(ox+sx, oy,    oz,    1, 0, 0, 0, 1, 0)

    f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
    f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
    f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)], pl_frt)
    f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)], pl_bck)
    f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)], pl_lft)
    f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)], pl_rgt)

    return [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]

# ── CATALOG MECHANISM: two disjoint cubes in one CLOSED_SHELL ─────────────────
# CubeA: unit cube at origin; CubeB: unit cube offset 10 units in X.
# No vertex or edge is shared between the two groups.
faces_a = make_box_faces(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)   # 6 faces, disjoint
faces_b = make_box_faces(10.0, 0.0, 0.0, 1.0, 1.0, 1.0)  # 6 faces, disjoint

all_faces = faces_a + faces_b  # 12 faces total — two disconnected components
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)

# Single CLOSED_SHELL wrapping both disconnected face groups — IS the defect
shell = f._emit_raw(f"CLOSED_SHELL('bo022_disconnected',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('bo022_solid',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
