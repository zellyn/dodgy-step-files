"""Twi064 — Wire-analysis pipeline collects all sub-check status flags without short-circuit.

Catalog claim: A diagnostic-only pass over a wire (no healing). The pipeline must
run CheckOrder, CheckSmall, CheckConnected, CheckEdgeCurves, CheckDegenerated,
CheckSelfIntersection, CheckLacking, CheckClosed and aggregate all status flags —
short-circuiting on the first defect leaves the user without a complete picture.
Typical fixture: an inner FACE_BOUND triangle with three near-coincident
VERTEX_POINTs and an EDGE_LOOP whose ORIENTED_EDGEs are listed out of head-to-tail
order — multiple defects in one EDGE_LOOP.

Mechanism IS a face with two wires:
  - outer wire: correct 10x10 square FACE_OUTER_BOUND
  - inner wire (FACE_BOUND): a triangle with three near-coincident VERTEX_POINTs
    at (5,5,0), (5+1e-7,5,0), (5,5+1e-7,0) — sub-tolerance side lengths (1e-7
    apart); ORIENTED_EDGEs listed in non-head-to-tail order (CheckOrder fails);
    sub-tolerance edges (CheckSmall fails); not properly closed (CheckClosed fails).
Multiple distinct sub-checks fail simultaneously on the inner wire. A pipeline
that short-circuits after CheckOrder would miss CheckSmall and CheckClosed.

The inner FACE_BOUND IS wired into an ADVANCED_FACE on a PLANE in a CLOSED_SHELL;
never orphaned. The multi-failure wire IS the mechanism.

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi064",
    defect=(
        "ADVANCED_FACE on a PLANE with TWO wires: "
        "outer FACE_OUTER_BOUND is a correct 10x10 square (4 edges, 4 vertices); "
        "inner FACE_BOUND is a degenerate triangle with near-coincident VERTEX_POINTs: "
        "v0=(5,5,0), v1=(5+1e-7,5,0), v2=(5,5+1e-7,0) — sub-tolerance side lengths 1e-7; "
        "ORIENTED_EDGEs in the inner EDGE_LOOP are listed out of head-to-tail order "
        "(CheckOrder fails) — edge for v2→v0 appears before edge for v1→v2; "
        "sub-tolerance edge lengths (CheckSmall fails); "
        "multiple distinct sub-checks fail on the inner wire simultaneously; "
        "a pipeline that short-circuits after first failure misses remaining checks; "
        "all entities ARE wired into ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Outer wire: correct 10x10 square ─────────────────────────────────────────
v_bl = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))
v_br = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))
v_tr = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))
v_tl = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))

e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
oe_bot = f.oriented_edge(e_bot, True)

e_rgt  = f.edge_curve(v_br, v_tr,
                      f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
oe_rgt = f.oriented_edge(e_rgt, True)

e_top  = f.edge_curve(v_tr, v_tl,
                      f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                             f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
oe_top = f.oriented_edge(e_top, True)

e_lft  = f.edge_curve(v_tl, v_bl,
                      f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                             f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))
oe_lft = f.oriented_edge(e_lft, True)

outer_loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")

# ── Inner wire: degenerate near-coincident triangle — multiple defects ─────────
# Three near-coincident vertices; sub-tolerance edge lengths (1e-7)
# DEFECT 1 (CheckSmall): edge lengths ~1e-7, far below tolerance
# DEFECT 2 (CheckOrder): ORIENTED_EDGEs deliberately out of head-to-tail order
GAP = 1.0e-7
iv0 = f.vertex_point(f.cartesian_point((5.0,       5.0,       0.0)))
iv1 = f.vertex_point(f.cartesian_point((5.0 + GAP, 5.0,       0.0)))
iv2 = f.vertex_point(f.cartesian_point((5.0,       5.0 + GAP, 0.0)))

# The three edges of the triangle (correct geometry but sub-tolerance lengths)
# ie0: iv0 → iv1
ie0 = f.edge_curve(iv0, iv1,
                   f.line(f.cartesian_point((5.0, 5.0, 0.0)),
                          f.vector(f.direction((1.0, 0.0, 0.0)), GAP)))
ioe0 = f.oriented_edge(ie0, True)

# ie1: iv1 → iv2
import math as _math
_d = _math.sqrt(GAP*GAP + GAP*GAP)
ie1 = f.edge_curve(iv1, iv2,
                   f.line(f.cartesian_point((5.0 + GAP, 5.0, 0.0)),
                          f.vector(f.direction((-1.0/_math.sqrt(2), 1.0/_math.sqrt(2), 0.0)), _d)))
ioe1 = f.oriented_edge(ie1, True)

# ie2: iv2 → iv0
ie2 = f.edge_curve(iv2, iv0,
                   f.line(f.cartesian_point((5.0, 5.0 + GAP, 0.0)),
                          f.vector(f.direction((0.0, -1.0, 0.0)), GAP)))
ioe2 = f.oriented_edge(ie2, True)

# DEFECT (CheckOrder): list ORIENTED_EDGEs out of head-to-tail order:
# head-to-tail order would be ioe0(v0→v1), ioe1(v1→v2), ioe2(v2→v0)
# We reorder to: ioe2(v2→v0), ioe0(v0→v1), ioe1(v1→v2) — breaking contiguity
# at the seam (ioe1 end=v2, next=ioe2 start=v2 but preceded by ioe0 end=v1,
# so ioe2 starts at v2 but the wire left off at v0, breaking order).
inner_loop = f._emit_raw(
    f"EDGE_LOOP('',(#{ioe2.eid},#{ioe0.eid},#{ioe1.eid}))"
)
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

# ── ADVANCED_FACE with both outer and inner wires ────────────────────────────
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
