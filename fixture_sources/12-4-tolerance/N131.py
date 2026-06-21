"""N131 — ShapeAnalysis_ShapeTolerance vertex range inversion

InTolerance(shape, min, max, TopAbs_VERTEX) uses inverted comparison
(tol >= valmax) instead of (tol <= valmax), returning vertices outside
[min, max] range instead of inside. Contradicts FACE/EDGE filtering logic.

Reproducer: shape with v_in_range (tol=0.0015, within [0.001, 0.002]) and
v_out_range (tol=0.005, outside range). InTolerance with inverted bound
returns v_out_range when it should return v_in_range.

Byte assertions:
  contains(b'v_in_range')
  contains(b'v_out_range')
  contains(b'ec1')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N131",
    defect=(
        "CLOSED_SHELL with face containing v_in_range (tol=0.0015) and v_out_range "
        "(tol=0.005); InTolerance(shape,0.001,0.002,VERTEX) uses inverted bound — "
        "returns v_out_range instead of v_in_range, contradicting FACE/EDGE logic"
    ),
)

# Two vertices at different tolerance levels
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v_in_range = f.vertex_point(p0, name="v_in_range")   # would have tol=0.0015
v_out_range = f.vertex_point(p1, name="v_out_range") # would have tol=0.005
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d_x = f.direction((1.0, 0.0, 0.0))
ec1 = f.edge_curve(v_in_range, v_out_range, f.line(p0, f.vector(d_x, 1.0)), name="ec1")
e_up   = f.edge_curve(v_out_range, v2, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v3, v_in_range, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(ec1, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N131.stp")
