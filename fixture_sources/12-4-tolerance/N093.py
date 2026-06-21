"""N093 — BRepLib.UpdateInnerTolerances on-degenerate-curve

When an edge's 3D curve is degenerate (single point geometry),
UpdateInnerTolerances samples the point repeatedly, computes a spurious
"varies between samples" tolerance instead of recognizing degeneracy.

Reproducer: edge with degenerate_edge (zero-length curve to same vertex),
alongside a normal_edge. UpdateInnerTolerances misidentifies the degenerate
curve's repeated-point sampling as geometric variation.

Byte assertions:
  contains(b'degenerate_edge')
  contains(b'normal_edge')
  count_entity_def(b'EDGE_CURVE') == 2

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N093",
    defect=(
        "OPEN_SHELL face with degenerate_edge (v_degenerate_a→v_degenerate_b, zero length) "
        "and normal_edge; UpdateInnerTolerances samples degenerate curve repeatedly, "
        "computing spurious tolerance instead of recognizing degeneracy"
    ),
)

# Plane
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Degenerate point — both vertices at same location
p_degen = f.cartesian_point((0.5, 0.5, 0.0))
p_degen2 = f.cartesian_point((0.5, 0.5, 0.0))
v_degen_a = f.vertex_point(p_degen, name="v_degenerate_a")
v_degen_b = f.vertex_point(p_degen2, name="v_degenerate_b")

# Degenerate curve: single point (zero-length vector)
d_degen = f.direction((1.0, 0.0, 0.0))
vec_degen = f.vector(d_degen, 0.0)  # zero length
l_degen = f.line(p_degen, vec_degen)
e_degen = f.edge_curve(v_degen_a, v_degen_b, l_degen, name="degenerate_edge")

# Normal edge for reference
p_n0 = f.cartesian_point((0.0, 0.0, 0.0))
p_n1 = f.cartesian_point((1.0, 0.0, 0.0))
v_n0 = f.vertex_point(p_n0, name="v_normal_a")
v_n1 = f.vertex_point(p_n1, name="v_normal_b")

d_n = f.direction((1.0, 0.0, 0.0))
vec_n = f.vector(d_n, 1.0)
l_n = f.line(p_n0, vec_n)
e_norm = f.edge_curve(v_n0, v_n1, l_n, name="normal_edge")

# Complete the face loop
p_tr = f.cartesian_point((1.0, 1.0, 0.0))
p_tl = f.cartesian_point((0.0, 1.0, 0.0))
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

e_up   = f.edge_curve(v_n1, v_tr, f.line(p_n1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v_tl, v_n0, f.line(p_tl, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e_norm, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
], name="wire_with_degen")
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="face_with_degen")

shell = f.open_shell([face], name="shell_with_degen")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N093.stp")
