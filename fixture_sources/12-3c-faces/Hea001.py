"""Hea001 — Top-level shape-healing pipeline must converge over multi-defect GEOMETRIC_SET.

Catalog claim: A top-level GEOMETRIC_SET compound mixes three distinct
defective sub-shapes whose fix order matters:
  (a) A defective ADVANCED_FACE with a tiny scrambled inner wire (sub-tolerance
      triangle, wrong orientation flag) — exercises face-level fixers;
  (b) A two-face OPEN_SHELL where face B has same_sense flipped and the shared
      edge is re-used with opposite orientation — exercises shell-level fixers;
  (c) A 3-edge scrambled-order free EDGE_LOOP wire — exercises wire-level fixers.

The shape-level orchestrator (ShapeFix_Shape::Perform) must dispatch to each
sub-fixer in the right order without looping indefinitely.

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea001",
    defect=(
        "GEOMETRIC_SET compound mixing three defective sub-shapes: "
        "(a) ADVANCED_FACE with tiny scrambled inner wire (sub-tolerance, wrong orientation); "
        "(b) OPEN_SHELL with face B same_sense .F. + shared edge in opposite orientation; "
        "(c) free EDGE_LOOP wire with scrambled edge order; "
        "ShapeFix_Shape orchestrator must converge over all three without looping"
    ),
)

# ── (a) Defective face: 10x10 square with scrambled inner triangle ────────────
# Plane at z=0
orig_a = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
plc_a  = f.axis2_placement_3d(orig_a, zdir, xdir)
plane_a = f.plane(plc_a)

# Outer 10×10 square
p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point((10.0, 0.0, 0.0))
p_tr = f.cartesian_point((10.0, 10.0, 0.0))
p_tl = f.cartesian_point((0.0, 10.0, 0.0))
v_bl = f.vertex_point(p_bl)
v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

ec_b = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
ec_r = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
ec_t = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ec_l = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(ec_b, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
])
fob_a = f.face_outer_bound(outer_loop)

# Defective inner wire: sub-tolerance triangle (5.0,5.0)-(5.001,5.0)-(5.0,5.001)
# scrambled order: edge3 first, then edge1, then edge2; .T. on inner = wrong orientation
p_i1 = f.cartesian_point((5.0, 5.0, 0.0))
p_i2 = f.cartesian_point((5.001, 5.0, 0.0))
p_i3 = f.cartesian_point((5.0, 5.001, 0.0))
v_i1 = f.vertex_point(p_i1)
v_i2 = f.vertex_point(p_i2)
v_i3 = f.vertex_point(p_i3)

# Edge 1: p_i1 -> p_i2 (along +X, sub-tolerance)
ie1 = f.edge_curve(v_i1, v_i2, f.line(p_i1, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)),
                   name="inner_e1")
# Edge 2: p_i2 -> p_i3 (diagonal NW, sub-tolerance)
import math as _math
_d2 = 1.0 / _math.sqrt(2.0)
ie2 = f.edge_curve(v_i2, v_i3,
                   f.line(p_i2, f.vector(f.direction((-_d2, _d2, 0.0)), 1.4142)),
                   name="inner_e2")
# Edge 3: p_i3 -> p_i1 (along -Y, sub-tolerance)
ie3 = f.edge_curve(v_i3, v_i1, f.line(p_i3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)),
                   name="inner_e3")

# Scrambled order: e3, e1, e2 (wrong order); .T. on FACE_BOUND (wrong orientation flag)
inner_loop = f.edge_loop([
    f.oriented_edge(ie3, True, name="inner_oe_e3"),
    f.oriented_edge(ie1, True, name="inner_oe_e1"),
    f.oriented_edge(ie2, True, name="inner_oe_e2"),
])
# FACE_INNER_BOUND with .T. = wrong orientation (should be .F. for inner holes)
fb_a = f._emit_raw(f"FACE_INNER_BOUND('inner_wrong_orientation',#{inner_loop.eid},.T.)")
face_a = f.advanced_face([fob_a, fb_a], plane_a, name="part_a_defective_face")

# ── (b) Defective shell: two faces sharing an edge, face B has same_sense .F. ─
# Plane at z=5
orig_sa = f.cartesian_point((0.0, 0.0, 5.0))
plc_sa  = f.axis2_placement_3d(orig_sa, zdir, xdir)
plane_sa = f.plane(plc_sa, name="shell_planeA")

orig_sb = f.cartesian_point((0.0, 0.0, 5.0))
plc_sb  = f.axis2_placement_3d(orig_sb, zdir, xdir)
plane_sb = f.plane(plc_sb, name="shell_planeB")

# Shell vertices: Face A is (0,0,5)-(2,0,5)-(2,2,5)-(0,2,5)
#                Face B shares edge (2,0,5)-(2,2,5), extends to (4,0,5)-(4,2,5)
p_Sa  = f.cartesian_point((0.0, 0.0, 5.0))
p_Ss0 = f.cartesian_point((2.0, 0.0, 5.0))
p_Ss1 = f.cartesian_point((2.0, 2.0, 5.0))
p_Sb  = f.cartesian_point((0.0, 2.0, 5.0))
p_Sc  = f.cartesian_point((4.0, 0.0, 5.0))
p_Sd  = f.cartesian_point((4.0, 2.0, 5.0))
v_Sa  = f.vertex_point(p_Sa, name="Sa")
v_Ss0 = f.vertex_point(p_Ss0, name="Ss0")
v_Ss1 = f.vertex_point(p_Ss1, name="Ss1")
v_Sb  = f.vertex_point(p_Sb, name="Sb")
v_Sc  = f.vertex_point(p_Sc, name="Sc")
v_Sd  = f.vertex_point(p_Sd, name="Sd")

# Shell A edges
ec_sA_bot = f.edge_curve(v_Sa, v_Ss0, f.line(p_Sa, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)),
                          name="shell_A_bottom")
ec_shared = f.edge_curve(v_Ss0, v_Ss1, f.line(p_Ss0, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)),
                          name="shell_shared")
ec_sA_top = f.edge_curve(v_Ss1, v_Sb, f.line(p_Ss1, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)),
                          name="shell_A_top")
ec_sA_lft = f.edge_curve(v_Sb, v_Sa, f.line(p_Sb, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)),
                          name="shell_A_left")
# Shell B edges
ec_sB_bot = f.edge_curve(v_Ss0, v_Sc, f.line(p_Ss0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)),
                          name="shell_B_bottom")
ec_sB_rgt = f.edge_curve(v_Sc, v_Sd, f.line(p_Sc, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)),
                          name="shell_B_right")
ec_sB_top = f.edge_curve(v_Sd, v_Ss1, f.line(p_Sd, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)),
                          name="shell_B_top")

# Face A loop
loopA = f.edge_loop([
    f.oriented_edge(ec_sA_bot, True),
    f.oriented_edge(ec_shared, True),
    f.oriented_edge(ec_sA_top, True),
    f.oriented_edge(ec_sA_lft, True),
], name="shellA_outer")
fob_sA = f.face_outer_bound(loopA)
face_sA = f.advanced_face([fob_sA], plane_sa, name="shell_faceA")

# Face B loop: shared edge traversed in reverse (ec_shared .F.)
loopB = f.edge_loop([
    f.oriented_edge(ec_sB_bot, True),
    f.oriented_edge(ec_sB_rgt, True),
    f.oriented_edge(ec_sB_top, True),
    f.oriented_edge(ec_shared, False),  # reverse
], name="shellB_outer")
fob_sB = f.face_outer_bound(loopB)
# DEFECT: same_sense = .F. on face B — shell orientation flipped
face_sB = f._emit_raw(
    f"ADVANCED_FACE('shell_faceB_flipped',(#{fob_sB.eid}),#{plane_sb.eid},.F.)"
)
shell_b = f.open_shell([face_sA, face_sB], name="part_b_defective_shell")

# ── (c) Free wire: 3-edge scrambled-order triangle at z=10 ───────────────────
p_Wa = f.cartesian_point((0.0, 0.0, 10.0))
p_Wb = f.cartesian_point((1.0, 0.0, 10.0))
p_Wc = f.cartesian_point((0.5, 0.866, 10.0))
v_Wa = f.vertex_point(p_Wa, name="Wa")
v_Wb = f.vertex_point(p_Wb, name="Wb")
v_Wc = f.vertex_point(p_Wc, name="Wc")

# Edges: e1(a->b), e2(b->c), e3(c->a)
we1 = f.edge_curve(v_Wa, v_Wb, f.line(p_Wa, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)),
                   name="wire_e1")
we2 = f.edge_curve(v_Wb, v_Wc, f.line(p_Wb, f.vector(f.direction((-0.5, 0.866, 0.0)), 1.0)),
                   name="wire_e2")
we3 = f.edge_curve(v_Wc, v_Wa, f.line(p_Wc, f.vector(f.direction((-0.5, -0.866, 0.0)), 1.0)),
                   name="wire_e3")
# Scrambled order: e3 first, then e1, then e2
free_wire = f.edge_loop([
    f.oriented_edge(we3, True, name="w_oe_e3"),
    f.oriented_edge(we1, True, name="w_oe_e1"),
    f.oriented_edge(we2, True, name="w_oe_e2"),
], name="part_c_free_wire_scrambled")

# ── Wrap all three in a GEOMETRIC_SET compound ────────────────────────────────
gset = f._emit_raw(
    f"GEOMETRIC_SET('compound_three_defects',(#{face_a.eid},#{shell_b.eid},#{free_wire.eid}))"
)
# Add product chain using the shell_b as the model entity (surface_shape mode)
f.add_product_chain(shell_b)

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea001.stp")
