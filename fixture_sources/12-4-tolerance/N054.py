"""N054 — ShapeFix_Edge.FixVertexTolerance multi-surface underestimation

When face parameter evaluation fails or face context is null,
CheckVertexTolerance computes vertex tolerance using only single-surface
geometry. For vertices shared between multiple surfaces with different
curvatures, single-surface evaluation underestimates required tolerance.

Reproducer: Edge shared between plane and cylindrical surfaces. Vertex at
intersection. Call FixVertexTolerance with face context=null. Single-surface
(plane only) tolerance computed as 0.001; correct tolerance should be ≥0.002
accounting for both plane and cylinder.

Byte assertions:
  contains(b'v_shared')
  contains(b'face_plane')
  contains(b'face_cylinder')

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(11) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N054",
    defect=(
        "shared vertex v_shared at (5,0,0) on intersection of PLANE z=0 and "
        "CYLINDRICAL_SURFACE r=5; FixVertexTolerance with face context=null "
        "computes from plane only, underestimating tolerance (misses cylinder)"
    ),
)

# Two surfaces: PLANE at z=0, CYLINDRICAL_SURFACE at x=0, r=5
orig = f.cartesian_point((0.0, 0.0, 0.0), name="origin")
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc_plane = f.axis2_placement_3d(orig, zdir, xdir, name="ax3_plane")
plane = f.plane(plc_plane, name="plane_z0")

# Cylindrical surface: axis along Z, radius 5, centered at origin
plc_cyl = f.axis2_placement_3d(orig, zdir, xdir, name="ax3_cyl")
cyl = f.cylindrical_surface(plc_cyl, 5.0, name="cyl_r5")

# Shared vertex at intersection: (5, 0, 0) lies on both plane and cylinder
p_shared = f.cartesian_point((5.0, 0.0, 0.0), name="shared_intersection")
v_shared = f.vertex_point(p_shared, name="v_shared")

# Vertices for plane face triangle: shared + two others in z=0 plane
p_pl2 = f.cartesian_point((0.0, 5.0, 0.0))
v_pl2 = f.vertex_point(p_pl2, name="v_plane_2")
p_pl3 = f.cartesian_point((-5.0, 0.0, 0.0))
v_pl3 = f.vertex_point(p_pl3, name="v_plane_3")

# Edges for plane face (triangle)
import math
sqrt2 = math.sqrt(2.0)
d_pl1 = f.direction((-1.0, 1.0, 0.0))
vec_pl1 = f.vector(d_pl1, 7.071067811865475)
l_pl1 = f.line(p_shared, vec_pl1)
e_pl1 = f.edge_curve(v_shared, v_pl2, l_pl1, name="e_plane_1")

d_pl2 = f.direction((-1.0, -1.0, 0.0))
vec_pl2 = f.vector(d_pl2, 7.071067811865475)
l_pl2 = f.line(p_pl2, vec_pl2)
e_pl2 = f.edge_curve(v_pl2, v_pl3, l_pl2, name="e_plane_2")

d_pl3 = f.direction((1.0, 0.0, 0.0))
vec_pl3 = f.vector(d_pl3, 10.0)
l_pl3 = f.line(p_pl3, vec_pl3)
e_pl3 = f.edge_curve(v_pl3, v_shared, l_pl3, name="e_plane_3")

loop_pl = f.edge_loop([
    f.oriented_edge(e_pl1, True),
    f.oriented_edge(e_pl2, True),
    f.oriented_edge(e_pl3, True),
])
fob_pl = f.face_outer_bound(loop_pl)
face_plane = f.advanced_face([fob_pl], plane, name="face_plane")

# Vertices for cylinder face: shared + two others on cylinder surface
p_cy2 = f.cartesian_point((5.0, 0.0, 2.0))
v_cy2 = f.vertex_point(p_cy2, name="v_cyl_2")
p_cy3 = f.cartesian_point((5.0, 0.0, -2.0))
v_cy3 = f.vertex_point(p_cy3, name="v_cyl_3")

# Edges for cylinder face: shared vertex participates in both faces
d_cy1 = f.direction((0.0, 0.0, 1.0))
vec_cy1 = f.vector(d_cy1, 2.0)
l_cy1 = f.line(p_shared, vec_cy1)
e_cy1 = f.edge_curve(v_shared, v_cy2, l_cy1, name="e_cyl_1")

d_cy2 = f.direction((0.0, 0.0, -1.0))
vec_cy2 = f.vector(d_cy2, 4.0)
l_cy2 = f.line(p_cy2, vec_cy2)
e_cy2 = f.edge_curve(v_cy2, v_cy3, l_cy2, name="e_cyl_2")

d_cy3 = f.direction((0.0, 0.0, 1.0))
vec_cy3 = f.vector(d_cy3, 2.0)
l_cy3 = f.line(p_cy3, vec_cy3)
e_cy3 = f.edge_curve(v_cy3, v_shared, l_cy3, name="e_cyl_3")

loop_cy = f.edge_loop([
    f.oriented_edge(e_cy1, True),
    f.oriented_edge(e_cy2, True),
    f.oriented_edge(e_cy3, True),
])
fob_cy = f.face_outer_bound(loop_cy)
face_cyl = f.advanced_face([fob_cy], cyl, name="face_cylinder")

# Defect: Shared vertex at (5,0,0) lies on intersection of plane and cylinder.
# FixVertexTolerance with face context=null computes tolerance from plane only,
# missing cylinder's contribution.
shell = f.open_shell([face_plane, face_cyl])
sbsm = f.shell_based_surface_model([shell], name="wrap_sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N054.stp")
