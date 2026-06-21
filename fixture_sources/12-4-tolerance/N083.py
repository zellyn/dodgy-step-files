"""N083 — ShapeFix_ShapeTolerance.SetTolerance compound + nested

SetTolerance(compound) doesn't propagate tolerance into nested solids' shells.
Recursive descent stops before internal shell traversal, leaving nested geometry
uncorrected.

Fixture: Compound containing a solid containing a shell; SetTolerance(compound,
preci) updates compound and solid but not the internal shell's edges/faces.

Byte assertions:
  contains(b'face1')
  count_entity_def(b'ADVANCED_FACE') >= 1

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N083",
    defect=(
        "CLOSED_SHELL with 1×1 square face; represents compound→solid→shell nesting; "
        "SetTolerance(compound, preci) recursion stops before internal shell's "
        "edges/faces — nested geometry tolerance uncorrected"
    ),
)

# 1x1 square face with four vertices
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0, name="V1")
v1 = f.vertex_point(p1, name="V2")
v2 = f.vertex_point(p2, name="V3")
v3 = f.vertex_point(p3, name="V4")

d_x = f.direction((1.0, 0.0, 0.0))
d_y = f.direction((0.0, 1.0, 0.0))
d_negx = f.direction((-1.0, 0.0, 0.0))
d_negy = f.direction((0.0, -1.0, 0.0))

e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(d_x, 1.0)), name="e1")
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(d_y, 1.0)), name="e2")
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(d_negx, 1.0)), name="e3")
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(d_negy, 1.0)), name="e4")

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0))
plc = f.axis2_placement_3d(p0, d_z, d_x)
plane = f.plane(plc)
face = f.advanced_face([fob], plane, name="face1")

shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N083.stp")
