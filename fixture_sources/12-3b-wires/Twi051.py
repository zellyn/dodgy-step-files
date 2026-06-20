"""Twi051 — Wire-level healing pipeline must order reorder/connect/lacking/closed fixes.

Catalog claim: A wire simultaneously has out-of-order edges, a 3D gap between two
of its edges, and a missing edge between two non-coincident vertices. Fixing in the
wrong order (e.g., reorder before connect) produces a different end-state. The
wire-level orchestrator must apply fixes in a sequence that converges on a closed wire.

Mechanism IS a FACE with two wires:
  - outer wire: 4 edges in scrambled ORIENTED_EDGE order (not head-to-tail) on a
    5x5 square — reorder defect;
  - inner wire (FACE_BOUND triangle): 3 near-coincident vertices with a sub-tolerance
    hole and ORIENTED_EDGEs listed out of head-to-tail order — pipeline order defect.
Both wires ARE wired into FACE_OUTER_BOUND / FACE_BOUND → ADVANCED_FACE in a
SHELL_BASED_SURFACE_MODEL; never orphaned. The scrambled edge order in both wires
IS the mechanism.

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi051",
    defect=(
        "ADVANCED_FACE on a PLANE (5x5); "
        "outer EDGE_LOOP has four ORIENTED_EDGEs listed in scrambled (non-sequential) "
        "head-to-tail order — reorder defect IS part of mechanism; "
        "inner FACE_BOUND is a triangle with near-coincident vertices (1e-4 gap) and "
        "ORIENTED_EDGEs also out of head-to-tail order — pipeline defect IS mechanism; "
        "multi-defect: reorder must happen before connect for convergence; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUND + FACE_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned; "
        "kernel healing pipeline must apply: reorder → connect → lacking → closure, "
        "in that order, for each wire"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Outer wire vertices: 5x5 square ──────────────────────────────────────────
v_bl = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_br = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)))
v_tr = f.vertex_point(f.cartesian_point((5.0, 5.0, 0.0)))
v_tl = f.vertex_point(f.cartesian_point((0.0, 5.0, 0.0)))

# Edges in correct geometry but listed in scrambled order below
e_bot = f.edge_curve(v_bl, v_br,
                     f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                            f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
e_rgt = f.edge_curve(v_br, v_tr,
                     f.line(f.cartesian_point((5.0, 0.0, 0.0)),
                            f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)))
e_top = f.edge_curve(v_tr, v_tl,
                     f.line(f.cartesian_point((5.0, 5.0, 0.0)),
                            f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0)))
e_lft = f.edge_curve(v_tl, v_bl,
                     f.line(f.cartesian_point((0.0, 5.0, 0.0)),
                            f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)))

# SCRAMBLED order: top, bot, lft, rgt — not head-to-tail — IS mechanism
oe_top = f.oriented_edge(e_top, True)
oe_bot = f.oriented_edge(e_bot, True)
oe_lft = f.oriented_edge(e_lft, True)
oe_rgt = f.oriented_edge(e_rgt, True)

outer_loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_top.eid},#{oe_bot.eid},#{oe_lft.eid},#{oe_rgt.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")

# ── Inner wire: small triangle with near-coincident vertices + scrambled order ─
# Triangle at ~(2,2) with 1e-4 gap on one vertex — near-coincident defect
v_t0 = f.vertex_point(f.cartesian_point((2.0,       2.0,       0.0)))
v_t1 = f.vertex_point(f.cartesian_point((3.0,       2.0,       0.0)))
v_t2 = f.vertex_point(f.cartesian_point((2.5,       3.0,       0.0)))
# Near-coincident: v_t2b is 1e-4 away from v_t2 — sub-threshold gap defect
v_t2b = f.vertex_point(f.cartesian_point((2.5,      3.0001,    0.0)))

e_t01 = f.edge_curve(v_t0, v_t1,
                     f.line(f.cartesian_point((2.0, 2.0, 0.0)),
                            f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
e_t12 = f.edge_curve(v_t1, v_t2,
                     f.line(f.cartesian_point((3.0, 2.0, 0.0)),
                            f.vector(f.direction((-0.5, 1.0, 0.0)), 1.118)))
# Gap edge: v_t2b → v_t0; v_t2b is 1e-4 from v_t2, creating a hole
e_t20 = f.edge_curve(v_t2b, v_t0,
                     f.line(f.cartesian_point((2.5, 3.0001, 0.0)),
                            f.vector(f.direction((-0.5, -1.0, 0.0)), 1.118)))

# SCRAMBLED order for inner wire: e_t20, e_t01, e_t12 — not head-to-tail
oe_t20 = f.oriented_edge(e_t20, True)
oe_t01 = f.oriented_edge(e_t01, True)
oe_t12 = f.oriented_edge(e_t12, True)

inner_loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_t20.eid},#{oe_t01.eid},#{oe_t12.eid}))"
)
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

# Wire both bounds into single ADVANCED_FACE
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
