"""N124 — ShapeFix_ShapeTolerance.SetTolerance recursion-stack-overflow

Deeply nested COMPOUND_SHAPE structure (50+ levels of nesting). SetTolerance
recurses on compound children without stack depth guard; uncontrolled recursion
exhausts stack.

Reproducer: triangular face wrapped in 50 levels of COMPOUND_SHAPE nesting.
SetTolerance recursion has no depth limit and overflows the stack.

Byte assertions:
  contains(b'triangle')
  contains(b'v0')
  contains(b'e01')

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N124",
    defect=(
        "CLOSED_SHELL tri_shell with triangle face (v0, v1, v2; e01, e12, e20) "
        "wrapped in 50 levels of COMPOUND_SHAPE nesting; SetTolerance recursion "
        "lacks depth guard and overflows stack on the nested compound chain"
    ),
)

# Triangle leaf geometry
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((0.0, 10.0, 0.0))

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")

d_01 = f.direction((1.0, 0.0, 0.0))
d_12 = f.direction((-1.0, 1.0, 0.0))
d_20 = f.direction((0.0, -1.0, 0.0))
e01 = f.edge_curve(v0, v1, f.line(p0, f.vector(d_01, 10.0)), name="e01")
e12 = f.edge_curve(v1, v2, f.line(p1, f.vector(d_12, 10.0)), name="e12")
e20 = f.edge_curve(v2, v0, f.line(p2, f.vector(d_20, 10.0)), name="e20")

loop = f.edge_loop([
    f.oriented_edge(e01, True),
    f.oriented_edge(e12, True),
    f.oriented_edge(e20, True),
], name="tri_loop")
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane, name="triangle")

shell = f.closed_shell([face], name="tri_shell")
brep = f.manifold_solid_brep(shell, name="leaf")

# 50 levels of COMPOUND_SHAPE nesting via _emit_raw
compound = brep
for i in range(1, 51):
    compound = f._emit_raw(f"COMPOUND_SHAPE('c{i:02d}',(#{compound.eid}))")

sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N124.stp")
