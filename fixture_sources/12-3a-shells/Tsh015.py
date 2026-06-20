"""Tsh015 — BREP_WITH_VOIDS: void shell oriented .T. instead of .F. (ProSTEP TR9).

Catalog claim: Per AP214, voids in a BREP_WITH_VOIDS must be reversed
orientation relative to the outer shell; some files emit them with .T. so the
void is mis-classified as a positive volume.

Mechanism IS the shell structure: an outer CLOSED_SHELL (6-face unit cube) and
a void CLOSED_SHELL (6-face inner cube) are assembled in BREP_WITH_VOIDS via
ORIENTED_CLOSED_SHELL. The void's ORIENTED_CLOSED_SHELL flag is emitted raw as
.T. instead of the required .F., so the void is oriented the same as the outer
shell. This IS wired into the shell topology via the raw ORIENTED_CLOSED_SHELL
emission. Strict receivers must detect mis-oriented void by signed-volume sign,
auto-reverse with warning.

Byte assertions:
  - contains(b'ORIENTED_CLOSED_SHELL')
  - count_entity_def(b'CLOSED_SHELL') == 2

Tier-3 assertion: n_faces_total == 12
live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh015",
    defect=(
        "BREP_WITH_VOIDS: void CLOSED_SHELL wrapped in ORIENTED_CLOSED_SHELL with .T. "
        "instead of required .F.; void mis-classified as positive volume; orientation flag "
        "IS wired into shell topology via ORIENTED_CLOSED_SHELL; strict receivers must "
        "detect mis-oriented void and reverse with warning"
    ),
)


def _cube_shell(x0, y0, z0, x1, y1, z1):
    """Build a 6-face CLOSED_SHELL for the axis-aligned box [x0,x1]x[y0,y1]x[z0,z1]."""
    def pt(x, y, z):
        return f.cartesian_point((float(x), float(y), float(z)))

    def mk_edge(va, vb, pstart, dx, dy, dz):
        d = f.direction((float(dx), float(dy), float(dz)))
        vec = f.vector(d, 1.0)
        ln = f.line(pstart, vec)
        return f.edge_curve(va, vb, ln)

    p000 = pt(x0, y0, z0); p100 = pt(x1, y0, z0)
    p110 = pt(x1, y1, z0); p010 = pt(x0, y1, z0)
    p001 = pt(x0, y0, z1); p101 = pt(x1, y0, z1)
    p111 = pt(x1, y1, z1); p011 = pt(x0, y1, z1)
    v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
    v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
    v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
    v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

    # Bottom z=z0, outward normal (0,0,-1)
    e_b0 = mk_edge(v000, v010, p000,  0, 1, 0)
    e_b1 = mk_edge(v010, v110, p010,  1, 0, 0)
    e_b2 = mk_edge(v110, v100, p110,  0,-1, 0)
    e_b3 = mk_edge(v100, v000, p100, -1, 0, 0)
    lp_bot = f.edge_loop([f.oriented_edge(e_b0,True), f.oriented_edge(e_b1,True),
                          f.oriented_edge(e_b2,True), f.oriented_edge(e_b3,True)])
    ax_bot = f.axis2_placement_3d(p000, f.direction((0,0,-1)), f.direction((1,0,0)))
    face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot))

    # Top z=z1, outward normal (0,0,1)
    e_t0 = mk_edge(v001, v101, p001,  1, 0, 0)
    e_t1 = mk_edge(v101, v111, p101,  0, 1, 0)
    e_t2 = mk_edge(v111, v011, p111, -1, 0, 0)
    e_t3 = mk_edge(v011, v001, p011,  0,-1, 0)
    lp_top = f.edge_loop([f.oriented_edge(e_t0,True), f.oriented_edge(e_t1,True),
                          f.oriented_edge(e_t2,True), f.oriented_edge(e_t3,True)])
    ax_top = f.axis2_placement_3d(p001, f.direction((0,0,1)), f.direction((1,0,0)))
    face_top = f.advanced_face([f.face_outer_bound(lp_top)], f.plane(ax_top))

    # Front y=y0, outward normal (0,-1,0)
    e_f0 = mk_edge(v000, v100, p000,  1, 0, 0)
    e_f1 = mk_edge(v100, v101, p100,  0, 0, 1)
    e_f2 = mk_edge(v101, v001, p101, -1, 0, 0)
    e_f3 = mk_edge(v001, v000, p001,  0, 0,-1)
    lp_frt = f.edge_loop([f.oriented_edge(e_f0,True), f.oriented_edge(e_f1,True),
                          f.oriented_edge(e_f2,True), f.oriented_edge(e_f3,True)])
    ax_frt = f.axis2_placement_3d(p000, f.direction((0,-1,0)), f.direction((1,0,0)))
    face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt))

    # Back y=y1, outward normal (0,1,0)
    e_bk0 = mk_edge(v010, v011, p010,  0, 0, 1)
    e_bk1 = mk_edge(v011, v111, p011,  1, 0, 0)
    e_bk2 = mk_edge(v111, v110, p111,  0, 0,-1)
    e_bk3 = mk_edge(v110, v010, p110, -1, 0, 0)
    lp_bk = f.edge_loop([f.oriented_edge(e_bk0,True), f.oriented_edge(e_bk1,True),
                         f.oriented_edge(e_bk2,True), f.oriented_edge(e_bk3,True)])
    ax_bk = f.axis2_placement_3d(p010, f.direction((0,1,0)), f.direction((1,0,0)))
    face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk))

    # Left x=x0, outward normal (-1,0,0)
    e_l0 = mk_edge(v000, v001, p000,  0, 0, 1)
    e_l1 = mk_edge(v001, v011, p001,  0, 1, 0)
    e_l2 = mk_edge(v011, v010, p011,  0, 0,-1)
    e_l3 = mk_edge(v010, v000, p010,  0,-1, 0)
    lp_lft = f.edge_loop([f.oriented_edge(e_l0,True), f.oriented_edge(e_l1,True),
                          f.oriented_edge(e_l2,True), f.oriented_edge(e_l3,True)])
    ax_lft = f.axis2_placement_3d(p000, f.direction((-1,0,0)), f.direction((0,1,0)))
    face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft))

    # Right x=x1, outward normal (1,0,0)
    e_r0 = mk_edge(v100, v110, p100,  0, 1, 0)
    e_r1 = mk_edge(v110, v111, p110,  0, 0, 1)
    e_r2 = mk_edge(v111, v101, p111,  0,-1, 0)
    e_r3 = mk_edge(v101, v100, p101,  0, 0,-1)
    lp_rgt = f.edge_loop([f.oriented_edge(e_r0,True), f.oriented_edge(e_r1,True),
                          f.oriented_edge(e_r2,True), f.oriented_edge(e_r3,True)])
    ax_rgt = f.axis2_placement_3d(p100, f.direction((1,0,0)), f.direction((0,1,0)))
    face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt))

    return f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])


# Outer shell: 2x2x2 cube
outer_shell = _cube_shell(0, 0, 0, 2, 2, 2)

# Void shell: 1x1x1 inner cube (centered inside outer)
void_shell = _cube_shell(0.5, 0.5, 0.5, 1.5, 1.5, 1.5)

# ── DEFECT: ORIENTED_CLOSED_SHELL for void uses .T. instead of .F. ───────────
# AP214 requires void orientation .F. (reversed relative to outer shell).
# Emitting .T. mis-classifies the void as a positive volume.
# This IS wired into the shell topology via ORIENTED_CLOSED_SHELL.
ocs_outer = f._emit_raw(f"ORIENTED_CLOSED_SHELL('',*,#{outer_shell.eid},.T.)")
ocs_void  = f._emit_raw(f"ORIENTED_CLOSED_SHELL('',*,#{void_shell.eid},.T.)")  # DEFECT: should be .F.
bwv = f._emit_raw(f"BREP_WITH_VOIDS('tsh015_bwv',#{ocs_outer.eid},(#{ocs_void.eid}))")

f.add_product_chain(bwv, mode="brep_shape")
