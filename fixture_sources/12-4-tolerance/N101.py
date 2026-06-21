"""N101 — ShapeFix_Edge.FixVertexTolerance reset-on-fix

Vertex tolerance escalated during initial edge check, then silently reset to
base value when FixVertexTolerance executes. Defect: no error on tolerance
loss; downstream checks see degraded tolerance state and fail inconsistently.

Reproducer: simple edge whose vertex tolerance is set higher than base during
edge validation, then FixVertexTolerance silently resets it.

Byte assertions:
  contains(b'edge1')
  contains(b'v1')
  contains(b'v2')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N101",
    defect=(
        "CLOSED_SHELL shell with face1 containing edge1 from v1 to v2; "
        "vertex tolerance escalated during edge check then silently reset by "
        "FixVertexTolerance — no error reported, downstream tolerance state degraded"
    ),
)

# Simple 1×1 square face
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v1 = f.vertex_point(p0, name="v1")
v2 = f.vertex_point(p1, name="v2")
v3 = f.vertex_point(p2)
v4 = f.vertex_point(p3)

e1 = f.edge_curve(v1, v2, f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)), name="edge1")
e2 = f.edge_curve(v2, v3, f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e3 = f.edge_curve(v3, v4, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e4 = f.edge_curve(v4, v1, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e4, True),
])
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane, name="face1")

shell = f.closed_shell([face], name="shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N101.stp")
