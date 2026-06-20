"""Twi049 — Wire on a face self-intersects in the host surface's parameter space.

Catalog claim: A single closed wire's edges, when projected to the host face's UV
parameter space, cross each other (figure-eight shape). The wire is topologically
closed but geometrically self-intersecting; it cannot bound a simple region.

Mechanism IS the EDGE_LOOP of four edges forming a figure-eight: the diagonals
cross at (5,5) in XY (the plane's UV space). The four edges are:
  (0,0,0)→(10,10,0), (10,10,0)→(10,0,0), (10,0,0)→(0,10,0), (0,10,0)→(0,0,0).
The EDGE_LOOP IS wired into a FACE_OUTER_BOUND on a planar ADVANCED_FACE in a
SHELL_BASED_SURFACE_MODEL; never orphaned. The UV-space crossing IS the mechanism.

Tier-3 assertions:
  - n_edges_total >= 6
  - face[0].surface_type == "plane"
  - face[1].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi049",
    defect=(
        "Two ADVANCED_FACEs on PLANEs; "
        "face 0 has an EDGE_LOOP of four diagonal edges that self-intersect in UV "
        "space (figure-eight): (0,0,0)→(10,10,0)→(10,0,0)→(0,10,0)→(0,0,0); "
        "the diagonals cross at (5,5,0) in XY = UV of the host plane; "
        "face 1 is a correct 10x10 square — provides n_faces_total >= 2 for tier-3; "
        "the UV-space self-intersection IS the mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → "
        "ADVANCED_FACEs in a single CLOSED_SHELL — never orphaned; "
        "kernel must detect UV crossing, split at intersection, or reject as malformed"
    ),
)

# ── Plane 0: the defective figure-eight face ──────────────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f._emit_raw(f"PLANE('',#{pl0_plc.eid})")

# Vertices of the figure-eight
v00 = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))
v10 = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))
v20 = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))
v30 = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))

# Edge 0: (0,0,0) → (10,10,0) — first diagonal
e0_line = f.line(f.cartesian_point((0.0,  0.0, 0.0)),
                 f.vector(f.direction((1.0, 1.0, 0.0)), 14.142135))
e0   = f.edge_curve(v00, v10, e0_line)
oe0  = f.oriented_edge(e0, True)

# Edge 1: (10,10,0) → (10,0,0)
e1_line = f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                 f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
e1   = f.edge_curve(v10, v20, e1_line)
oe1  = f.oriented_edge(e1, True)

# Edge 2: (10,0,0) → (0,10,0) — second diagonal, crosses first at (5,5,0)
e2_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                 f.vector(f.direction((-1.0, 1.0, 0.0)), 14.142135))
e2   = f.edge_curve(v20, v30, e2_line)
oe2  = f.oriented_edge(e2, True)

# Edge 3: (0,10,0) → (0,0,0)
e3_line = f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                 f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
e3   = f.edge_curve(v30, v00, e3_line)
oe3  = f.oriented_edge(e3, True)

loop0 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob0  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop0.eid},.T.)")
face0 = f._emit_raw(f"ADVANCED_FACE('',(#{fob0.eid}),#{plane0.eid},.T.)")

# ── Plane 1: a correct 10x10 square face (provides tier-3 face[1]) ────────────
pl1_orig = f.cartesian_point((0.0, 0.0, -1.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
pl1_plc  = f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir)
plane1   = f._emit_raw(f"PLANE('',#{pl1_plc.eid})")

v_bl1 = f.vertex_point(f.cartesian_point((0.0,  0.0,  -1.0)))
v_br1 = f.vertex_point(f.cartesian_point((10.0, 0.0,  -1.0)))
v_tr1 = f.vertex_point(f.cartesian_point((10.0, 10.0, -1.0)))
v_tl1 = f.vertex_point(f.cartesian_point((0.0,  10.0, -1.0)))

bot1_line = f.line(f.cartesian_point((0.0,  0.0, -1.0)),
                   f.vector(f.direction((1.0,  0.0, 0.0)), 10.0))
rgt1_line = f.line(f.cartesian_point((10.0, 0.0, -1.0)),
                   f.vector(f.direction((0.0,  1.0, 0.0)), 10.0))
top1_line = f.line(f.cartesian_point((10.0, 10.0, -1.0)),
                   f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
lft1_line = f.line(f.cartesian_point((0.0,  10.0, -1.0)),
                   f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))

eb1 = f.edge_curve(v_bl1, v_br1, bot1_line); oeb1 = f.oriented_edge(eb1, True)
er1 = f.edge_curve(v_br1, v_tr1, rgt1_line); oer1 = f.oriented_edge(er1, True)
et1 = f.edge_curve(v_tr1, v_tl1, top1_line); oet1 = f.oriented_edge(et1, True)
el1 = f.edge_curve(v_tl1, v_bl1, lft1_line); oel1 = f.oriented_edge(el1, True)

loop1 = f._emit_raw(
    f"EDGE_LOOP('',(#{oeb1.eid},#{oer1.eid},#{oet1.eid},#{oel1.eid}))"
)
fob1  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop1.eid},.T.)")
face1 = f._emit_raw(f"ADVANCED_FACE('',(#{fob1.eid}),#{plane1.eid},.T.)")

# ── Shell containing both faces ───────────────────────────────────────────────
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face0.eid},#{face1.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
