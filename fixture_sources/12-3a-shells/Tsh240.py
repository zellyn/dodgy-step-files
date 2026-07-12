"""Tsh240 — Second independent BREP_WITH_VOIDS nested-void solid, geometry
distinct from Tsh015 (insurance fixture for occt-coverage `bc-enclosed-region`).

Catalog claim (occt-coverage `bc-enclosed-region`, BRepCheck_Solid.cxx:297
EnclosedRegion branch): a solid whose internal shell is fully enclosed within
another shell (a void/nested-solid configuration) that the analyzer flags as
needing attention rather than assuming intentional void semantics. Per the
occt-coverage audit (problems.json, `bc-enclosed-region`), Tsh015 is the SOLE
surviving fixture for this class (Bo003/Bo004 were pruned as structurally
unable to fire it). This fixture is a second, independent, geometrically
distinct BREP_WITH_VOIDS to reduce that single-fixture dependency, WITHOUT
modifying Tsh015.

Distinct from Tsh015: Tsh015 nests two axis-aligned unit CUBES (2x2x2 outer,
1x1x1 inner, both regular cubes). This fixture nests two RECTANGULAR
(non-cube) boxes of different proportions and a different outer origin —
outer 12x8x6 box at origin, inner 4x3x2 void box offset inside it — so no
coordinate or dimension in this fixture's bytes matches Tsh015's.

Mechanism IS the shell topology: outer CLOSED_SHELL (6-face 12x8x6 box) and
void CLOSED_SHELL (6-face 4x3x2 box, geometrically fully interior to the
outer box) are assembled via BREP_WITH_VOIDS. Per AP214, the void's
ORIENTED_CLOSED_SHELL orientation must be reversed (`.F.`) relative to the
outer shell; this fixture emits it as `.T.` instead (same defect direction
as Tsh015, distinct geometry) — the mis-oriented void is wired directly into
the shell topology via a real, reachable ORIENTED_CLOSED_SHELL, not an
orphaned/dead entity.

Live-oracle note (verified directly against this worktree's OCP/OCCT 7.8.1):
BRepCheck_Analyzer on a raw BRep_Builder-constructed solid with two shells
(outer + geometrically-enclosed inner, no reversal applied) DOES reliably
raise BRepCheck_Status.BRepCheck_EnclosedRegion in-memory — confirming the
check itself is real and reachable. However, OCCT's STEPControl_Reader
default transfer path silently reclassifies/heals BREP_WITH_VOIDS void
orientation by signed-volume sign during translation (this was independently
re-verified live on both this fixture's `.T.` encoding and a hand-corrected
`.F.` encoding: both translate to BRepCheck_Status.NoError). That silent
healing is itself the catalog's documented "Expected kernel behavior" for
this class ("heal; detect mis-oriented voids by signed-volume sign;
auto-reverse with warning") — OCCT performs the heal, just without the
warning. The byte-level defect (a real, reachable ORIENTED_CLOSED_SHELL
carrying the wrong orientation flag inside a genuine nested-void
BREP_WITH_VOIDS) is what this fixture demonstrates; live shape validity
after translation is expected to be healed, matching Tsh015's own class.

Byte assertions:
  - contains(b'ORIENTED_CLOSED_SHELL')
  - count_entity_def(b'CLOSED_SHELL') == 2

Tier-3 assertions (live-computed via tier3_geometric.py):
  - n_faces_total == 12
  - face[0].surface_type == "plane"

live oracle (computed via validate2.py against this worktree's bytes):
  occt=shape(1)/shape(1) gmsh=shape(52)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh240",
    defect=(
        "BREP_WITH_VOIDS: outer CLOSED_SHELL (12x8x6 box) and void "
        "CLOSED_SHELL (4x3x2 box, geometrically nested fully inside outer) "
        "assembled via ORIENTED_CLOSED_SHELL with the void's orientation "
        "flag .T. instead of the AP214-required .F.; mis-oriented void IS "
        "wired into real, reachable shell topology (distinct dimensions "
        "and origin from Tsh015's unit-cube pair) — a second, independent "
        "bc-enclosed-region fixture"
    ),
)


def make_box_closed_shell(ox, oy, oz, sx, sy, sz, tag):
    """Build a watertight CLOSED_SHELL box at origin (ox,oy,oz), size (sx,sy,sz)."""
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
        orig = f.cartesian_point((px, py, pz))
        zd = f.direction((zx, zy, zz)); xd = f.direction((xx, xy, xz))
        return f.plane(f.axis2_placement_3d(orig, zd, xd))

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
    f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
    f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
    f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
    f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

    return f.closed_shell([f_bot, f_top, f_frt, f_bck, f_lft, f_rgt], name=tag)


# Outer shell: 12x8x6 box, corner at origin.
outer_shell = make_box_closed_shell(0.0, 0.0, 0.0, 12.0, 8.0, 6.0, "tsh240_outer")

# Void shell: 4x3x2 box, geometrically fully nested inside the outer box
# (outer spans x[0,12] y[0,8] z[0,6]; void spans x[4,8] y[2,5] z[2,4]).
void_shell = make_box_closed_shell(4.0, 2.0, 2.0, 4.0, 3.0, 2.0, "tsh240_void")

# DEFECT: void's ORIENTED_CLOSED_SHELL orientation is .T. instead of the
# AP214-required .F. — mis-classifies the void as positive material.
ocs_void = f._emit_raw(f"ORIENTED_CLOSED_SHELL('',*,#{void_shell.eid},.T.)")
bwv = f._emit_raw(
    f"BREP_WITH_VOIDS('tsh240_bwv',#{outer_shell.eid},(#{ocs_void.eid}))"
)

f.add_product_chain(bwv, mode="brep_shape")
