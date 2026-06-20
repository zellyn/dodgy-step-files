"""Tfa042 — Strip face: face whose width is below tolerance.

Catalog claim: A face bounded by two long edges that are confused along their
full length (separated by < tolerance) and two tiny end edges. The face is a
degenerate sliver; typically the residue of a Boolean-cut subtraction along a
feature edge.

Reproducer recipe (from catalog): A face whose outer wire is
(0,0)→(100,0)→(100,1e-3)→(0,1e-3)→(0,0) — aspect ratio 1e5.

Mechanism: The defect ADVANCED_FACE is face[0]: a 100 × 0.001 rectangle on
a PLANE at z=0. Two long edges (length=100) run along X, two short edges
(length=0.001) close the ends. The aspect ratio = 100/0.001 = 1e5 > 1e3.
A valid 10×10 reference face is face[1] to ensure shape(1).

Tier-3 assertions:
  face[0].sliver_aspect_max_min > 1e3
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa042",
    defect=(
        "OPEN_SHELL: face[0] is 100×0.001 strip ADVANCED_FACE on PLANE at z=0; "
        "outer EDGE_LOOP (0,0)→(100,0)→(100,0.001)→(0,0.001); "
        "two long edges (length=100) separated by width=0.001 < tolerance; "
        "aspect ratio = 100/0.001 = 1e5 > 1e3 (strip face criterion); "
        "ShapeFix_FixSmallFace::FixStripFace must merge long edges; "
        "face[1] is valid 10×10 plane to ensure shape(1); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── face[0]: strip face 100×0.001 mm ─────────────────────────────────────────
L = 100.0     # long dimension
W = 0.001     # short dimension (sub-tolerance)

pa = f.cartesian_point((0.0, 0.0, 0.0))
pb = f.cartesian_point((L,   0.0, 0.0))
pc = f.cartesian_point((L,   W,   0.0))
pd = f.cartesian_point((0.0, W,   0.0))
va = f.vertex_point(pa); vb = f.vertex_point(pb)
vc = f.vertex_point(pc); vd = f.vertex_point(pd)

ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

strip_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])

strip_orig  = f.cartesian_point((0.0, 0.0, 0.0))
strip_zdir  = f.direction((0.0, 0.0, 1.0))
strip_xdir  = f.direction((1.0, 0.0, 0.0))
strip_plc   = f.axis2_placement_3d(strip_orig, strip_zdir, strip_xdir)
strip_plane = f.plane(strip_plc)
face0 = f.advanced_face([f.face_outer_bound(strip_loop)], strip_plane)

# ── face[1]: valid 10×10 reference plane at y=1 ───────────────────────────────
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa042.stp")
