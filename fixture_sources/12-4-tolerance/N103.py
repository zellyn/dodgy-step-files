"""N103 — BRepLib.UpdateEdgeTol negative-coverage sparse sampling

Edge tolerance recomputed via interpolation across sampled sub-regions. Sparse
sampling leaves gaps with zero coverage; interpolation breaks down, produces
NaN or infinite tolerance in unsampled zone. Defect: interpolation instability
on sparse sample sets.

Reproducer: two-segment edge loop on a face (edge1 from v1 to v2, edge2 from
v2 to v3) with very short segment edge2 likely to be under-sampled.

Byte assertions:
  contains(b'edge1')
  contains(b'edge2')
  contains(b'v1')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N103",
    defect=(
        "CLOSED_SHELL shell with face1 containing edge1 (v1→v2) and edge2 (v2→v3); "
        "sparse sampling of short edge2 leaves unsampled zone; UpdateEdgeTol "
        "interpolation breaks down to NaN/infinite tolerance in gap"
    ),
)

# Two-segment edge loop: long edge1 + very short edge2
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 0.001, 0.0))  # very short segment

v1 = f.vertex_point(p0, name="v1")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2, name="v3")

d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 10.0)
l1 = f.line(p0, vec_x)
e1 = f.edge_curve(v1, v2, l1, name="edge1")

d_y = f.direction((0.0, 1.0, 0.0))
vec_y = f.vector(d_y, 0.001)
l2 = f.line(p1, vec_y)
e2 = f.edge_curve(v2, v3, l2, name="edge2")

# Close the loop back to v1
p3 = f.cartesian_point((0.0, 0.001, 0.0))
v4 = f.vertex_point(p3)
e3 = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
e4 = f.edge_curve(v4, v1, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 0.001)))

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e4, True),
], name="loop")
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane, name="face1")

shell = f.closed_shell([face], name="shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N103.stp")
