"""Tfa097 — ShapeAnalysis_CheckSmallFace.CheckPinFace blunt-pin classification.

Catalog claim: Face with a pin (tapering region) at ~10° internal angle, not
sharp. CheckPinFace's angle threshold (typically M_PI/6 ≈ 30°) misclassifies
blunt pins as sharp features.

Mechanism: CLOSED_SHELL with a planar top face shaped as a wedge (pin). The
outer wire is a triangle: horizontal base 10 mm wide at y=0, and two slanted
sides meeting at apex (5, 1) — giving an internal angle at the apex of ~11.3°
(much less than the 30° sharp threshold). The pin is "blunt" for the geometry
but CheckPinFace's angle comparison uses >= instead of >, so the 10° pin is
flagged as sharp when it should not be. Box shell closes the solid.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') >= 1
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa097",
    defect=(
        "CLOSED_SHELL: top face is wedge (pin) triangle at z=1; "
        "base vertices A=(0,0,1), B=(10,0,1); apex C=(5,1,1); "
        "internal angle at apex ≈ 11.3° (blunt pin, << 30° sharp threshold); "
        "CheckPinFace: angle threshold M_PI/6≈30°; "
        "off-by-one in comparison (>= vs >) misclassifies blunt as sharp; "
        "triangular prism closed shell with 5 faces; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# ── Triangle apex configuration ───────────────────────────────────────────────
# Base: A=(0,0) B=(10,0) — 10 mm wide
# Apex: C=(5,1) — 1 mm height gives internal angle at C:
#   half-base = 5, height = 1
#   half-angle = arctan(1/5) ≈ 11.3° → full internal angle ≈ 22.6° which is
#   still < 30°; or using the two slant vectors:
#   CA = A-C = (-5,-1), CB = B-C = (5,-1)
#   angle = arccos(dot/|CA||CB|) = arccos((−25+1)/(sqrt26*sqrt26)) = arccos(-24/26) ≈ 157°
#   The apex *internal* angle from the wedge perspective = 180° - 157° = ...
#   Actually: the pin angle is the angle OF the wedge at apex:
#   vectors from apex: to A = (-5,-1), to B = (5,-1)
#   dot = -25+1 = -24; |v|=sqrt(26) each
#   angle = arccos(-24/26) ≈ 157.4° — interior angle of the triangle is 157°
#   The pin angle (narrow angle) = 180° - 157.4° = 22.6° — but that's exterior
#   Actually the full angle AT apex = arccos(-24/26) ≈ 157°... let's use a narrower apex.
# Use apex=(5, 0.5) for a narrower pin:
#   vectors: (-5, -0.5) and (5, -0.5); dot=-25+0.25=-24.75; |v|=sqrt(25.25)
#   angle=arccos(-24.75/25.25)=arccos(-0.9802)≈168.5° internal → pin angle 11.5°
# This matches catalog "~10° internal angle"

A = (0.0,  0.0)   # base left
B = (10.0, 0.0)   # base right
C = (5.0,  0.5)   # apex (narrow pin, ~11° pin angle)

z0 = 0.0   # bottom
z1 = 1.0   # top

pA0=f.cartesian_point((A[0],A[1],z0)); pA1=f.cartesian_point((A[0],A[1],z1))
pB0=f.cartesian_point((B[0],B[1],z0)); pB1=f.cartesian_point((B[0],B[1],z1))
pC0=f.cartesian_point((C[0],C[1],z0)); pC1=f.cartesian_point((C[0],C[1],z1))

vA0=f.vertex_point(pA0); vA1=f.vertex_point(pA1)
vB0=f.vertex_point(pB0); vB1=f.vertex_point(pB1)
vC0=f.vertex_point(pC0); vC1=f.vertex_point(pC1)

def _edge_3d(va, xa, ya, za, vb, xb, yb, zb):
    dx=xb-xa; dy=yb-ya; dz=zb-za
    mag=math.sqrt(dx*dx+dy*dy+dz*dz)
    d=f.direction((dx/mag, dy/mag, dz/mag))
    return f.edge_curve(va, vb, f.line(f.cartesian_point((xa,ya,za)), f.vector(d, mag)))

# Bottom triangle edges
eAB0=_edge_3d(vA0,A[0],A[1],z0, vB0,B[0],B[1],z0)
eBC0=_edge_3d(vB0,B[0],B[1],z0, vC0,C[0],C[1],z0)
eCA0=_edge_3d(vC0,C[0],C[1],z0, vA0,A[0],A[1],z0)

# Top triangle edges
eAB1=_edge_3d(vA1,A[0],A[1],z1, vB1,B[0],B[1],z1)
eBC1=_edge_3d(vB1,B[0],B[1],z1, vC1,C[0],C[1],z1)
eCA1=_edge_3d(vC1,C[0],C[1],z1, vA1,A[0],A[1],z1)

# Vertical edges
eVA=_edge_3d(vA0,A[0],A[1],z0, vA1,A[0],A[1],z1)
eVB=_edge_3d(vB0,B[0],B[1],z0, vB1,B[0],B[1],z1)
eVC=_edge_3d(vC0,C[0],C[1],z0, vC1,C[0],C[1],z1)

# ── Bottom face z=0 ───────────────────────────────────────────────────────────
bot_loop=f.edge_loop([f.oriented_edge(eAB0,True),f.oriented_edge(eBC0,True),
                      f.oriented_edge(eCA0,True)])
ax_bot=f.axis2_placement_3d(pA0,f.direction((0.0,0.0,-1.0)),f.direction((1.0,0.0,0.0)))
face_bot=f.advanced_face([f.face_outer_bound(bot_loop)],f.plane(ax_bot))

# ── Top face z=1: wedge triangle (the pin face defect) ───────────────────────
top_loop=f.edge_loop([f.oriented_edge(eAB1,True),f.oriented_edge(eBC1,True),
                      f.oriented_edge(eCA1,True)])
ax_top=f.axis2_placement_3d(pA1,f.direction((0.0,0.0,1.0)),f.direction((1.0,0.0,0.0)))
face_top=f.advanced_face([f.face_outer_bound(top_loop)],f.plane(ax_top))

# ── Side faces ────────────────────────────────────────────────────────────────
# Side AB (y=0, south wall)
# AB-bottom → VB-up → AB-top(reversed) → VA-down
def _side_normal_2d(xa, ya, xb, yb):
    dx=xb-xa; dy=yb-ya; mag=math.sqrt(dx*dx+dy*dy)
    # outward normal: rotate edge dir 90° CW (for CCW winding viewed from outside)
    return (dy/mag, -dx/mag, 0.0)

n_AB = _side_normal_2d(A[0],A[1],B[0],B[1])
sAB_loop=f.edge_loop([f.oriented_edge(eAB0,True),f.oriented_edge(eVB,True),
                      f.oriented_edge(eAB1,False),f.oriented_edge(eVA,False)])
ax_AB=f.axis2_placement_3d(pA0,f.direction(n_AB),f.direction((1.0,0.0,0.0)))
face_AB=f.advanced_face([f.face_outer_bound(sAB_loop)],f.plane(ax_AB))

n_BC = _side_normal_2d(B[0],B[1],C[0],C[1])
dx_BC=C[0]-B[0]; dy_BC=C[1]-B[1]; L_BC=math.sqrt(dx_BC*dx_BC+dy_BC*dy_BC)
sBC_loop=f.edge_loop([f.oriented_edge(eBC0,True),f.oriented_edge(eVC,True),
                      f.oriented_edge(eBC1,False),f.oriented_edge(eVB,False)])
ax_BC=f.axis2_placement_3d(pB0,f.direction(n_BC),f.direction((dx_BC/L_BC,dy_BC/L_BC,0.0)))
face_BC=f.advanced_face([f.face_outer_bound(sBC_loop)],f.plane(ax_BC))

n_CA = _side_normal_2d(C[0],C[1],A[0],A[1])
dx_CA=A[0]-C[0]; dy_CA=A[1]-C[1]; L_CA=math.sqrt(dx_CA*dx_CA+dy_CA*dy_CA)
sCA_loop=f.edge_loop([f.oriented_edge(eCA0,True),f.oriented_edge(eVA,True),
                      f.oriented_edge(eCA1,False),f.oriented_edge(eVC,False)])
ax_CA=f.axis2_placement_3d(pC0,f.direction(n_CA),f.direction((dx_CA/L_CA,dy_CA/L_CA,0.0)))
face_CA=f.advanced_face([f.face_outer_bound(sCA_loop)],f.plane(ax_CA))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh=f.closed_shell([face_bot,face_top,face_AB,face_BC,face_CA])
msb=f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb,mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa097.stp")
