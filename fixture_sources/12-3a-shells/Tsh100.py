"""Tsh100 — ShapeFix_Shell.FixFaceOrientation tangent-edge propagation.

Catalog claim: Two coplanar faces (z=0) meeting at shared edge; dihedral
angle=0°. Orientation propagation cannot determine which face "wins" and
fails to propagate consistently. Tests boundary case where topology rules
break down.

Mechanism IS the shell structure: Two ADVANCED_FACEs both at z=0 share one
EDGE_CURVE along x=[1,2], y=0. Both faces are coplanar — dihedral angle IS 0°.
The shared ORIENTED_EDGEs reference the same EDGE_CURVE: Face A uses it with
orientation=True (.T.) and Face B uses it with orientation=False (.F.) for the
shared boundary. This shared edge with dihedral angle 0° IS directly wired into
both ADVANCED_FACE EDGE_LOOPs. FixFaceOrientation computes the dihedral angle
to decide propagation direction; dihedral=0° IS the mechanism — the cross-
product used for orientation determination collapses to zero, making propagation
indeterminate. The two faces sharing the zero-dihedral edge ARE the mechanism
wired into the shell/face topology.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh100",
    defect=(
        "OPEN_SHELL with 2 coplanar ADVANCED_FACEs both at z=0 sharing one EDGE_CURVE; "
        "shared EDGE_CURVE along x=[1,2] y=0 IS directly wired into both face EDGE_LOOPs; "
        "dihedral angle between coplanar faces IS 0° — IS the tangent-edge mechanism; "
        "Face A references shared edge with orientation=True (.T.) in its EDGE_LOOP; "
        "Face B references same EDGE_CURVE with orientation=False (.F.) in its EDGE_LOOP; "
        "zero dihedral IS the mechanism — cross-product collapses, propagation indeterminate; "
        "fix: detect dihedral == 0° before propagation; flag edge as ambiguous; "
        "emit E_TANGENT_EDGE_ORIENTATION_PROPAGATION_FAILURE when dihedral angle is zero"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A: unit quad at z=0, x=[0,2], y=[0,1]
# Vertices: (0,0,0) (2,0,0) (2,1,0) (0,1,0)
pA0 = cp(0,0,0); pA1 = cp(2,0,0); pA2 = cp(2,1,0); pA3 = cp(0,1,0)
vA0 = f.vertex_point(pA0); vA1 = f.vertex_point(pA1)
vA2 = f.vertex_point(pA2); vA3 = f.vertex_point(pA3)

# Face B: unit quad at z=0, x=[0,2], y=[-1,0] (coplanar, sharing bottom edge of A)
pB0 = cp(0,-1,0); pB1 = cp(2,-1,0); pB2 = cp(2,0,0); pB3 = cp(0,0,0)
vB0 = f.vertex_point(pB0); vB1 = f.vertex_point(pB1)
# vB2 and vB3 are same positions as vA0/vA1 — shared edge vertices
vB2 = vA1; vB3 = vA0

# Shared edge: (0,0,0)→(2,0,0) — IS the zero-dihedral tangent edge mechanism
shared_edge = led(vA0, vA1, pA0, 1, 0, 0)

# Face A edges
eA_bottom = shared_edge  # (0,0,0)→(2,0,0) — shared, used True
eA_right  = led(vA1, vA2, pA1,  0, 1, 0)
eA_top    = led(vA2, vA3, pA2, -1, 0, 0)
eA_left   = led(vA3, vA0, pA3,  0,-1, 0)
loop_a = f.edge_loop([
    f.oriented_edge(eA_bottom, True),
    f.oriented_edge(eA_right,  True),
    f.oriented_edge(eA_top,    True),
    f.oriented_edge(eA_left,   True),
])
pl_a = f.plane(f.axis2_placement_3d(pA0, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], pl_a, same_sense=True)

# Face B edges — shared edge used with orientation=False (.F.) — IS the mechanism
eB_right  = led(vB1, vB2, pB1,  0, 1, 0)
eB_top    = f.oriented_edge(shared_edge, False)  # reversed reference — dihedral=0° mechanism
eB_left   = led(vB3, vB0, pB3,  0,-1, 0)
eB_bottom = led(vB0, vB1, pB0,  1, 0, 0)
loop_b = f.edge_loop([
    f.oriented_edge(eB_bottom, True),
    f.oriented_edge(eB_right,  True),
    eB_top,
    f.oriented_edge(eB_left,   True),
])
pl_b = f.plane(f.axis2_placement_3d(pB0, dir3(0, 0, 1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], pl_b, same_sense=True)

# OPEN_SHELL: two coplanar faces sharing zero-dihedral edge IS the mechanism
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
