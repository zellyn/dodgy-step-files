"""N102 — ShapeAnalysis_Edge.CheckOverlapping multi-curve three-way overlap

Three edges share identical 3D LINE geometry. CheckOverlapping designed for
pairwise comparison; three-way case produces inconsistent verdicts
(edge 1-2 vs 2-3 vs 1-3). Defect: voting inconsistency in overlap
classification.

Reproducer: three EDGE_CURVE entities referencing the same LINE geometry
from v1 to v2. Three-way pairwise check yields contradictory overlap results.

Byte assertions:
  contains(b'edge1')
  contains(b'edge2')
  contains(b'edge3')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N102",
    defect=(
        "CLOSED_SHELL shell with face1 containing edge1, edge2, edge3 all referencing "
        "identical LINE from v1 to v2; CheckOverlapping pairwise logic produces "
        "inconsistent three-way verdicts — voting inconsistency in overlap classification"
    ),
)

# Three edges with identical geometry
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))

v1 = f.vertex_point(p0, name="v1")
v2 = f.vertex_point(p1, name="v2")

# Same direction/line reused — three edges on same geometry
d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 1.0)
l_shared = f.line(p0, vec_x)

e1 = f.edge_curve(v1, v2, l_shared, name="edge1")
e2 = f.edge_curve(v1, v2, l_shared, name="edge2")
e3 = f.edge_curve(v1, v2, l_shared, name="edge3")

# Build a face using only e1 in the loop (e2, e3 are orphan references)
# Close with a square
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v3 = f.vertex_point(p2)
v4 = f.vertex_point(p3)

e_up   = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v4, v1, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
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
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N102.stp")
