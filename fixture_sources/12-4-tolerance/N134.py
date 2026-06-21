"""N134 — ShapeFix_ShapeTolerance shared vertex double mutation

LimitTolerance(wire, tmin, tmax) recursively processes V1/V2 per edge without
deduplication. Shared vertices between edges processed multiple times;
tolerance converges nondeterministically.

Reproducer: wire with v_shared vertex used by two edges (ec1 from v_shared to
v2, ec2 from v_shared to v3). LimitTolerance writes to v_shared twice with
last-write-wins semantics.

Byte assertions:
  contains(b'v_shared')
  contains(b'ec1')
  contains(b'ec2')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N134",
    defect=(
        "CLOSED_SHELL with face containing v_shared used by both ec1 (→v2) and "
        "ec2 (→v3); LimitTolerance processes v_shared twice without deduplication — "
        "tolerance applied twice, last-write-wins nondeterministic semantics"
    ),
)

# v_shared is shared between two edges
p0 = f.cartesian_point((0.0, 0.0, 0.0))   # v_shared
p1 = f.cartesian_point((1.0, 0.0, 0.0))   # v2
p2 = f.cartesian_point((0.0, 1.0, 0.0))   # v3
p3 = f.cartesian_point((1.0, 1.0, 0.0))   # corner

v_shared = f.vertex_point(p0, name="v_shared")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2, name="v3")
v4 = f.vertex_point(p3)

ec1 = f.edge_curve(v_shared, v2, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="ec1")
ec2 = f.edge_curve(v3, v_shared, f.line(p2, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)), name="ec2")
e_up   = f.edge_curve(v2, v4, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v4, v3, f.line(p3, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(ec1, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(ec2, True),
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
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N134.stp")
