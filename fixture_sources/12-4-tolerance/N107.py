"""N107 — ShapeAnalysis_ShapeTolerance.AddTolerance with-history

AddTolerance call updates internal history list; list pointer becomes stale
after first update. Closed rectangular face with four edges on plane. Triggers
history tracking mechanism during tolerance accumulation across recursive
shape graph traversal.

Byte assertions:
  contains(b'e1')
  contains(b'face1')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N107",
    defect=(
        "CLOSED_SHELL shell with face1 containing e1-e4; AddTolerance updates "
        "internal history list with stale pointer after first update — tolerance "
        "accumulation via recursive shape graph traversal fails on subsequent calls"
    ),
)

# 1×1 rectangular face — 1e-4 uncertainty context
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
], name="eloop")
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane, name="face1")

shell = f.closed_shell([face], name="shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty=1.0E-4)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N107.stp")
