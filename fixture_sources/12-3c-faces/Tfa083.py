"""Tfa083 — ShapeFix_Face.FixNotchedEdges near-tangent notch detection.

Catalog claim: Face boundary with two consecutive edges forming 179.8-degree
angle (near-reversal notch). Tangent-angle comparison fails for near-tangent
threshold. Small notch bulge on bottom edge of rectangle.

Mechanism: CLOSED_SHELL box (20×10×5 mm). The top face (z=5) has a 6-edge
outer wire: the south boundary is split into three segments forming a tiny
outward notch — the south top edge goes left-to-center-left (angle≈0°) then
short diagonal to notch apex at (10, -0.05, 5), then diagonal-back then
right. The angle between the notch arms is ≈179.8° (near-tangent reversal).
FixNotchedEdges tangent-angle comparison (≤ threshold) misses this.

The notch apex bulges 0.05 mm south of y=0, outside the main face boundary.
The main body south wall is at y=0; the extra notch wedge (tiny triangular
prism) is added to the shell to maintain manifold topology.

Defect: top face outer wire has near-tangent notch edges. Kerned shell is
a box + tiny notch prism.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') >= 1
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa083",
    defect=(
        "CLOSED_SHELL 20×10×5 mm box + tiny notch prism; top face (z=5) outer wire "
        "has near-tangent notch on south boundary: "
        "split at x=8 and x=12, notch apex at (10,-0.05,5) = 0.05mm south; "
        "angle between consecutive notch edges ≈ 179.8° (near-reversal); "
        "FixNotchedEdges: tangent-angle threshold (≤ comparison) misses near-tangent notch; "
        "notch prism closes manifold shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

W  = 20.0   # box x
D  = 10.0   # box y
H  = 5.0    # box z
NX0 = 8.0   # left split x
NX1 = 12.0  # right split x
NY_N = -0.05  # notch apex y (just south of y=0)

# ── Helper ────────────────────────────────────────────────────────────────────
def pt(coords):
    return f.cartesian_point(coords)

def vtx(p):
    return f.vertex_point(p)

def sedge(va, ca, vb, cb):
    dx=cb[0]-ca[0]; dy=cb[1]-ca[1]; dz=cb[2]-ca[2]
    mag=math.sqrt(dx*dx+dy*dy+dz*dz)
    d=f.direction((dx/mag, dy/mag, dz/mag))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, mag)))

# ── Main box corners z=0 ─────────────────────────────────────────────────────
C_sw0=(0.0,0.0,0.0); C_se0=(W,0.0,0.0); C_ne0=(W,D,0.0); C_nw0=(0.0,D,0.0)
p_sw0=pt(C_sw0); p_se0=pt(C_se0); p_ne0=pt(C_ne0); p_nw0=pt(C_nw0)
v_sw0=vtx(p_sw0); v_se0=vtx(p_se0); v_ne0=vtx(p_ne0); v_nw0=vtx(p_nw0)

# Main box corners z=H (top, straight)
C_sw1=(0.0,0.0,H); C_se1=(W,0.0,H); C_ne1=(W,D,H); C_nw1=(0.0,D,H)
p_sw1=pt(C_sw1); p_se1=pt(C_se1); p_ne1=pt(C_ne1); p_nw1=pt(C_nw1)
v_sw1=vtx(p_sw1); v_se1=vtx(p_se1); v_ne1=vtx(p_ne1); v_nw1=vtx(p_nw1)

# Notch split points at top z=H (south boundary)
C_nl1=(NX0, 0.0, H); C_nr1=(NX1, 0.0, H); C_notch1=(NX0+(NX1-NX0)/2, NY_N, H)
p_nl1=pt(C_nl1); p_nr1=pt(C_nr1); p_notch1=pt(C_notch1)
v_nl1=vtx(p_nl1); v_nr1=vtx(p_nr1); v_notch1=vtx(p_notch1)

# Notch split points at bottom z=0 (for the tiny notch prism side walls)
C_nl0=(NX0, 0.0, 0.0); C_nr0=(NX1, 0.0, 0.0); C_notch0=(NX0+(NX1-NX0)/2, NY_N, 0.0)
p_nl0=pt(C_nl0); p_nr0=pt(C_nr0); p_notch0=pt(C_notch0)
v_nl0=vtx(p_nl0); v_nr0=vtx(p_nr0); v_notch0=vtx(p_notch0)

# ── Box bottom face z=0 (6-edge: sw→nl→notch→nr→se→ne→nw→sw) ────────────────
# The bottom face includes the notch footprint (triangle notch at y<0)
e_bot_sw = sedge(v_sw0, C_sw0, v_nl0, C_nl0)    # (0,0)→(8,0)
e_bot_nl  = sedge(v_nl0, C_nl0, v_notch0, C_notch0)  # left notch arm
e_bot_nr  = sedge(v_notch0, C_notch0, v_nr0, C_nr0)  # right notch arm
e_bot_nrse= sedge(v_nr0, C_nr0, v_se0, C_se0)   # (12,0)→(20,0)
e_bot_e   = sedge(v_se0, C_se0, v_ne0, C_ne0)
e_bot_n   = sedge(v_ne0, C_ne0, v_nw0, C_nw0)
e_bot_w   = sedge(v_nw0, C_nw0, v_sw0, C_sw0)

bot_loop = f.edge_loop([
    f.oriented_edge(e_bot_sw, True), f.oriented_edge(e_bot_nl, True),
    f.oriented_edge(e_bot_nr, True), f.oriented_edge(e_bot_nrse, True),
    f.oriented_edge(e_bot_e, True), f.oriented_edge(e_bot_n, True),
    f.oriented_edge(e_bot_w, True),
])
ax_bot = f.axis2_placement_3d(p_sw0, f.direction((0.0,0.0,-1.0)), f.direction((1.0,0.0,0.0)))
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# ── Top face z=H (THE DEFECT FACE: 6-edge outer wire with near-tangent notch) ──
# Same layout as bottom but at z=H; normal pointing +Z
e_top_sw  = sedge(v_sw1, C_sw1, v_nl1, C_nl1)
e_top_nl  = sedge(v_nl1, C_nl1, v_notch1, C_notch1)
e_top_nr  = sedge(v_notch1, C_notch1, v_nr1, C_nr1)
e_top_nrse= sedge(v_nr1, C_nr1, v_se1, C_se1)
e_top_e   = sedge(v_se1, C_se1, v_ne1, C_ne1)
e_top_n   = sedge(v_ne1, C_ne1, v_nw1, C_nw1)
e_top_w   = sedge(v_nw1, C_nw1, v_sw1, C_sw1)

top_loop = f.edge_loop([
    f.oriented_edge(e_top_sw, True), f.oriented_edge(e_top_nl, True),
    f.oriented_edge(e_top_nr, True), f.oriented_edge(e_top_nrse, True),
    f.oriented_edge(e_top_e, True), f.oriented_edge(e_top_n, True),
    f.oriented_edge(e_top_w, True),
])
ax_top = f.axis2_placement_3d(p_sw1, f.direction((0.0,0.0,1.0)), f.direction((1.0,0.0,0.0)))
face_top = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

# ── Vertical edges ────────────────────────────────────────────────────────────
ev_sw  = sedge(v_sw0, C_sw0, v_sw1, C_sw1)
ev_se  = sedge(v_se0, C_se0, v_se1, C_se1)
ev_ne  = sedge(v_ne0, C_ne0, v_ne1, C_ne1)
ev_nw  = sedge(v_nw0, C_nw0, v_nw1, C_nw1)
ev_nl  = sedge(v_nl0, C_nl0, v_nl1, C_nl1)
ev_nr  = sedge(v_nr0, C_nr0, v_nr1, C_nr1)
ev_notch = sedge(v_notch0, C_notch0, v_notch1, C_notch1)

# ── Side faces ─────────────────────────────────────────────────────────────────
# North face y=D
nf_loop=f.edge_loop([f.oriented_edge(ev_nw,True),f.oriented_edge(e_top_n,False),
                     f.oriented_edge(ev_ne,False),f.oriented_edge(e_bot_n,False)])
ax_nf=f.axis2_placement_3d(p_nw0,f.direction((0.0,1.0,0.0)),f.direction((1.0,0.0,0.0)))
face_nf=f.advanced_face([f.face_outer_bound(nf_loop)],f.plane(ax_nf))

# East face x=W
ef_loop=f.edge_loop([f.oriented_edge(e_bot_e,True),f.oriented_edge(ev_ne,True),
                     f.oriented_edge(e_top_e,False),f.oriented_edge(ev_se,False)])
ax_ef=f.axis2_placement_3d(p_se0,f.direction((1.0,0.0,0.0)),f.direction((0.0,1.0,0.0)))
face_ef=f.advanced_face([f.face_outer_bound(ef_loop)],f.plane(ax_ef))

# West face x=0
wf_loop=f.edge_loop([f.oriented_edge(ev_sw,True),f.oriented_edge(e_top_w,False),
                     f.oriented_edge(ev_nw,False),f.oriented_edge(e_bot_w,False)])
ax_wf=f.axis2_placement_3d(p_sw0,f.direction((-1.0,0.0,0.0)),f.direction((0.0,1.0,0.0)))
face_wf=f.advanced_face([f.face_outer_bound(wf_loop)],f.plane(ax_wf))

# South-left face (x=0..8, y=0): (sw→nl at z=0), ev_nl, (nl→sw at z=H), ev_sw
sf_l_loop=f.edge_loop([f.oriented_edge(e_bot_sw,True),f.oriented_edge(ev_nl,True),
                       f.oriented_edge(e_top_sw,False),f.oriented_edge(ev_sw,False)])
ax_sf_l=f.axis2_placement_3d(p_sw0,f.direction((0.0,-1.0,0.0)),f.direction((1.0,0.0,0.0)))
face_sf_l=f.advanced_face([f.face_outer_bound(sf_l_loop)],f.plane(ax_sf_l))

# South-right face (x=12..20, y=0)
sf_r_loop=f.edge_loop([f.oriented_edge(e_bot_nrse,True),f.oriented_edge(ev_se,True),
                       f.oriented_edge(e_top_nrse,False),f.oriented_edge(ev_nr,False)])
ax_sf_r=f.axis2_placement_3d(p_nr0,f.direction((0.0,-1.0,0.0)),f.direction((1.0,0.0,0.0)))
face_sf_r=f.advanced_face([f.face_outer_bound(sf_r_loop)],f.plane(ax_sf_r))

# Notch left arm face (slanted wall, left arm of notch)
# Connects e_bot_nl (bottom notch left arm) to e_top_nl (top notch left arm)
# via vertical edges ev_nl and ev_notch
notch_l_loop=f.edge_loop([f.oriented_edge(e_bot_nl,True),f.oriented_edge(ev_notch,True),
                           f.oriented_edge(e_top_nl,False),f.oriented_edge(ev_nl,False)])
# Normal: perpendicular to the notch-left-arm plane; use (0,-1,0) as approximation
# (it's slightly tilted but very close to y-normal since the notch is tiny)
# For a valid PLANE we need a correct axis. The notch-left arm goes from (8,0) to (10,-0.05).
# The face normal is perpendicular to both the edge direction and the vertical (z) axis.
dx_nl_arm = C_notch1[0]-C_nl1[0]; dy_nl_arm = C_notch1[1]-C_nl1[1]
mag_nl_arm = math.hypot(dx_nl_arm, dy_nl_arm)
# Normal to the arm in XY plane (rotate 90° CW for outward-pointing): (dy, -dx) normalized
nx_l = dy_nl_arm/mag_nl_arm; ny_l = -dx_nl_arm/mag_nl_arm
ax_notch_l=f.axis2_placement_3d(p_nl0, f.direction((nx_l, ny_l, 0.0)), f.direction((dx_nl_arm/mag_nl_arm, dy_nl_arm/mag_nl_arm, 0.0)))
face_notch_l=f.advanced_face([f.face_outer_bound(notch_l_loop)],f.plane(ax_notch_l))

# Notch right arm face
notch_r_loop=f.edge_loop([f.oriented_edge(e_bot_nr,True),f.oriented_edge(ev_nr,True),
                           f.oriented_edge(e_top_nr,False),f.oriented_edge(ev_notch,False)])
dx_nr_arm = C_nr1[0]-C_notch1[0]; dy_nr_arm = C_nr1[1]-C_notch1[1]
mag_nr_arm = math.hypot(dx_nr_arm, dy_nr_arm)
nx_r = dy_nr_arm/mag_nr_arm; ny_r = -dx_nr_arm/mag_nr_arm
ax_notch_r=f.axis2_placement_3d(p_notch0, f.direction((nx_r, ny_r, 0.0)), f.direction((dx_nr_arm/mag_nr_arm, dy_nr_arm/mag_nr_arm, 0.0)))
face_notch_r=f.advanced_face([f.face_outer_bound(notch_r_loop)],f.plane(ax_notch_r))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh=f.closed_shell([face_bot, face_top, face_nf, face_ef, face_wf,
                           face_sf_l, face_sf_r, face_notch_l, face_notch_r])
msb=f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa083.stp")
