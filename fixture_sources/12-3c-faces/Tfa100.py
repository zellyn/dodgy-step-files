"""Tfa100 — ShapeFix_Face.FixWiresTwoCoincEdges with seam.

Catalog claim: Face on cylinder with two wires both containing the cylinder's
seam edge (u=0/2π boundary). FixWiresTwoCoincEdges treats seams differently
than regular edges and misses the duplicate coincidence.

Mechanism: MANIFOLD_SOLID_BREP with two faces:
  face[0] — CYLINDRICAL_SURFACE face (radius 5, axis Z). Two wires:
    - outer wire: rectangle at v=0..2 (z=0..2), traversing the full
      circumference at u=0 and u=2π. A CIRCLE entity is used for the
      circumferential edges (u-direction). The seam edge runs at u=0.
    - inner wire (FACE_BOUND, not outer): a second rectangle also at
      v=0..2, identical circumferential loop, reusing the same CIRCLE
      geometry — the coincident seam defect.
  face[1] — flat rectangular plane cap to produce a valid shape(1) load.

Both wires contain seam-crossing edges that share geometry.
FixWiresTwoCoincEdges misses the coincidence because of the seam.

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa100",
    defect=(
        "CLOSED_SHELL: CYLINDRICAL_SURFACE face (radius=5, axis Z) with outer wire "
        "and inner wire BOTH crossing the cylinder seam at u=0; CIRCLE geometry is "
        "shared between corresponding seam-crossing edges of both wires; "
        "ShapeFix_Face::FixWiresTwoCoincEdges treats seam edges differently and "
        "misses the coincidence across wires; defect IS on live CLOSED_SHELL traversal path"
    ),
)

R  = 5.0   # cylinder radius
H  = 2.0   # cylinder height (v range 0..2)

# Cylindrical surface: radius=5, axis Z, origin at (0,0,0)
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# Seam circle at z=0 (base circle of cylinder, parametrically at v=0).
# This CIRCLE entity is shared across both wires' seam-crossing edges.
seam_ax0_origin = f.cartesian_point((0.0, 0.0, 0.0))
seam_ax0_zdir   = f.direction((0.0, 0.0, 1.0))
seam_ax0_xdir   = f.direction((1.0, 0.0, 0.0))
seam_ax0_plc    = f.axis2_placement_3d(seam_ax0_origin, seam_ax0_zdir, seam_ax0_xdir)
shared_circle   = f.circle(seam_ax0_plc, R)

# Points on the cylinder surface: seam at x=(R,0), opposite at x=(-R,0)
# z=0 ring
p_A0 = f.cartesian_point(( R, 0.0, 0.0))   # seam at z=0
p_B0 = f.cartesian_point((-R, 0.0, 0.0))   # opposite at z=0
# z=H ring
p_AH = f.cartesian_point(( R, 0.0, H))    # seam at z=H
p_BH = f.cartesian_point((-R, 0.0, H))    # opposite at z=H

v_A0 = f.vertex_point(p_A0)
v_B0 = f.vertex_point(p_B0)
v_AH = f.vertex_point(p_AH)
v_BH = f.vertex_point(p_BH)

# Vertical (axial) edge at seam u=0: A0 → AH
e_vert_seam = f.edge_curve(v_A0, v_AH,
    f.line(p_A0, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
# Vertical edge opposite: B0 → BH
e_vert_opp = f.edge_curve(v_B0, v_BH,
    f.line(p_B0, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# Arc edge at z=0 from A0 to B0 (half circle, shared circle)
e_arc_bot_fwd = f.edge_curve(v_A0, v_B0, shared_circle)
# Arc at z=H (use a separate circle at z=H)
top_ax_origin = f.cartesian_point((0.0, 0.0, H))
top_ax_plc    = f.axis2_placement_3d(top_ax_origin, f.direction((0.0, 0.0, 1.0)),
                                       f.direction((1.0, 0.0, 0.0)))
top_circle    = f.circle(top_ax_plc, R)
e_arc_top     = f.edge_curve(v_AH, v_BH, top_circle)

# ── Outer wire loop: A0 → arc_bot → B0 → vert_opp → BH → arc_top_rev → AH → vert_seam_rev ──
# Shape: A0 → B0 (arc fwd) → BH (vert) → AH (arc back) → A0 (vert back)
outer_loop = f.edge_loop([
    f.oriented_edge(e_arc_bot_fwd, True),    # A0 → B0 along arc
    f.oriented_edge(e_vert_opp,    True),    # B0 → BH along seam opp
    f.oriented_edge(e_arc_top,     False),   # BH → AH (arc reversed: AH→BH, so False)
    f.oriented_edge(e_vert_seam,   False),   # AH → A0 (vert reversed: A0→AH, so False)
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner wire: DUPLICATE seam crossing — reuses shared_circle (the defect) ──
# Second set of vertices (coincident positions, fresh entity IDs)
p_A0b = f.cartesian_point(( R, 0.0, 0.0))
p_B0b = f.cartesian_point((-R, 0.0, 0.0))
p_AHb = f.cartesian_point(( R, 0.0, H))
p_BHb = f.cartesian_point((-R, 0.0, H))

v_A0b = f.vertex_point(p_A0b)
v_B0b = f.vertex_point(p_B0b)
v_AHb = f.vertex_point(p_AHb)
v_BHb = f.vertex_point(p_BHb)

e_vert_seam_b = f.edge_curve(v_A0b, v_AHb,
    f.line(p_A0b, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
e_vert_opp_b  = f.edge_curve(v_B0b, v_BHb,
    f.line(p_B0b, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
# THE DEFECT: inner wire reuses shared_circle for its bottom arc edge
e_arc_bot_b   = f.edge_curve(v_A0b, v_B0b, shared_circle)   # shared circle entity
top_circle_b  = f.circle(
    f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, H)),
                          f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))),
    R)
e_arc_top_b   = f.edge_curve(v_AHb, v_BHb, top_circle_b)

inner_loop = f.edge_loop([
    f.oriented_edge(e_arc_bot_b,   True),
    f.oriented_edge(e_vert_opp_b,  True),
    f.oriented_edge(e_arc_top_b,   False),
    f.oriented_edge(e_vert_seam_b, False),
])
inner_fb = f.face_bound(inner_loop)   # inner wire (not outer)

# Cylindrical face with both wires
cyl_face = f.advanced_face([outer_fob, inner_fb], cyl_surf)

# ── Cap: flat rectangular face to produce a valid solid ──────────────────────
# Plane at z=0: a 10×2 rectangle offset from the cylinder
cap_orig = f.cartesian_point((R, 0.0, 0.0))
p_c0 = f.cartesian_point(( R, 0.0, 0.0))
p_c1 = f.cartesian_point(( R, 2.0, 0.0))
p_c2 = f.cartesian_point((-R, 2.0, 0.0))
p_c3 = f.cartesian_point((-R, 0.0, 0.0))

v_c0 = f.vertex_point(p_c0)
v_c1 = f.vertex_point(p_c1)
v_c2 = f.vertex_point(p_c2)
v_c3 = f.vertex_point(p_c3)

e_c01 = f.edge_curve(v_c0, v_c1, f.line(p_c0, f.vector(f.direction((0.0, 1.0, 0.0)), 2.0)))
e_c12 = f.edge_curve(v_c1, v_c2, f.line(p_c1, f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0 * R)))
e_c23 = f.edge_curve(v_c2, v_c3, f.line(p_c2, f.vector(f.direction((0.0, -1.0, 0.0)), 2.0)))
e_c30 = f.edge_curve(v_c3, v_c0, f.line(p_c3, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0 * R)))

cap_loop = f.edge_loop([
    f.oriented_edge(e_c01, True),
    f.oriented_edge(e_c12, True),
    f.oriented_edge(e_c23, True),
    f.oriented_edge(e_c30, True),
])
cap_plc  = f.axis2_placement_3d(cap_orig, f.direction((0.0, 0.0, -1.0)),
                                  f.direction((1.0, 0.0, 0.0)))
cap_face = f.advanced_face([f.face_outer_bound(cap_loop)], f.plane(cap_plc))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([cyl_face, cap_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa100.stp")
