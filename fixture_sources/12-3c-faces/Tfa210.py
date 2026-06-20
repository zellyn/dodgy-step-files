"""Tfa210 — FixSplitFace multi-loop split on disconnected wires

Planar face with outer boundary and two disconnected inner hole loops. Tests
face-splitting branch that detects topological separation and splits into
independent faces when holes lack connection edges to outer boundary.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The outer boundary
is a 10×10 square CCW loop. Two inner hole wires are small 1×1 squares placed
well apart from each other (at (2,2) and (7,7)). Because neither inner loop
shares any edges with the outer boundary, the OCCT FixSplitFace code path at
lines 2908-2930 detects topological separation and splits the face into three
independent faces (the outer region plus each hole considered independently).
The disconnected inner wires are the defect on the live traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa210",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "outer boundary: 10×10 square CCW; "
        "inner wire 1: 1×1 square hole at (2,2) - disconnected from outer; "
        "inner wire 2: 1×1 square hole at (7,7) - disconnected from outer; "
        "FixSplitFace lines 2908-2930: disconnected-wire detection; "
        "splits face into 3 independent faces (outer + two holes); "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ───────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))

# ── Outer boundary: 10×10 square CCW ─────────────────────────────────────────
op_ll = f.cartesian_point(( 0.0,  0.0, 0.0))
op_lr = f.cartesian_point((10.0,  0.0, 0.0))
op_ur = f.cartesian_point((10.0, 10.0, 0.0))
op_ul = f.cartesian_point(( 0.0, 10.0, 0.0))

ov_ll = f.vertex_point(op_ll)
ov_lr = f.vertex_point(op_lr)
ov_ur = f.vertex_point(op_ur)
ov_ul = f.vertex_point(op_ul)

oe_bot = f.edge_curve(ov_ll, ov_lr, f.line(op_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
oe_rgt = f.edge_curve(ov_lr, ov_ur, f.line(op_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
oe_top = f.edge_curve(ov_ur, ov_ul, f.line(op_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
oe_lft = f.edge_curve(ov_ul, ov_ll, f.line(op_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(oe_bot, True),
    f.oriented_edge(oe_rgt, True),
    f.oriented_edge(oe_top, True),
    f.oriented_edge(oe_lft, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner wire 1: 1×1 square at (2, 2) — disconnected ───────────────────────
i1p_ll = f.cartesian_point((2.0, 2.0, 0.0))
i1p_lr = f.cartesian_point((3.0, 2.0, 0.0))
i1p_ur = f.cartesian_point((3.0, 3.0, 0.0))
i1p_ul = f.cartesian_point((2.0, 3.0, 0.0))

i1v_ll = f.vertex_point(i1p_ll)
i1v_lr = f.vertex_point(i1p_lr)
i1v_ur = f.vertex_point(i1p_ur)
i1v_ul = f.vertex_point(i1p_ul)

i1e_bot = f.edge_curve(i1v_ll, i1v_lr, f.line(i1p_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
i1e_rgt = f.edge_curve(i1v_lr, i1v_ur, f.line(i1p_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
i1e_top = f.edge_curve(i1v_ur, i1v_ul, f.line(i1p_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
i1e_lft = f.edge_curve(i1v_ul, i1v_ll, f.line(i1p_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

inner_loop1 = f.edge_loop([
    f.oriented_edge(i1e_bot, True),
    f.oriented_edge(i1e_rgt, True),
    f.oriented_edge(i1e_top, True),
    f.oriented_edge(i1e_lft, True),
])
inner_fb1 = f.face_bound(inner_loop1, False)

# ── Inner wire 2: 1×1 square at (7, 7) — disconnected ───────────────────────
i2p_ll = f.cartesian_point((7.0, 7.0, 0.0))
i2p_lr = f.cartesian_point((8.0, 7.0, 0.0))
i2p_ur = f.cartesian_point((8.0, 8.0, 0.0))
i2p_ul = f.cartesian_point((7.0, 8.0, 0.0))

i2v_ll = f.vertex_point(i2p_ll)
i2v_lr = f.vertex_point(i2p_lr)
i2v_ur = f.vertex_point(i2p_ur)
i2v_ul = f.vertex_point(i2p_ul)

i2e_bot = f.edge_curve(i2v_ll, i2v_lr, f.line(i2p_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
i2e_rgt = f.edge_curve(i2v_lr, i2v_ur, f.line(i2p_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
i2e_top = f.edge_curve(i2v_ur, i2v_ul, f.line(i2p_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
i2e_lft = f.edge_curve(i2v_ul, i2v_ll, f.line(i2p_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

inner_loop2 = f.edge_loop([
    f.oriented_edge(i2e_bot, True),
    f.oriented_edge(i2e_rgt, True),
    f.oriented_edge(i2e_top, True),
    f.oriented_edge(i2e_lft, True),
])
inner_fb2 = f.face_bound(inner_loop2, False)

# ── Assemble face: outer + two disconnected inner holes ───────────────────────
face = f.advanced_face([outer_fob, inner_fb1, inner_fb2], plane)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa210.stp")
