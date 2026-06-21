"""Pf022 — Non-deterministic empty-export from in-memory state leakage.

Catalog claim: after import-then-partial-clear, the writer emits "No suitable
CAD data found" non-deterministically; depends on past actions, not on whether
the document currently contains shapes. The fixture provides a multi-shape file
so that selective gmsh.model.remove() calls leave varying mixes of
populated/cleared state across runs.

Tier-3: load == "ok", n_edges_total >= 1, n_vertices_total >= 2, brepcheck.valid == True
Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf022",
    defect=(
        "Non-deterministic empty-export from in-memory state leakage; "
        "writer state must be a pure function of input; normalize global state per call; "
        "gmsh: import STEP, model.remove() some entities, then write — emits 'No suitable "
        "CAD data found' non-deterministically depending on past actions; "
        "OCCT Draw: stepread populates transient model reused by next stepwrite, doubling output; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

# Build a simple unit cube as the round-trip target shape
pts = [
    f.cartesian_point((0.0, 0.0, 0.0)),  # 0
    f.cartesian_point((1.0, 0.0, 0.0)),  # 1
    f.cartesian_point((1.0, 1.0, 0.0)),  # 2
    f.cartesian_point((0.0, 1.0, 0.0)),  # 3
    f.cartesian_point((0.0, 0.0, 1.0)),  # 4
    f.cartesian_point((1.0, 0.0, 1.0)),  # 5
    f.cartesian_point((1.0, 1.0, 1.0)),  # 6
    f.cartesian_point((0.0, 1.0, 1.0)),  # 7
]
vts = [f.vertex_point(p) for p in pts]


def le(ia, ib, dx, dy, dz, length):
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pts[ia], v)
    return f.edge_curve(vts[ia], vts[ib], ln)


e_bot_f = le(0, 1,  1, 0, 0, 1.0)
e_bot_r = le(1, 2,  0, 1, 0, 1.0)
e_bot_b = le(3, 2,  1, 0, 0, 1.0)
e_bot_l = le(0, 3,  0, 1, 0, 1.0)
e_top_f = le(4, 5,  1, 0, 0, 1.0)
e_top_r = le(5, 6,  0, 1, 0, 1.0)
e_top_b = le(7, 6,  1, 0, 0, 1.0)
e_top_l = le(4, 7,  0, 1, 0, 1.0)
e_v0    = le(0, 4,  0, 0, 1, 1.0)
e_v1    = le(1, 5,  0, 0, 1, 1.0)
e_v2    = le(2, 6,  0, 0, 1, 1.0)
e_v3    = le(3, 7,  0, 0, 1, 1.0)


def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((zx, zy, zz))
    xd   = f.direction((xx, xy, xz))
    return f.plane(f.axis2_placement_3d(orig, zd, xd))


def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    fob  = f.face_outer_bound(loop)
    return f.advanced_face([fob], plane)


pl_bot = mk_plane(0, 0, 0,  0, 0,-1,  1, 0, 0)
pl_top = mk_plane(0, 0, 1,  0, 0, 1,  1, 0, 0)
pl_frt = mk_plane(0, 0, 0,  0,-1, 0,  1, 0, 0)
pl_bck = mk_plane(0, 1, 0,  0, 1, 0,  1, 0, 0)
pl_lft = mk_plane(0, 0, 0, -1, 0, 0,  0, 1, 0)
pl_rgt = mk_plane(1, 0, 0,  1, 0, 0,  0, 1, 0)

f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

all_faces = [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pf022_roundtrip_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pf022_roundtrip_solid',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
