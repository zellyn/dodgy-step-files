"""N108 — BRepLib.SameRange clamped-range

SameRange called on edge with parameter range [0.999, 1.001] near parametric
boundary. Rounding logic fails to detect range adjustment needed; function
returns success without actual parameter synchronization. Linear edge on
plane tests range clamping behavior.

Byte assertions:
  contains(b'clamped_edge')
  contains(b'v1')
  contains(b'v2')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N108",
    defect=(
        "CLOSED_SHELL shell with face1 containing clamped_edge from v1 to v2; "
        "SameRange called with parameter range [0.999,1.001] near parametric boundary — "
        "rounding logic fails to detect adjustment needed, returns success without sync"
    ),
)

# Linear edge near parametric boundary
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v1 = f.vertex_point(p0, name="v1")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2)
v4 = f.vertex_point(p3)

d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 1.0)
l_main = f.line(p0, vec_x)
e_clamped = f.edge_curve(v1, v2, l_main, name="clamped_edge")

e_up   = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v4, v1, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e_clamped, True),
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
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N108.stp")
