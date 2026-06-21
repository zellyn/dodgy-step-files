"""N109 — ShapeFix_ShapeTolerance.SetTolerance with-cyclic-reference

Shape with cyclic reference in sub-shape graph; SetTolerance recursion lacks
cycle detection and loops indefinitely. Closed rectangular face referenced
twice in shell structure to create circular topology. Tests recursion
termination condition.

Byte assertions:
  contains(b'face1')
  contains(b'shell_inner')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N109",
    defect=(
        "CLOSED_SHELL shell_inner with face1; SHELL_BASED_SURFACE_MODEL referenced "
        "twice as cyclic_sbsm and sbsm; SetTolerance recursion lacks cycle detection "
        "and loops indefinitely on the circular sub-shape reference"
    ),
)

# 1×1 rectangular face
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v1 = f.vertex_point(p0)
v2 = f.vertex_point(p1)
v3 = f.vertex_point(p2)
v4 = f.vertex_point(p3)

e1 = f.edge_curve(v1, v2, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="e1")
e2 = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)), name="e2")
e3 = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)), name="e3")
e4 = f.edge_curve(v4, v1, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)), name="e4")

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, False),
    f.oriented_edge(e4, False),
], name="loop1")
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane, name="face1")

shell = f.closed_shell([face], name="shell_inner")
sbsm = f.shell_based_surface_model([shell])
# Emit an additional SBSM referencing the same shell (cyclic reference trigger)
cyclic_sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('cyclic_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm, uncertainty=1.0E-3)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N109.stp")
