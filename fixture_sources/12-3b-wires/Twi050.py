"""Twi050 — Two distinct wires share a VERTEX_POINT instance that needs to be split.

Catalog claim: Two unrelated wires (in two different faces) accidentally reference
the same VERTEX_POINT instance because the sender deduplicated vertices too
aggressively. Topology operators that assume vertices are owned by exactly one
connected component misbehave.

Mechanism IS the single VERTEX_POINT at (0,0,0) referenced by the outer wires of
two unrelated planar ADVANCED_FACEs — the same entity id appears in both EDGE_LOOPs.
The shared VERTEX_POINT IS wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → two
ADVANCED_FACEs in a SHELL_BASED_SURFACE_MODEL; never orphaned. The over-shared
vertex instance IS the mechanism.

Tier-3 assertions:
  - n_edges_total >= 6
  - face[0].surface_type == "plane"
  - face[1].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi050",
    defect=(
        "Two ADVANCED_FACEs on PLANEs; "
        "both outer EDGE_LOOPs reference the same VERTEX_POINT instance at (0,0,0); "
        "sender deduplicated vertices too aggressively — (0,0,0) appears in face-0 "
        "and face-1 wires as the exact same entity reference; "
        "the shared VERTEX_POINT IS the mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → "
        "ADVANCED_FACEs in a CLOSED_SHELL — never orphaned; "
        "kernel must detect vertex over-sharing and split into independent copies, "
        "one per wire, or reject as malformed"
    ),
)

# ── Shared VERTEX_POINT at (0,0,0) — IS mechanism ────────────────────────────
v_shared = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))   # shared by both faces

# ── Plane 0: 5x5 square in Z=0 ───────────────────────────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f._emit_raw(f"PLANE('',#{pl0_plc.eid})")

# Other vertices of face 0
v0_br = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)))
v0_tr = f.vertex_point(f.cartesian_point((5.0, 5.0, 0.0)))
v0_tl = f.vertex_point(f.cartesian_point((0.0, 5.0, 0.0)))

e0_bot  = f.edge_curve(v_shared, v0_br,
                        f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                               f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
oe0_bot = f.oriented_edge(e0_bot, True)

e0_rgt  = f.edge_curve(v0_br, v0_tr,
                        f.line(f.cartesian_point((5.0, 0.0, 0.0)),
                               f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)))
oe0_rgt = f.oriented_edge(e0_rgt, True)

e0_top  = f.edge_curve(v0_tr, v0_tl,
                        f.line(f.cartesian_point((5.0, 5.0, 0.0)),
                               f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0)))
oe0_top = f.oriented_edge(e0_top, True)

e0_lft  = f.edge_curve(v0_tl, v_shared,
                        f.line(f.cartesian_point((0.0, 5.0, 0.0)),
                               f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)))
oe0_lft = f.oriented_edge(e0_lft, True)

loop0 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0_bot.eid},#{oe0_rgt.eid},#{oe0_top.eid},#{oe0_lft.eid}))"
)
fob0  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop0.eid},.T.)")
face0 = f._emit_raw(f"ADVANCED_FACE('',(#{fob0.eid}),#{plane0.eid},.T.)")

# ── Plane 1: 5x5 square in Z=-10; reuses v_shared at (0,0,0) ─────────────────
pl1_orig = f.cartesian_point((0.0, 0.0, -10.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
pl1_plc  = f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir)
plane1   = f._emit_raw(f"PLANE('',#{pl1_plc.eid})")

# Reuse v_shared (same entity) for face 1's bottom-left corner — IS the defect
v1_br = f.vertex_point(f.cartesian_point((5.0, 0.0, -10.0)))
v1_tr = f.vertex_point(f.cartesian_point((5.0, 5.0, -10.0)))
v1_tl = f.vertex_point(f.cartesian_point((0.0, 5.0, -10.0)))
# Note: v_shared is at (0,0,0), geometrically wrong for Z=-10, but that's the defect.

e1_bot  = f.edge_curve(v_shared, v1_br,
                        f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                               f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
oe1_bot = f.oriented_edge(e1_bot, True)

e1_rgt  = f.edge_curve(v1_br, v1_tr,
                        f.line(f.cartesian_point((5.0, 0.0, -10.0)),
                               f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)))
oe1_rgt = f.oriented_edge(e1_rgt, True)

e1_top  = f.edge_curve(v1_tr, v1_tl,
                        f.line(f.cartesian_point((5.0, 5.0, -10.0)),
                               f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0)))
oe1_top = f.oriented_edge(e1_top, True)

e1_lft  = f.edge_curve(v1_tl, v_shared,
                        f.line(f.cartesian_point((0.0, 5.0, -10.0)),
                               f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)))
oe1_lft = f.oriented_edge(e1_lft, True)

loop1 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1_bot.eid},#{oe1_rgt.eid},#{oe1_top.eid},#{oe1_lft.eid}))"
)
fob1  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop1.eid},.T.)")
face1 = f._emit_raw(f"ADVANCED_FACE('',(#{fob1.eid}),#{plane1.eid},.T.)")

# ── Shell containing both faces ───────────────────────────────────────────────
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face0.eid},#{face1.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
