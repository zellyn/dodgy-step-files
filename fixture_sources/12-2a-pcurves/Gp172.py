"""Gp172 — PCURVE.basis_surface referencing the wrong (adjacent) ADVANCED_FACE surface.

Catalog claim: STEP file with two adjacent ADVANCED_FACE entities F1 (on surface S1:
PLANE at y=0, normal +Y) and F2 (on surface S2: CYLINDRICAL_SURFACE, radius=3,
axis along +Z). They share edge E: a line from (3,0,0) to (3,0,5) which lies on
both surfaces (satisfies x=3,y=0 on the plane, and x^2+y^2=9 on the cylinder).

THE DEFECT: The PCURVE for edge E contributed to the SURFACE_CURVE's pcurve list
for F1's face (the PLANE) has its basis_surface attribute pointing to S2 (the
CYLINDRICAL_SURFACE) instead of S1 (the PLANE). The 3D curve of E is correct.

Expected: OCCT may silently use the wrong surface's UV domain to evaluate the pcurve,
producing incorrect UV bounds for F1's boundary; checkshape may flag pcurve-off-surface.

Source: OCCT MANTIS 0030124.
B4 wave-6 DEF-EE. Confidence: HIGH.

Byte assertions:
  count_entity_def(b'ADVANCED_FACE') >= 2
  contains(b'PCURVE')
  contains(b'CYLINDRICAL_SURFACE')
  contains(b'PLANE')
Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp172",
    defect=(
        "Two adjacent ADVANCED_FACEs: F1 on PLANE (y=0, XZ plane, normal +Y) and "
        "F2 on CYLINDRICAL_SURFACE (radius=3, axis +Z); shared edge E: LINE from "
        "(3,0,0) to (3,0,5) lies on both surfaces; SURFACE_CURVE for E carries two "
        "pcurves — one for F2 (basis_surface=CYLINDRICAL_SURFACE, CORRECT) and one "
        "for F1 (THE DEFECT: basis_surface=CYLINDRICAL_SURFACE instead of PLANE); "
        "OCCT may silently miscompute UV bounds for F1 boundary; pcurve-off-surface; "
        "OCCT MANTIS 0030124; SHELL_BASED_SURFACE_MODEL IS model entity"
    ),
)

# UV parametric context.
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── S1: PLANE at y=0 (the XZ plane), normal = +Y ─────────────────────────────
s1_orig = f.cartesian_point((0.0, 0.0, 0.0))
s1_nrm  = f.direction((0.0, 1.0, 0.0))    # normal +Y
s1_xdir = f.direction((1.0, 0.0, 0.0))    # x-axis +X
s1_plc  = f.axis2_placement_3d(s1_orig, s1_nrm, s1_xdir)
surf_s1 = f.plane(s1_plc)

# ── S2: CYLINDRICAL_SURFACE, radius=3, axis along +Z at origin ───────────────
s2_orig = f.cartesian_point((0.0, 0.0, 0.0))
s2_zdir = f.direction((0.0, 0.0, 1.0))
s2_xdir = f.direction((1.0, 0.0, 0.0))
s2_plc  = f.axis2_placement_3d(s2_orig, s2_zdir, s2_xdir)
surf_s2 = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl_s2',#{s2_plc.eid},3.0)")

# ── Shared edge E vertices ─────────────────────────────────────────────────────
p_e_bot = f.cartesian_point((3.0, 0.0, 0.0))
p_e_top = f.cartesian_point((3.0, 0.0, 5.0))
v_e_bot = f.vertex_point(p_e_bot)
v_e_top = f.vertex_point(p_e_top)

# 3D curve for edge E: LINE from (3,0,0) to (3,0,5).
e_dir   = f.direction((0.0, 0.0, 1.0))
e_vec   = f.vector(e_dir, 5.0)
e_line3 = f.line(p_e_bot, e_vec)

# Pcurve for E on F2 (cylinder) — CORRECT: basis_surface = S2.
# On cylinder (theta, v) with axis+Z, xdir+X: point (3,0,z) → (theta=0, v=z).
pc_E_F2_start = f.cartesian_point((0.0, 0.0))
pc_E_F2_dir   = f.direction((0.0, 1.0))       # along v (z-axis)
pc_E_F2_vec   = f.vector(pc_E_F2_dir, 5.0)
pc_E_F2_line  = f.line(pc_E_F2_start, pc_E_F2_vec)
pc_E_F2_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_E_F2',(#{pc_E_F2_line.eid}),#{prc.eid})"
)
pcurve_E_F2   = f._emit_raw(
    f"PCURVE('pc_E_for_F2',#{surf_s2.eid},#{pc_E_F2_def.eid})"  # correct
)

# THE DEFECT: Pcurve for E on F1 (plane y=0) but basis_surface = S2 (WRONG).
# On plane y=0 (normal+Y, xdir+X): UV maps (u,v) → (u, 0, v). So (3,0,z) → (u=3, v=z).
# Correct pcurve would be at (3,0)→(3,5) in UV with basis_surface=S1.
# But we SET basis_surface=S2 (the cylinder) — that is the defect.
pc_E_F1_start = f.cartesian_point((3.0, 0.0))  # UV coords that SHOULD be on S1
pc_E_F1_dir   = f.direction((0.0, 1.0))
pc_E_F1_vec   = f.vector(pc_E_F1_dir, 5.0)
pc_E_F1_line  = f.line(pc_E_F1_start, pc_E_F1_vec)
pc_E_F1_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_E_F1_wrong',(#{pc_E_F1_line.eid}),#{prc.eid})"
)
# THE DEFECT IS IN THE NEXT LINE: basis_surface = surf_s2 (cylinder) not surf_s1 (plane).
pcurve_E_F1   = f._emit_raw(
    f"PCURVE('pc_E_for_F1_WRONG_BASIS',#{surf_s2.eid},#{pc_E_F1_def.eid})"
)

# SURFACE_CURVE: 3D line + two pcurves (one for each adjacent face).
sc_E = f._emit_raw(
    f"SURFACE_CURVE('shared_edge_E',#{e_line3.eid},"
    f"(#{pcurve_E_F1.eid},#{pcurve_E_F2.eid}),.PCURVE_S1.)"
)
ec_E = f._emit_raw(
    f"EDGE_CURVE('shared_edge_E',#{v_e_bot.eid},#{v_e_top.eid},#{sc_E.eid},.T.)"
)

# ── Face F2: quarter-cylinder strip, theta=[0, pi/2], z=[0, 5] ───────────────
# Vertices of F2: (3,0,0)=v_e_bot, (0,3,0), (0,3,5), (3,0,5)=v_e_top.
p_q1_bot = f.cartesian_point((0.0, 3.0, 0.0))
p_q1_top = f.cartesian_point((0.0, 3.0, 5.0))
v_q1_bot = f.vertex_point(p_q1_bot)
v_q1_top = f.vertex_point(p_q1_top)

# Bottom arc of F2 (z=0, theta from 0→pi/2).
arc_z0_center = f.cartesian_point((0.0, 0.0, 0.0))
arc_z0_z      = f.direction((0.0, 0.0, 1.0))
arc_z0_x      = f.direction((1.0, 0.0, 0.0))
arc_z0_ax     = f.axis2_placement_3d(arc_z0_center, arc_z0_z, arc_z0_x)
arc_z0_circ   = f._emit_raw(f"CIRCLE('arc_z0',#{arc_z0_ax.eid},3.0)")
pc_az0_s  = f.cartesian_point((0.0, 0.0))
pc_az0_d  = f.direction((1.0, 0.0)); pc_az0_v = f.vector(pc_az0_d, math.pi/2)
pc_az0_l  = f.line(pc_az0_s, pc_az0_v)
pc_az0_df = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pc_az0',(#{pc_az0_l.eid}),#{prc.eid})")
pc_az0    = f._emit_raw(f"PCURVE('pc_az0',#{surf_s2.eid},#{pc_az0_df.eid})")
sc_az0    = f._emit_raw(f"SURFACE_CURVE('sc_az0',#{arc_z0_circ.eid},(#{pc_az0.eid}),.PCURVE_S1.)")
ec_az0    = f._emit_raw(f"EDGE_CURVE('ec_az0',#{v_e_bot.eid},#{v_q1_bot.eid},#{sc_az0.eid},.T.)")

# Left edge of F2 (theta=pi/2, z from 0→5).
p_left_bot = f.cartesian_point((0.0, 3.0, 0.0))
d_lz       = f.direction((0.0, 0.0, 1.0)); v_lz = f.vector(d_lz, 5.0)
l_left_3d  = f.line(p_left_bot, v_lz)
pc_lf_s    = f.cartesian_point((math.pi/2, 0.0))
pc_lf_d    = f.direction((0.0, 1.0)); pc_lf_v = f.vector(pc_lf_d, 5.0)
pc_lf_l    = f.line(pc_lf_s, pc_lf_v)
pc_lf_df   = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pc_lf',(#{pc_lf_l.eid}),#{prc.eid})")
pc_lf      = f._emit_raw(f"PCURVE('pc_lf',#{surf_s2.eid},#{pc_lf_df.eid})")
sc_lf      = f._emit_raw(f"SURFACE_CURVE('sc_lf',#{l_left_3d.eid},(#{pc_lf.eid}),.PCURVE_S1.)")
ec_lf      = f._emit_raw(f"EDGE_CURVE('ec_lf',#{v_q1_bot.eid},#{v_q1_top.eid},#{sc_lf.eid},.T.)")

# Top arc of F2 (z=5, theta from pi/2→0, reversed).
arc_z5_center = f.cartesian_point((0.0, 0.0, 5.0))
arc_z5_ax     = f.axis2_placement_3d(arc_z5_center, arc_z0_z, arc_z0_x)
arc_z5_circ   = f._emit_raw(f"CIRCLE('arc_z5',#{arc_z5_ax.eid},3.0)")
pc_az5_s  = f.cartesian_point((0.0, 5.0))
pc_az5_d  = f.direction((1.0, 0.0)); pc_az5_v = f.vector(pc_az5_d, math.pi/2)
pc_az5_l  = f.line(pc_az5_s, pc_az5_v)
pc_az5_df = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pc_az5',(#{pc_az5_l.eid}),#{prc.eid})")
pc_az5    = f._emit_raw(f"PCURVE('pc_az5',#{surf_s2.eid},#{pc_az5_df.eid})")
sc_az5    = f._emit_raw(f"SURFACE_CURVE('sc_az5',#{arc_z5_circ.eid},(#{pc_az5.eid}),.PCURVE_S1.)")
ec_az5    = f._emit_raw(f"EDGE_CURVE('ec_az5',#{v_e_top.eid},#{v_q1_top.eid},#{sc_az5.eid},.T.)")

# F2 loop: az0(fwd) → lf(fwd) → az5(rev) → E(rev).
loop_f2 = f.edge_loop([
    f.oriented_edge(ec_az0, True),
    f.oriented_edge(ec_lf,  True),
    f.oriented_edge(ec_az5, False),
    f.oriented_edge(ec_E,   False),
])
face_f2 = f.advanced_face([f.face_outer_bound(loop_f2)], surf_s2)

# ── Face F1: single-edge loop using ec_E (the defective pcurve face) ─────────
# F1 uses ec_E with the wrong pcurve basis_surface.
# A single-edge degenerate loop is intentional: it isolates the defect.
loop_f1 = f.edge_loop([f.oriented_edge(ec_E, True)])
face_f1 = f.advanced_face([f.face_outer_bound(loop_f1)], surf_s1)

shell = f.open_shell([face_f1, face_f2])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
