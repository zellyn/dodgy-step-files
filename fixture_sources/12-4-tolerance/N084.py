"""N084 — BRepLib.UpdateInnerTolerances degenerate-edge postcondition

Degenerate edge check skips tolerance update; vertex distances still computed
and updated post-loop. Loop exits on degeneracy but vertices V1, V2 at lines
85-98 still receive UpdateVertex calls with undefined End1/End2 values.

Fixture: Degenerate edge (zero-length 3D curve) co-located with normal edge;
postcondition assumes edge was updated, but UpdateVertex is called on undefined
curve endpoints.

Byte assertions:
  contains(b'V_degen')
  contains(b'edge_degen')
  count_entity_def(b'EDGE_CURVE') >= 2

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N084",
    defect=(
        "degenerate edge edge_degen with zero-length curve (V_degen→V_degen); "
        "UpdateInnerTolerances exits early on degeneracy but still calls "
        "UpdateVertex with undefined End1/End2 from the skipped curve"
    ),
)

# Degenerate vertex at the degenerate edge location
p_degen = f.cartesian_point((0.5, 0.5, 0.0), name="p_degen")
p1 = f.cartesian_point((0.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 0.0, 0.0))

v_degen = f.vertex_point(p_degen, name="V_degen")
v1 = f.vertex_point(p1, name="V1")
v2 = f.vertex_point(p2, name="V2")

# Degenerate edge: zero-length 3D curve (vector magnitude = 0)
d_x = f.direction((1.0, 0.0, 0.0))
vec_degen = f.vector(d_x, 0.0)  # zero-length
l_degen = f.line(p_degen, vec_degen)
e_degen = f.edge_curve(v_degen, v_degen, l_degen, name="edge_degen")

# Normal edge from v1 to v2
vec_norm = f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
l_norm = f.line(p1, vec_norm)
e_norm = f.edge_curve(v1, v2, l_norm, name="edge_normal")

# Close the loop to form a valid face
p3 = f.cartesian_point((1.0, 1.0, 0.0))
p4 = f.cartesian_point((0.0, 1.0, 0.0))
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)

e_up   = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v3, v4, f.line(p3, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v4, v1, f.line(p4, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e_norm, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0))
plc = f.axis2_placement_3d(p1, d_z, f.direction((1.0, 0.0, 0.0)))
plane = f.plane(plc)
face = f.advanced_face([fob], plane)
shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N084.stp")
