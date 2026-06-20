"""Tfa034 — Face orientation flag inconsistent with shell normal.

Catalog claim: One or more faces in a closed shell have orientation flags
inverted relative to the outward direction. Visualization shows mixed red/blue
normals. Common after Booleans or sloppy hand-built shells; also from sender
mirror-block instances.

Mechanism: MANIFOLD_SOLID_BREP built from a CLOSED_SHELL that is a valid unit
cube with six faces, but face[0] (the bottom face at z=0) is wired into the
shell with the sense flag set to .F. instead of .T., so its normal points
inward (into the solid) rather than outward.

  face[0]: bottom z=0 — ADVANCED_FACE with face_outer_bound orientation=False
    (the defect: sense flag inverted relative to outward shell normal)
  face[1]: top z=1      — correct outward orientation
  face[2]: front y=0    — correct
  face[3]: back y=1     — correct
  face[4]: left x=0     — correct
  face[5]: right x=1    — correct

The ADVANCED_FACE plane normals are geometrically correct; only the
FACE_OUTER_BOUND orientation flag for face[0] is wrong (.F. instead of .T.).

Tier-3 assertions:
  n_edges_total >= 24
  face[0].surface_type == "plane"
  face[5].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(27) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa034",
    defect=(
        "CLOSED_SHELL unit cube: face[0] (bottom z=0) has FACE_OUTER_BOUND "
        "orientation=.F. (inverted) so its normal points inward into the solid; "
        "faces[1-5] have correct outward orientation; "
        "FixFaceOrientation must flood-fill from a correct-seed face and flip "
        "the inverted face's orientation flag; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)


def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))


def mk_line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    mag = abs(dx) + abs(dy) + abs(dz)
    vec = f.vector(d, float(mag))
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)


# Cube vertices
p000 = pt(0,0,0); p100 = pt(1,0,0); p110 = pt(1,1,0); p010 = pt(0,1,0)
p001 = pt(0,0,1); p101 = pt(1,0,1); p111 = pt(1,1,1); p011 = pt(0,1,1)
v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# ── Bottom z=0 edges ──────────────────────────────────────────────────────────
e_b0 = mk_line_edge(v000, v100, p000,  1, 0, 0)
e_b1 = mk_line_edge(v100, v110, p100,  0, 1, 0)
e_b2 = mk_line_edge(v110, v010, p110, -1, 0, 0)
e_b3 = mk_line_edge(v010, v000, p010,  0,-1, 0)
lp_bot = f.edge_loop([f.oriented_edge(e_b0, True), f.oriented_edge(e_b1, True),
                      f.oriented_edge(e_b2, True), f.oriented_edge(e_b3, True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
# DEFECT: face_outer_bound orientation=False → normal flipped inward
fob_bot = f.face_outer_bound(lp_bot, orientation=False)
face_bot = f.advanced_face([fob_bot], f.plane(ax_bot))

# ── Top z=1 ───────────────────────────────────────────────────────────────────
e_t0 = mk_line_edge(v001, v101, p001,  1, 0, 0)
e_t1 = mk_line_edge(v101, v111, p101,  0, 1, 0)
e_t2 = mk_line_edge(v111, v011, p111, -1, 0, 0)
e_t3 = mk_line_edge(v011, v001, p011,  0,-1, 0)
lp_top = f.edge_loop([f.oriented_edge(e_t0, True), f.oriented_edge(e_t1, True),
                      f.oriented_edge(e_t2, True), f.oriented_edge(e_t3, True)])
ax_top = f.axis2_placement_3d(p001, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_top = f.advanced_face([f.face_outer_bound(lp_top)], f.plane(ax_top))

# ── Front y=0 ─────────────────────────────────────────────────────────────────
e_f0 = mk_line_edge(v000, v100, p000,  1, 0, 0)
e_f1 = mk_line_edge(v100, v101, p100,  0, 0, 1)
e_f2 = mk_line_edge(v101, v001, p101, -1, 0, 0)
e_f3 = mk_line_edge(v001, v000, p001,  0, 0,-1)
lp_frt = f.edge_loop([f.oriented_edge(e_f0, True), f.oriented_edge(e_f1, True),
                      f.oriented_edge(e_f2, True), f.oriented_edge(e_f3, True)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt))

# ── Back y=1 ──────────────────────────────────────────────────────────────────
e_bk0 = mk_line_edge(v010, v011, p010,  0, 0, 1)
e_bk1 = mk_line_edge(v011, v111, p011,  1, 0, 0)
e_bk2 = mk_line_edge(v111, v110, p111,  0, 0,-1)
e_bk3 = mk_line_edge(v110, v010, p110, -1, 0, 0)
lp_bk = f.edge_loop([f.oriented_edge(e_bk0, True), f.oriented_edge(e_bk1, True),
                     f.oriented_edge(e_bk2, True), f.oriented_edge(e_bk3, True)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk))

# ── Left x=0 ──────────────────────────────────────────────────────────────────
e_l0 = mk_line_edge(v000, v001, p000,  0, 0, 1)
e_l1 = mk_line_edge(v001, v011, p001,  0, 1, 0)
e_l2 = mk_line_edge(v011, v010, p011,  0, 0,-1)
e_l3 = mk_line_edge(v010, v000, p010,  0,-1, 0)
lp_lft = f.edge_loop([f.oriented_edge(e_l0, True), f.oriented_edge(e_l1, True),
                      f.oriented_edge(e_l2, True), f.oriented_edge(e_l3, True)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft))

# ── Right x=1 ─────────────────────────────────────────────────────────────────
e_r0 = mk_line_edge(v100, v110, p100,  0, 1, 0)
e_r1 = mk_line_edge(v110, v111, p110,  0, 0, 1)
e_r2 = mk_line_edge(v111, v101, p111,  0,-1, 0)
e_r3 = mk_line_edge(v101, v100, p101,  0, 0,-1)
lp_rgt = f.edge_loop([f.oriented_edge(e_r0, True), f.oriented_edge(e_r1, True),
                      f.oriented_edge(e_r2, True), f.oriented_edge(e_r3, True)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt))

# ── CLOSED_SHELL: face[0] has inverted orientation flag ────────────────────────
closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa034.stp")
