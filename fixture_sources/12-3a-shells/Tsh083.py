"""Tsh083 — ShapeFix_Solid.SolidFromShell open-shell-as-solid promotion
non-closure detection.

Catalog claim: Single OPEN_SHELL passed where a closed solid is required;
shell is missing one face (e.g., top), so it is not closed; fixer must detect
non-closure or refuse promotion with diagnostic.

Mechanism: A box with 5 of 6 faces (top face omitted) wrapped in an OPEN_SHELL.
OCC loads it as a shape (shape(1)); SolidFromShell should reject or report
non-closure.

Tier-3 assertion: load == "ok"

Expected validation: (not specified in catalog — loaded as shape)
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tsh083",
    defect=(
        "OPEN_SHELL containing 5 of 6 faces of a unit box (top face omitted); "
        "shell is not closed — missing one face creates an open boundary; "
        "ShapeFix_Solid.SolidFromShell must detect non-closure or refuse "
        "promotion to solid with a diagnostic; "
        "closure check must be deterministic"
    ),
)

# ── Build 5 faces of a 5x5x5 box (all except the top face) ──────────────────
ox, oy, oz = 0.0, 0.0, 0.0
sx, sy, sz = 5.0, 5.0, 5.0

pts = [
    f.cartesian_point((ox,     oy,     oz    )),  # 0 BLL
    f.cartesian_point((ox+sx,  oy,     oz    )),  # 1 BRL
    f.cartesian_point((ox+sx,  oy+sy,  oz    )),  # 2 BRR
    f.cartesian_point((ox,     oy+sy,  oz    )),  # 3 BLR
    f.cartesian_point((ox,     oy,     oz+sz )),  # 4 TLL
    f.cartesian_point((ox+sx,  oy,     oz+sz )),  # 5 TRL
    f.cartesian_point((ox+sx,  oy+sy,  oz+sz )),  # 6 TRR
    f.cartesian_point((ox,     oy+sy,  oz+sz )),  # 7 TLR
]
vs = [f.vertex_point(p) for p in pts]

def le(ia, ib, dx, dy, dz, length):
    d = f.direction((dx, dy, dz))
    v = f.vector(d, length)
    return f.edge_curve(vs[ia], vs[ib], f.line(pts[ia], v))

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

pl_bot = mk_plane(ox,    oy,    oz,     0,  0, -1, 1, 0, 0)
pl_frt = mk_plane(ox,    oy,    oz,     0, -1,  0, 1, 0, 0)
pl_bck = mk_plane(ox,    oy+sy, oz,     0,  1,  0, 1, 0, 0)
pl_lft = mk_plane(ox,    oy,    oz,    -1,  0,  0, 0, 1, 0)
pl_rgt = mk_plane(ox+sx, oy,    oz,     1,  0,  0, 0, 1, 0)

f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)], pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)], pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)], pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)], pl_rgt)

# ── 5-face OPEN_SHELL (top face omitted — creates open boundary) ─────────────
five_faces = [f_bot, f_frt, f_bck, f_lft, f_rgt]
face_refs = ",".join(f"#{fa.eid}" for fa in five_faces)
shell = f._emit_raw(f"OPEN_SHELL('tsh083_open_box',({face_refs}))")
sbsm  = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('tsh083_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3a-shells" / "Tsh083.stp")
