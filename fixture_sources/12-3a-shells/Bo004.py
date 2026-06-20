"""Bo004 — Closed shell encloses an unrepresented cavity (genus mismatch).

Catalog claim: The outer CLOSED_SHELL of a MANIFOLD_SOLID_BREP has topological
genus ≥ 1 (bounds an interior cavity) yet no BREP_WITH_VOIDS wrapper is present.
The "EnclosedRegion" branch of BRepCheck_Solid.cxx.

Mechanism IS the shell/face topology: a hollow-box outer shell (6 outer faces +
6 inner faces forming an interior cavity) IS the CLOSED_SHELL of a plain
MANIFOLD_SOLID_BREP with no BREP_WITH_VOIDS. The cavity IS encoded in the
face structure but the wrapper is absent — genus mismatch wired into topology.

Tier-3 assertions: face[0].surface_type == "plane", face[5].surface_type == "plane"
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo004",
    defect=(
        "MANIFOLD_SOLID_BREP outer CLOSED_SHELL has 12 faces (6 outer + 6 inner "
        "cavity faces, genus ≥ 1) but no BREP_WITH_VOIDS wrapper; EnclosedRegion "
        "branch; genus mismatch IS wired into closed-shell face topology"
    ),
)

# ── helpers ───────────────────────────────────────────────────────────────────
def make_box_faces(ox, oy, oz, sx, sy, sz):
    """Return 6 ADVANCED_FACE entities forming a box (no shell yet)."""
    pts = [
        f.cartesian_point((ox,    oy,    oz   )),
        f.cartesian_point((ox+sx, oy,    oz   )),
        f.cartesian_point((ox+sx, oy+sy, oz   )),
        f.cartesian_point((ox,    oy+sy, oz   )),
        f.cartesian_point((ox,    oy,    oz+sz)),
        f.cartesian_point((ox+sx, oy,    oz+sz)),
        f.cartesian_point((ox+sx, oy+sy, oz+sz)),
        f.cartesian_point((ox,    oy+sy, oz+sz)),
    ]
    vts = [f.vertex_point(p) for p in pts]

    def le(ia, ib, dx, dy, dz, length):
        d = f.direction((dx, dy, dz)); v = f.vector(d, length)
        ln = f.line(pts[ia], v)
        return f.edge_curve(vts[ia], vts[ib], ln)

    e_bot_f = le(0,1, 1,0,0, sx); e_bot_r = le(1,2, 0,1,0, sy)
    e_bot_b = le(3,2, 1,0,0, sx); e_bot_l = le(0,3, 0,1,0, sy)
    e_top_f = le(4,5, 1,0,0, sx); e_top_r = le(5,6, 0,1,0, sy)
    e_top_b = le(7,6, 1,0,0, sx); e_top_l = le(4,7, 0,1,0, sy)
    e_v0 = le(0,4, 0,0,1, sz); e_v1 = le(1,5, 0,0,1, sz)
    e_v2 = le(2,6, 0,0,1, sz); e_v3 = le(3,7, 0,0,1, sz)

    def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
        orig = f.cartesian_point((px, py, pz))
        zd = f.direction((zx,zy,zz)); xd = f.direction((xx,xy,xz))
        return f.plane(f.axis2_placement_3d(orig, zd, xd))

    def face4(edges_with_ori, plane):
        loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
        return f.advanced_face([f.face_outer_bound(loop)], plane)

    pl_bot = mk_plane(ox,    oy,    oz,    0,0,-1, 1,0,0)
    pl_top = mk_plane(ox,    oy,    oz+sz, 0,0, 1, 1,0,0)
    pl_frt = mk_plane(ox,    oy,    oz,    0,-1,0, 1,0,0)
    pl_bck = mk_plane(ox,    oy+sy, oz,    0, 1,0, 1,0,0)
    pl_lft = mk_plane(ox,    oy,    oz,   -1,0, 0, 0,1,0)
    pl_rgt = mk_plane(ox+sx, oy,    oz,    1,0, 0, 0,1,0)

    f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
    f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
    f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)], pl_frt)
    f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)], pl_bck)
    f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)], pl_lft)
    f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)], pl_rgt)
    return [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]

# ── CATALOG MECHANISM: outer 5x5x5 faces + inner 2x2x2 cavity faces ──────────
# Both sets of faces go into ONE CLOSED_SHELL with no BREP_WITH_VOIDS wrapper.
outer_faces = make_box_faces(-2.5, -2.5, -2.5, 5.0, 5.0, 5.0)
inner_faces = make_box_faces(-1.0, -1.0, -1.0, 2.0, 2.0, 2.0)

all_faces = outer_faces + inner_faces  # 12 faces total — genus mismatch

# Single CLOSED_SHELL enclosing both surfaces (cavity unrepresented as void)
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('genus_mismatch',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('bo004_enclosed_region',#{shell.eid})")
# No BREP_WITH_VOIDS — that is the defect

f.add_product_chain(msb, mode="brep_shape")
