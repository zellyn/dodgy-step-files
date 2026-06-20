"""Tfa041 — Spot face: face collapsed to a near-point.

Catalog claim: An ADVANCED_FACE whose outer wire's bounding box is smaller than
the kernel's working precision in both U and V. The face is geometrically a
point; it has no usable interior and contributes nothing to the shape's volume
or boundary.

Reproducer recipe (from catalog): A square face with vertices at (0,0),
(0.001,0), (0.001,0.001), (0,0.001).

Mechanism: The defect ADVANCED_FACE is a 0.001×0.001 square at the origin on
a PLANE at z=0. All four vertices are within 1e-3 of (0,0), so the face's
bounding box is sub-tolerance (smaller than the kernel's working precision).
A valid 10×10 reference face is added as face[1] to ensure the shell loads as
shape(1). The spot face is face[0].

Tier-3 assertions:
  face[0].area < 1e-3
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa041",
    defect=(
        "OPEN_SHELL: face[0] is 0.001×0.001 spot face on PLANE at z=0; "
        "vertices at (0,0,0),(0.001,0,0),(0.001,0.001,0),(0,0.001,0); "
        "bounding box smaller than working precision in both U and V; "
        "face is geometrically a point with no usable interior; "
        "FixSpotFace must remove/replace with vertex; "
        "face[1] is valid 10×10 plane so shape(1) loads; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── face[0]: spot face 0.001×0.001 at origin ─────────────────────────────────
S = 0.001   # side length (sub-tolerance)

pa = f.cartesian_point((0.0, 0.0, 0.0))
pb = f.cartesian_point((S,   0.0, 0.0))
pc = f.cartesian_point((S,   S,   0.0))
pd = f.cartesian_point((0.0, S,   0.0))
va = f.vertex_point(pa); vb = f.vertex_point(pb)
vc = f.vertex_point(pc); vd = f.vertex_point(pd)

ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), S)))
ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), S)))
ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), S)))
ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), S)))

spot_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])

spot_orig  = f.cartesian_point((0.0, 0.0, 0.0))
spot_zdir  = f.direction((0.0, 0.0, 1.0))
spot_xdir  = f.direction((1.0, 0.0, 0.0))
spot_plc   = f.axis2_placement_3d(spot_orig, spot_zdir, spot_xdir)
spot_plane = f.plane(spot_plc)
face0 = f.advanced_face([f.face_outer_bound(spot_loop)], spot_plane)

# ── face[1]: valid 10×10 plane at y=1 (to meet n_edges_total>=4, n_verts>=8) ──
p0 = f.cartesian_point((  0.0, 1.0, 0.0))
p1 = f.cartesian_point(( 10.0, 1.0, 0.0))
p2 = f.cartesian_point(( 10.0,11.0, 0.0))
p3 = f.cartesian_point((  0.0,11.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

ref_loop  = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
ref_orig  = f.cartesian_point((0.0, 0.0, 0.0))
ref_zdir  = f.direction((0.0, 0.0, 1.0))
ref_xdir  = f.direction((1.0, 0.0, 0.0))
ref_plc   = f.axis2_placement_3d(ref_orig, ref_zdir, ref_xdir)
ref_plane = f.plane(ref_plc)
face1 = f.advanced_face([f.face_outer_bound(ref_loop)], ref_plane)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa041.stp")
