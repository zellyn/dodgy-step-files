"""Ps004 — Left-handed AXIS2_PLACEMENT_3D on a child shape.

Catalog claim: An ADVANCED_BREP_SHAPE_REPRESENTATION includes a child
AXIS2_PLACEMENT_3D whose axis and ref_direction, after Gram-Schmidt
orthonormalization, induce a left-handed basis. AXIS2_PLACEMENT_3D only stores
axis + ref_direction (third is computed); individual unit/orthogonality checks
pass and no diagnostic fires. Tier-3: det(basis) check reveals reflection.

Tier-3: face[3].surface_type == "plane", n_edges_total >= 12,
        face[0].surface_type == "plane", n_vertices_total >= 24
Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps004",
    defect=(
        "AXIS2_PLACEMENT_3D with left-handed basis: axis=(0,0,1), ref_direction=(0,1,0) "
        "yields computed Y_local = axis × ref_direction = (-1,0,0) — reflection not rotation; "
        "individual unit/orthogonality checks pass; no diagnostic fires; "
        "tier-3: det([ref_dir, axis×ref_dir, axis]) = -1 reveals mirror; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

# Tetrahedron vertices
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((0.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 0.0, 1.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)


def eline(pa, pb, dx, dy, dz, length, va, vb):
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pa, v)
    return f.edge_curve(va, vb, ln)


import math
s2 = math.sqrt(2.0) / 2.0
s3 = math.sqrt(3.0) / 3.0

e01 = eline(p0, p1,  1, 0, 0, 1.0, v0, v1)
e02 = eline(p0, p2,  0, 1, 0, 1.0, v0, v2)
e03 = eline(p0, p3,  0, 0, 1, 1.0, v0, v3)
e12 = eline(p1, p2, -s2, s2, 0, math.sqrt(2.0), v1, v2)
e13 = eline(p1, p3, -s2, 0, s2, math.sqrt(2.0), v1, v3)
e23 = eline(p2, p3,  0, -s2, s2, math.sqrt(2.0), v2, v3)


def mk_plane(px, py, pz, ax, ay, az, rx, ry, rz):
    orig = f.cartesian_point((px, py, pz))
    axd  = f.direction((ax, ay, az))
    rxd  = f.direction((rx, ry, rz))
    return f.plane(f.axis2_placement_3d(orig, axd, rxd))


# Bottom face (z=0): normal -Z
pl_bot  = mk_plane(0, 0, 0,  0, 0,-1,  1, 0, 0)
# X=0 face: normal -X
pl_x0   = mk_plane(0, 0, 0, -1, 0, 0,  0, 1, 0)
# Y=0 face: normal -Y
pl_y0   = mk_plane(0, 0, 0,  0,-1, 0,  1, 0, 0)
# Slant face through (1,0,0)(0,1,0)(0,0,1): normal = (1,1,1)/sqrt(3)
pl_slnt = mk_plane(1, 0, 0,  s3, s3, s3,  s2, -s2, 0)


def face3(e1, o1, e2, o2, e3, o3, plane):
    loop = f.edge_loop([
        f.oriented_edge(e1, o1),
        f.oriented_edge(e2, o2),
        f.oriented_edge(e3, o3),
    ])
    fob = f.face_outer_bound(loop)
    return f.advanced_face([fob], plane)


f_bot  = face3(e01, True,  e12, True,  e02, False, pl_bot)
f_x0   = face3(e02, True,  e23, True,  e03, False, pl_x0)
f_y0   = face3(e01, True,  e13, True,  e03, False, pl_y0)
f_slnt = face3(e12, True,  e23, True,  e13, False, pl_slnt)

# Normal right-handed placement (used as the "good" placement in the representation)
good_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)

# THE DEFECT: a left-handed AXIS2_PLACEMENT_3D also listed in the representation
# axis=(0,0,1), ref_direction=(0,1,0) → computed Y_local = (0,0,1)×(0,1,0) = (-1,0,0)
# This is a reflection (det = -1), not a rotation.
lh_plc = f._emit_raw(
    "AXIS2_PLACEMENT_3D('left_handed_placement',"
    f"#{f.cartesian_point((2.0, 0.0, 0.0)).eid},"
    f"#{f.direction((0.0, 0.0, 1.0)).eid},"
    f"#{f.direction((0.0, 1.0, 0.0)).eid})"
)

all_faces = [f_bot, f_slnt, f_x0, f_y0]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('ps004_tetra',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('ps004_tetra_solid',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
