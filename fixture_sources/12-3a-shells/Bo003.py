"""Bo003 — Two void shells of one solid are nested inside each other.

Catalog claim: A BREP_WITH_VOIDS carries two inner void shells where one void
is fully enclosed by the other (nested cavities / imbricated shells).

Mechanism IS the BREP_WITH_VOIDS shell topology: two ORIENTED_CLOSED_SHELLs
(inner 1x1x1 cube fully inside outer 3x3x3 cube) are both listed as voids of
the same solid. The geometric nesting IS wired into the shell/face structure.

Live-verified 2026-07-16 (this worktree's OCP/OCCT 7.8.1): this fixture does
NOT fire BRepCheck_InvalidImbricationOfShells -- BRepCheck_Solid::Blind(), the
method that sets that status, is a no-op in this OCCT build. The real
imbrication check lives in BRepCheck_Solid::Minimum() and only fires
InvalidImbricationOfShells when the SAME TopoDS_Face is shared by two
different shells within one solid -- a different pattern than nested-but-
disjoint void shells. What this fixture's nested-void topology actually fires
is BRepCheck_SubshapeNotInShape, raised via Minimum()'s nested-solid IsOut()
classification path (confirmed live: BRepCheck_Analyzer(shape,
True).IsValid() == False, with exactly one status on the solid,
BRepCheck_SubshapeNotInShape). See occt-coverage/exchange/problems.json
(bc-invalid-imbrication-of-shells, bc-subshape-not-in-shape) and BACKLOG.md
Q10/Q11 for the investigation trail.

Byte-history: this fixture originally omitted the required `*` derived-
attribute placeholder on both ORIENTED_CLOSED_SHELL instances (3-arg instead
of the correct 4-arg EXPRESS form: name, *, closed_shell_element,
orientation -- cfs_faces is DERIVE'd in ORIENTED_CLOSED_SHELL, redeclared
from connected_face_set). That arity bug crashed STEPControl_Reader.
TransferRoots() (signal 11) before BRepCheck ever ran. Fixed 2026-07-16;
purely syntactic, no geometry change. Corpus-wide grep confirmed Bo003 was
the only shipped fixture with this pattern.

Tier-3 assertions: face[0].surface_type == "plane", face[5].surface_type == "plane"
Expected: occt=shape(1)/shape(1) gmsh=shape(79) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo003",
    defect=(
        "BREP_WITH_VOIDS with two ORIENTED_CLOSED_SHELL voids nested inside each "
        "other; inner 1x1x1 box fully enclosed by outer 3x3x3 box IS wired into "
        "shell/face topology; live-verified OCCT 7.8.1 fires "
        "BRepCheck_SubshapeNotInShape (nested-solid IsOut() classification in "
        "BRepCheck_Solid::Minimum), NOT InvalidImbricationOfShells -- "
        "BRepCheck_Solid::Blind() is a no-op in this build"
    ),
)

# ── helpers ───────────────────────────────────────────────────────────────────
def make_box_closed_shell(ox, oy, oz, sx, sy, sz, tag):
    """Build a watertight CLOSED_SHELL box at origin (ox,oy,oz) with size (sx,sy,sz)."""
    # 8 corners
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
        ln = f.line(pts[ia], v)
        return f.edge_curve(vts[ia], vts[ib], ln)

    # 12 edges
    e_bot_f  = le(0, 1,  1, 0, 0, sx)   # bottom-front
    e_bot_r  = le(1, 2,  0, 1, 0, sy)   # bottom-right
    e_bot_b  = le(3, 2,  1, 0, 0, sx)   # bottom-back  (3→2)
    e_bot_l  = le(0, 3,  0, 1, 0, sy)   # bottom-left  (0→3)
    e_top_f  = le(4, 5,  1, 0, 0, sx)   # top-front
    e_top_r  = le(5, 6,  0, 1, 0, sy)   # top-right
    e_top_b  = le(7, 6,  1, 0, 0, sx)   # top-back
    e_top_l  = le(4, 7,  0, 1, 0, sy)   # top-left
    e_v0     = le(0, 4,  0, 0, 1, sz)   # vert 0
    e_v1     = le(1, 5,  0, 0, 1, sz)   # vert 1
    e_v2     = le(2, 6,  0, 0, 1, sz)   # vert 2
    e_v3     = le(3, 7,  0, 0, 1, sz)   # vert 3

    def mk_plane(ox2, oy2, oz2, zx, zy, zz, xx, xy, xz):
        orig2 = f.cartesian_point((ox2, oy2, oz2))
        zd = f.direction((zx, zy, zz)); xd = f.direction((xx, xy, xz))
        plc = f.axis2_placement_3d(orig2, zd, xd)
        return f.plane(plc)

    def face4(edges_with_ori, plane):
        loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
        return f.advanced_face([f.face_outer_bound(loop)], plane)

    # 6 faces: bottom, top, front, back, left, right
    pl_bot = mk_plane(ox,    oy,    oz,    0, 0, -1, 1, 0, 0)
    pl_top = mk_plane(ox,    oy,    oz+sz, 0, 0,  1, 1, 0, 0)
    pl_frt = mk_plane(ox,    oy,    oz,    0,-1,  0, 1, 0, 0)
    pl_bck = mk_plane(ox,    oy+sy, oz,    0, 1,  0, 1, 0, 0)
    pl_lft = mk_plane(ox,    oy,    oz,   -1, 0,  0, 0, 1, 0)
    pl_rgt = mk_plane(ox+sx, oy,    oz,    1, 0,  0, 0, 1, 0)

    f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
    f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
    f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)], pl_frt)
    f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)], pl_bck)
    f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)], pl_lft)
    f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)], pl_rgt)

    return f.closed_shell([f_bot, f_top, f_frt, f_bck, f_lft, f_rgt], name=tag)

# ── CATALOG MECHANISM: outer shell (5x5x5), two nested void shells ────────────
# outer solid boundary
outer_shell = make_box_closed_shell(-5.0, -5.0, -5.0, 10.0, 10.0, 10.0, "outer")

# void1: 3x3x3 box centred at origin
void1_shell = make_box_closed_shell(-1.5, -1.5, -1.5, 3.0, 3.0, 3.0, "void1")

# void2: 1x1x1 box INSIDE void1 — nested/imbricated (IS the defect)
void2_shell = make_box_closed_shell(-0.5, -0.5, -0.5, 1.0, 1.0, 1.0, "void2")

# Solid body
msb = f._emit_raw(f"MANIFOLD_SOLID_BREP('outer_body',#{outer_shell.eid})")

# BREP_WITH_VOIDS: both void shells listed — inner void2 is nested inside void1
# NOTE: cfs_faces is DERIVE'd in ORIENTED_CLOSED_SHELL (redeclared from
# connected_face_set), so the Part-21 attribute list must carry a `*`
# placeholder for it: (name, *, closed_shell_element, orientation).
ocs1 = f._emit_raw(f"ORIENTED_CLOSED_SHELL('',*,#{void1_shell.eid},.F.)")
ocs2 = f._emit_raw(f"ORIENTED_CLOSED_SHELL('',*,#{void2_shell.eid},.F.)")
bwv  = f._emit_raw(
    f"BREP_WITH_VOIDS('bo003_nested_voids',#{outer_shell.eid},(#{ocs1.eid},#{ocs2.eid}))"
)

f.add_product_chain(bwv, mode="brep_shape")
