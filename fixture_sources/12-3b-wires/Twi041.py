"""Twi041 — ADVANCED_FACE FACE_BOUND contains a VERTEX_LOOP wrapping a single internal
VERTEX_POINT (infinite loop in outer-wire detection).

Catalog claim: An ADVANCED_FACE with a normal square FACE_OUTER_BOUND plus an inner
FACE_BOUND containing a VERTEX_LOOP that wraps a single VERTEX_POINT inside the outer
wire. Such INTERNAL-orientation vertex sub-shapes cause an outer-wire-detection pass
to spin indefinitely, or to skip the primal wire when iteration reports only vertex
children remaining.

Mechanism IS the VERTEX_LOOP wired into a FACE_BOUND on the same ADVANCED_FACE that
carries the normal FACE_OUTER_BOUND. The VERTEX_LOOP wraps a single VERTEX_POINT at
(5,5,0) inside the 10x10 square face. This VERTEX_LOOP IS the inner bound entity —
referenced directly by a FACE_BOUND — which IS referenced by the ADVANCED_FACE
alongside the outer EDGE_LOOP. The ADVANCED_FACE IS wired into a CLOSED_SHELL in a
SHELL_BASED_SURFACE_MODEL; never orphaned. The VERTEX_LOOP IS the mechanism (internal
vertex sub-shape that stalls outer-wire detection).

Reproducer: 10x10 planar face with FACE_OUTER_BOUND (square EDGE_LOOP) and one
FACE_BOUND whose bound is a VERTEX_LOOP at the interior point (5, 5, 0).

Byte assertions:
  - count_entity_def(b'VERTEX_LOOP') == 1
  - count_entity_def(b'FACE_OUTER_BOUND') == 1
  - count_entity_def(b'FACE_BOUND') == 1

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi041",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 square); "
        "FACE_OUTER_BOUND carries a normal square EDGE_LOOP (4 edges); "
        "a second FACE_BOUND (inner, orientation .F.) carries a VERTEX_LOOP "
        "wrapping a single VERTEX_POINT at (5,5,0) inside the face; "
        "VERTEX_LOOP IS the mechanism (INTERNAL vertex sub-shape stalls outer-wire detection); "
        "both bounds ARE referenced by the ADVANCED_FACE; "
        "ADVANCED_FACE IS wired into CLOSED_SHELL in shell — never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Outer-wire vertices: 10x10 square ────────────────────────────────────────
v_bl = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))
v_br = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))
v_tr = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))
v_tl = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))

# ── Outer-wire edges ──────────────────────────────────────────────────────────
def make_edge(p1, v1, p2, v2, dx, dy, length):
    line = f.line(f.cartesian_point((p1, p2, 0.0)),
                  f.vector(f.direction((dx, dy, 0.0)), length))
    return f.edge_curve(v1, v2, line)

e_bot = make_edge(0.0,  v_bl, 0.0,  v_br, 1.0,  0.0, 10.0)
e_rgt = make_edge(10.0, v_br, 0.0,  v_tr, 0.0,  1.0, 10.0)
e_top = make_edge(10.0, v_tr, 10.0, v_tl, -1.0, 0.0, 10.0)
e_lft = make_edge(0.0,  v_tl, 10.0, v_bl, 0.0, -1.0, 10.0)

oe_bot = f.oriented_edge(e_bot, True)
oe_rgt = f.oriented_edge(e_rgt, True)
oe_top = f.oriented_edge(e_top, True)
oe_lft = f.oriented_edge(e_lft, True)

outer_loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")

# ── Interior VERTEX_LOOP — IS the mechanism ───────────────────────────────────
v_internal   = f.vertex_point(f.cartesian_point((5.0, 5.0, 0.0)))
vertex_loop  = f._emit_raw(f"VERTEX_LOOP('',#{v_internal.eid})")
inner_bound  = f._emit_raw(f"FACE_BOUND('',#{vertex_loop.eid},.F.)")

# ── ADVANCED_FACE referencing both bounds ─────────────────────────────────────
face  = f._emit_raw(
    f"ADVANCED_FACE('',(#{fob.eid},#{inner_bound.eid}),#{plane.eid},.T.)"
)
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
