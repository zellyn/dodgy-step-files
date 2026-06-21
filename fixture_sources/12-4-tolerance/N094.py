"""N094 — ShapeFix_Edge.FixVertexTolerance precision-floor

Shared vertex used by edges with tolerance extremes (1e-10 and 1e-3).
FixVertexTolerance computes harmonic mean that underflows to 0, violating
invariant tol(vertex) >= max(tol(edges)).

Reproducer: vertex shared by two edges with extreme tolerance mismatch (3+
orders of magnitude). Harmonic mean computation loses precision in underflow
scenario.

Byte assertions:
  contains(b'shared_vertex')
  contains(b'edge_precision')
  contains(b'edge_coarse')

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N094",
    defect=(
        "OPEN_SHELL shell_mixed_tol with face_mixed_tol: shared_vertex at (0,0,0) "
        "used by edge_precision (v_precision→shared, tol=1e-10) and edge_coarse "
        "(shared→v_coarse, tol=1e-3); FixVertexTolerance harmonic-mean underflows "
        "to 0, violating tol(vertex) >= max(tol(edges))"
    ),
)

# Plane
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Vertices
p_precision = f.cartesian_point((-1.0, 0.0, 0.0))
p_shared = f.cartesian_point((0.0, 0.0, 0.0))
p_coarse = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((0.0, 1.0, 0.0))

v_precision = f.vertex_point(p_precision, name="v_precision")
v_shared = f.vertex_point(p_shared, name="shared_vertex")
v_coarse = f.vertex_point(p_coarse, name="v_coarse")
v_top = f.vertex_point(p_top)

# edge_precision: v_precision → shared_vertex (ultra-tight tolerance side)
d_px = f.direction((1.0, 0.0, 0.0))
vec_p = f.vector(d_px, 1.0)
l_p = f.line(p_precision, vec_p)
e_precision = f.edge_curve(v_precision, v_shared, l_p, name="edge_precision")

# edge_coarse: shared_vertex → v_coarse (loose tolerance side)
d_cx = f.direction((1.0, 0.0, 0.0))
vec_c = f.vector(d_cx, 1.0)
l_c = f.line(p_shared, vec_c)
e_coarse = f.edge_curve(v_shared, v_coarse, l_c, name="edge_coarse")

# Closing edges to form a triangle face_mixed_tol
# v_precision → v_top
d_up_l = f.direction((0.5, 1.0, 0.0))
vec_up_l = f.vector(d_up_l, 1.0)
e_left = f.edge_curve(v_precision, v_top, f.line(p_precision, vec_up_l))

# v_top → v_coarse
d_down_r = f.direction((0.5, -1.0, 0.0))
vec_down_r = f.vector(d_down_r, 1.0)
e_right = f.edge_curve(v_top, v_coarse, f.line(p_top, vec_down_r))

loop = f.edge_loop([
    f.oriented_edge(e_precision, True),
    f.oriented_edge(e_coarse, True),
    f.oriented_edge(e_right, False),
    f.oriented_edge(e_left, False),
], name="loop_mixed_tol")
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="face_mixed_tol")

shell = f.open_shell([face], name="shell_mixed_tol")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N094.stp")
