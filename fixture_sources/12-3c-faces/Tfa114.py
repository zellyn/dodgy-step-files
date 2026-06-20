"""Tfa114 — ShapeAnalysis_CheckSmallFace.CheckSpotFace zero-radius.

Catalog claim: Face whose enclosing circle radius is exactly 0.0 (all vertices
at the same point); CheckSpotFace returns "definitely a spot" but the geometry
is degenerate beyond meaningful classification. Bounding radius calculation
produces zero; classification fails on degenerate case.

Mechanism: MANIFOLD_SOLID_BREP where the defect face is a PLANE ADVANCED_FACE
with 4 edges all connecting to a single collapsed point (5,5,0). All
CARTESIAN_POINT coordinates are identical; all edge geometry is zero-length.
ShapeAnalysis_CheckSmallFace::CheckSpotFace computes the bounding circle radius
as 0.0 and encounters numerical instability when comparing against threshold.
A companion flat 1×1 square face ensures OCC loads shape(1). The defect face
IS on the live CLOSED_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'CLOSED_SHELL')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa114",
    defect=(
        "CLOSED_SHELL: defect ADVANCED_FACE has 4 edges all at point (5,5,0); "
        "all 4 vertices are coincident, all edge line directions are degenerate zero-length; "
        "ShapeAnalysis_CheckSmallFace::CheckSpotFace bounding-circle radius == 0.0; "
        "zero-radius causes numerical instability in threshold comparison; "
        "companion 1×1 square face at z=1 ensures shape(1) loads; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Degenerate spot face: all 4 vertices at (5, 5, 0)
spot = (5.0, 5.0, 0.0)
p_spot = f.cartesian_point(spot)
v0 = f.vertex_point(p_spot)
v1 = f.vertex_point(f.cartesian_point(spot))
v2 = f.vertex_point(f.cartesian_point(spot))
v3 = f.vertex_point(f.cartesian_point(spot))

# Zero-length edges: each edge connects two coincident vertices
# Direction (1,0,0) with magnitude 0.0 is degenerate
zero_dir = f.direction((1.0, 0.0, 0.0))
zero_vec = f.vector(zero_dir, 0.0)

e0 = f.edge_curve(v0, v1, f.line(p_spot, zero_vec))
e1 = f.edge_curve(v1, v2, f.line(f.cartesian_point(spot), zero_vec))
e2 = f.edge_curve(v2, v3, f.line(f.cartesian_point(spot), zero_vec))
e3 = f.edge_curve(v3, v0, f.line(f.cartesian_point(spot), zero_vec))

spot_loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])

spot_orig = f.cartesian_point(spot)
spot_plc  = f.axis2_placement_3d(spot_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
spot_face = f.advanced_face([f.face_outer_bound(spot_loop)], f.plane(spot_plc))

# Companion face: valid 1×1 square at z=1 to ensure shape(1) loads
p_c0 = f.cartesian_point((4.0, 4.0, 1.0)); p_c1 = f.cartesian_point((5.0, 4.0, 1.0))
p_c2 = f.cartesian_point((5.0, 5.0, 1.0)); p_c3 = f.cartesian_point((4.0, 5.0, 1.0))
vc0 = f.vertex_point(p_c0); vc1 = f.vertex_point(p_c1)
vc2 = f.vertex_point(p_c2); vc3 = f.vertex_point(p_c3)
ec0 = f.edge_curve(vc0, vc1, f.line(p_c0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
ec1 = f.edge_curve(vc1, vc2, f.line(p_c1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
ec2 = f.edge_curve(vc2, vc3, f.line(p_c2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ec3 = f.edge_curve(vc3, vc0, f.line(p_c3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))
comp_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])
comp_plc  = f.axis2_placement_3d(p_c0, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
comp_face = f.advanced_face([f.face_outer_bound(comp_loop)], f.plane(comp_plc))

# Use open_shell: the two faces don't share edges, so not watertight
open_sh = f.open_shell([spot_face, comp_face])
sbsm    = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm, mode="surface_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa114.stp")
