"""N104 — ShapeFix_ShapeTolerance.SetTolerance applied-to-frozen-shape

SetTolerance called on shape already marked immutable by downstream API
(e.g., post-validate). Modification executes silently without error; tolerance
state becomes corrupt (cached vs. actual mismatch). Defect: no precondition
validation; silent state mutation.

Reproducer: rectangular face in a CLOSED_SHELL; shape passed to SetTolerance
after a validation pass marks it as frozen. Tolerance mutated silently.

Byte assertions:
  contains(b'e1')
  contains(b'e2')
  contains(b'v1')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N104",
    defect=(
        "CLOSED_SHELL shell with face1 containing e1-e4 and v1-v4; "
        "SetTolerance applied post-validate to immutable (frozen) shape — "
        "silent state mutation, cached vs actual tolerance mismatch"
    ),
)

# 1×1 square face
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v1 = f.vertex_point(p0, name="v1")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2, name="v3")
v4 = f.vertex_point(p3, name="v4")

e1 = f.edge_curve(v1, v2, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="e1")
e2 = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)), name="e2")
e3 = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)), name="e3")
e4 = f.edge_curve(v4, v1, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)), name="e4")

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
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N104.stp")
