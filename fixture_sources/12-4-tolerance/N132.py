"""N132 — ShapeFix_ShapeTolerance ambiguous equality bound

LimitTolerance(shape, tmax, tmin) checks (iamax = tmax >= tmin) without
enforcing tmax > tmin. When equality holds, tolerance state becomes
nondeterministic; FACE/EDGE/VERTEX bounds undefined.

Reproducer: shape with v_ambiguous vertex where SetTolerance(shape, 1.0, 1.0,
VERTEX) is called; tmax == tmin equality produces undefined tolerance semantics.

Byte assertions:
  contains(b'v_ambiguous')
  contains(b'ec1')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N132",
    defect=(
        "CLOSED_SHELL with face containing v_ambiguous; LimitTolerance tmax==tmin "
        "equality check (tmax >= tmin) doesn't enforce strict ordering — "
        "nondeterministic tolerance semantics when bounds are equal"
    ),
)

# Rectangular face with ambiguously-bounded vertex
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v_ambiguous = f.vertex_point(p0, name="v_ambiguous")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2)
v4 = f.vertex_point(p3)

ec1 = f.edge_curve(v_ambiguous, v2, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="ec1")
e_up   = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v4, v_ambiguous, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

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
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N132.stp")
