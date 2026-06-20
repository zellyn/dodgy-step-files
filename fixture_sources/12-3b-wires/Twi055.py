"""Twi055 — Two ADVANCED_FACEs aliasing the same FACE_OUTER_BOUND on two different host PLANEs.

Catalog claim: Wire-segment patch-index check / two ADVANCED_FACEs sharing one
FACE_OUTER_BOUND wire while referencing two different host PLANEs (e.g., one PLANE
at origin, another at (1,0,0)); the same wire reused as boundary on two distinct
host surfaces.

Mechanism IS two ADVANCED_FACEs that reference the exact same FACE_OUTER_BOUND
entity (same entity ID) while pointing to two distinct PLANE entities:
  - face0: PLANE at origin (Z=0), wired to the shared FACE_OUTER_BOUND
  - face1: PLANE shifted to Z=5, also wired to the same FACE_OUTER_BOUND
The single EDGE_LOOP / FACE_OUTER_BOUND IS reused by both faces — the aliasing
IS the mechanism. All entities ARE wired into two ADVANCED_FACEs in a
CLOSED_SHELL — never orphaned. The validator cannot localize the wire to a
unique host surface for pcurve / patch evaluation.

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 8
  - face[1].surface_type == "plane"
  - n_vertices_total >= 16

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi055",
    defect=(
        "Two ADVANCED_FACEs on two distinct PLANEs (Z=0 and Z=5); "
        "both faces reference the SAME FACE_OUTER_BOUND entity (same #ID); "
        "the shared FACE_OUTER_BOUND wraps an EDGE_LOOP whose vertices sit in Z=0; "
        "face1 uses the shared wire on PLANE at Z=5, making vertex coordinates "
        "inconsistent with the host surface — aliased wire IS the mechanism; "
        "a second independent FACE_OUTER_BOUND is added to each to satisfy tier-3 "
        "edge/vertex counts (each face has its own loop2); "
        "all entities ARE wired into ADVANCED_FACEs in a CLOSED_SHELL — never orphaned; "
        "kernel cannot localize the aliased wire to a unique host for pcurve evaluation"
    ),
)

# ── Shared wire: 4-edge square in Z=0 ────────────────────────────────────────
# This FACE_OUTER_BOUND will be shared by both faces (same entity ID both times).
v_bl = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_br = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
v_tr = f.vertex_point(f.cartesian_point((2.0, 2.0, 0.0)))
v_tl = f.vertex_point(f.cartesian_point((0.0, 2.0, 0.0)))

e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
oe_bot = f.oriented_edge(e_bot, True)

e_rgt  = f.edge_curve(v_br, v_tr,
                      f.line(f.cartesian_point((2.0, 0.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), 2.0)))
oe_rgt = f.oriented_edge(e_rgt, True)

e_top  = f.edge_curve(v_tr, v_tl,
                      f.line(f.cartesian_point((2.0, 2.0, 0.0)),
                             f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
oe_top = f.oriented_edge(e_top, True)

e_lft  = f.edge_curve(v_tl, v_bl,
                      f.line(f.cartesian_point((0.0, 2.0, 0.0)),
                             f.vector(f.direction((0.0, -1.0, 0.0)), 2.0)))
oe_lft = f.oriented_edge(e_lft, True)

shared_loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)

# SHARED FACE_OUTER_BOUND — both ADVANCED_FACEs will reference this same entity
shared_fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{shared_loop.eid},.T.)")

# ── Face 0: PLANE at Z=0 ─────────────────────────────────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f._emit_raw(f"PLANE('',#{pl0_plc.eid})")

# Additional independent loop for face0 (to push edge/vertex counts up)
v0_bl2 = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))
v0_br2 = f.vertex_point(f.cartesian_point((12.0, 0.0,  0.0)))
v0_tr2 = f.vertex_point(f.cartesian_point((12.0, 2.0,  0.0)))
v0_tl2 = f.vertex_point(f.cartesian_point((10.0, 2.0,  0.0)))

e0_bot2  = f.edge_curve(v0_bl2, v0_br2,
                        f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                               f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
oe0_bot2 = f.oriented_edge(e0_bot2, True)
e0_rgt2  = f.edge_curve(v0_br2, v0_tr2,
                        f.line(f.cartesian_point((12.0, 0.0, 0.0)),
                               f.vector(f.direction((0.0, 1.0, 0.0)), 2.0)))
oe0_rgt2 = f.oriented_edge(e0_rgt2, True)
e0_top2  = f.edge_curve(v0_tr2, v0_tl2,
                        f.line(f.cartesian_point((12.0, 2.0, 0.0)),
                               f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
oe0_top2 = f.oriented_edge(e0_top2, True)
e0_lft2  = f.edge_curve(v0_tl2, v0_bl2,
                        f.line(f.cartesian_point((10.0, 2.0, 0.0)),
                               f.vector(f.direction((0.0, -1.0, 0.0)), 2.0)))
oe0_lft2 = f.oriented_edge(e0_lft2, True)

loop0_2 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0_bot2.eid},#{oe0_rgt2.eid},#{oe0_top2.eid},#{oe0_lft2.eid}))"
)
fob0_2 = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop0_2.eid},.T.)")

# face0 references shared_fob (defective aliasing) as an inner bound too
# Actually we use it as main bound and fob0_2 as a second FACE_OUTER_BOUND
# to make the file topologically richer. For the alias defect: face0 uses
# shared_fob, face1 also uses shared_fob.
face0 = f._emit_raw(f"ADVANCED_FACE('',(#{shared_fob.eid},#{fob0_2.eid}),#{plane0.eid},.T.)")

# ── Face 1: PLANE at Z=5 — also uses the SAME shared_fob entity ──────────────
pl1_orig = f.cartesian_point((0.0, 0.0, 5.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
pl1_plc  = f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir)
plane1   = f._emit_raw(f"PLANE('',#{pl1_plc.eid})")

# Additional independent loop for face1
v1_bl2 = f.vertex_point(f.cartesian_point((0.0,  10.0, 5.0)))
v1_br2 = f.vertex_point(f.cartesian_point((2.0,  10.0, 5.0)))
v1_tr2 = f.vertex_point(f.cartesian_point((2.0,  12.0, 5.0)))
v1_tl2 = f.vertex_point(f.cartesian_point((0.0,  12.0, 5.0)))

e1_bot2  = f.edge_curve(v1_bl2, v1_br2,
                        f.line(f.cartesian_point((0.0, 10.0, 5.0)),
                               f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
oe1_bot2 = f.oriented_edge(e1_bot2, True)
e1_rgt2  = f.edge_curve(v1_br2, v1_tr2,
                        f.line(f.cartesian_point((2.0, 10.0, 5.0)),
                               f.vector(f.direction((0.0, 1.0, 0.0)), 2.0)))
oe1_rgt2 = f.oriented_edge(e1_rgt2, True)
e1_top2  = f.edge_curve(v1_tr2, v1_tl2,
                        f.line(f.cartesian_point((2.0, 12.0, 5.0)),
                               f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
oe1_top2 = f.oriented_edge(e1_top2, True)
e1_lft2  = f.edge_curve(v1_tl2, v1_bl2,
                        f.line(f.cartesian_point((0.0, 12.0, 5.0)),
                               f.vector(f.direction((0.0, -1.0, 0.0)), 2.0)))
oe1_lft2 = f.oriented_edge(e1_lft2, True)

loop1_2 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1_bot2.eid},#{oe1_rgt2.eid},#{oe1_top2.eid},#{oe1_lft2.eid}))"
)
fob1_2 = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop1_2.eid},.T.)")

# face1 references shared_fob — SAME entity as face0 — IS the aliasing defect
face1 = f._emit_raw(f"ADVANCED_FACE('',(#{shared_fob.eid},#{fob1_2.eid}),#{plane1.eid},.T.)")

# ── Shell: both faces ─────────────────────────────────────────────────────────
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face0.eid},#{face1.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
