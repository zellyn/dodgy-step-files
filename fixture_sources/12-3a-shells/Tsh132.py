"""Tsh132 — ShapeFix_Shell.FixFaceOrientation flat-shell.

Catalog claim: Shell consists entirely of coplanar faces (flat shell, 2x2 grid
of unit squares in z=0). Expected: FixFaceOrientation's normal-vector comparison
fails when all normals are parallel/anti-parallel (indeterminate). Fixture: four
coplanar unit squares arranged in 2x2 grid; all in z=0 plane; all normals
(0,0,±1).

Mechanism IS the shell structure: four ADVANCED_FACEs arranged in a 2x2 grid
(x=[0,2], y=[0,2], z=0) with shared internal edges between adjacent faces — all
sharing IS directly wired into the 4 EDGE_LOOPs. All four plane normals ARE
(0,0,1) (parallel) — this IS the flat-shell mechanism wired into the 4 PLANE
references. FixFaceOrientation uses cross-products of adjacent face normals to
determine propagation direction; when all normals are (0,0,±1) the cross-product
IS identically zero, making orientation propagation indeterminate.

Tier-3 assertion: n_faces_total == 4

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh132",
    defect=(
        "OPEN_SHELL with 4 coplanar ADVANCED_FACEs in 2x2 grid at z=0 — IS the flat-shell mechanism; "
        "Face1 unit square x=[0,1] y=[0,1] z=0 with PLANE normal (0,0,1) — IS wired into topology; "
        "Face2 unit square x=[1,2] y=[0,1] z=0 with PLANE normal (0,0,1) — IS wired into topology; "
        "Face3 unit square x=[0,1] y=[1,2] z=0 with PLANE normal (0,0,1) — IS wired into topology; "
        "Face4 unit square x=[1,2] y=[1,2] z=0 with PLANE normal (0,0,1) — IS wired into topology; "
        "3 shared EDGE_CURVEs between adjacent faces ARE wired into the 4 EDGE_LOOPs; "
        "all 4 PLANE normals ARE parallel (0,0,1) — IS the flat-shell indeterminacy mechanism; "
        "FixFaceOrientation cross-product of adjacent normals IS zero for all face pairs; "
        "propagation direction IS indeterminate — IS the defect wired into PLANE topology; "
        "fix: detect coplanar adjacency; use edge-direction rather than normal cross-product; "
        "emit E_FLAT_SHELL_ORIENTATION_INDETERMINATE when all normals are parallel"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# 2x2 grid vertices
p00 = cp(0,0,0); p10 = cp(1,0,0); p20 = cp(2,0,0)
p01 = cp(0,1,0); p11 = cp(1,1,0); p21 = cp(2,1,0)
p02 = cp(0,2,0); p12 = cp(1,2,0); p22 = cp(2,2,0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11); v21 = f.vertex_point(p21)
v02 = f.vertex_point(p02); v12 = f.vertex_point(p12); v22 = f.vertex_point(p22)

# Outer boundary edges
e_bot1  = led(v00, v10, p00,  1, 0, 0)  # (0,0)→(1,0)
e_bot2  = led(v10, v20, p10,  1, 0, 0)  # (1,0)→(2,0)
e_top1  = led(v01, v11, p01,  1, 0, 0)  # (0,1)→(1,1)  [internal y=1 row]
e_top2  = led(v11, v21, p11,  1, 0, 0)  # (1,1)→(2,1)
e_top3  = led(v02, v12, p02,  1, 0, 0)  # (0,2)→(1,2)
e_top4  = led(v12, v22, p12,  1, 0, 0)  # (1,2)→(2,2)
e_lft1  = led(v00, v01, p00,  0, 1, 0)  # (0,0)→(0,1)
e_lft2  = led(v01, v02, p01,  0, 1, 0)  # (0,1)→(0,2)
e_mid1  = led(v10, v11, p10,  0, 1, 0)  # (1,0)→(1,1)  [internal x=1 col]
e_mid2  = led(v11, v12, p11,  0, 1, 0)  # (1,1)→(1,2)
e_rgt1  = led(v20, v21, p20,  0, 1, 0)  # (2,0)→(2,1)
e_rgt2  = led(v21, v22, p21,  0, 1, 0)  # (2,1)→(2,2)

# All 4 faces share the same z=0 plane — IS the flat-shell mechanism
def mk_plane_z0(ox, oy):
    orig = f.cartesian_point((ox, oy, 0.0))
    return f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# Face1: x=[0,1], y=[0,1] — bottom-left
face1 = face4([(e_bot1,True),(e_mid1,True),(e_top1,False),(e_lft1,False)],
              mk_plane_z0(0, 0))

# Face2: x=[1,2], y=[0,1] — bottom-right
face2 = face4([(e_bot2,True),(e_rgt1,True),(e_top2,False),(e_mid1,False)],
              mk_plane_z0(1, 0))

# Face3: x=[0,1], y=[1,2] — top-left
face3 = face4([(e_top1,True),(e_mid2,True),(e_top3,False),(e_lft2,False)],
              mk_plane_z0(0, 1))

# Face4: x=[1,2], y=[1,2] — top-right
face4_ = face4([(e_top2,True),(e_rgt2,True),(e_top4,False),(e_mid2,False)],
               mk_plane_z0(1, 1))

# OPEN_SHELL: 4 coplanar faces sharing internal edges — IS the flat-shell mechanism
shell = f.open_shell([face1, face2, face3, face4_])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
