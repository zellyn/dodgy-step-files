"""N046 — Default tolerance projection wrong on non-default tolerance shapes

A point-projection-onto-surface routine uses a hard-coded tolerance instead
of consulting the input shape's vertex/edge tolerance or the file's declared
UNCERTAINTY_MEASURE_WITH_UNIT. When the input context declares tolerance 1e-3,
the projection fails because the routine still uses 1e-7. A free CARTESIAN_POINT
at (0.5, 0.5, 5e-4) sits 5e-4 above a PLANE z=0; within the declared 1e-3 mm
context tolerance, but the kernel can't project it.

Byte assertions:
  contains(b'bloated')
  contains(b'5.0E-4')
  count_entity_def(b'VERTEX_POINT') == 4

Tier-3: n_edges_total >= 4
Tier-3: face[0].surface_type == "plane"
Tier-3: n_vertices_total >= 8
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N046",
    defect=(
        "PLANE z=0 with declared tolerance 1.0E-3; free CARTESIAN_POINT at "
        "(0.5, 0.5, 5.0E-4) is 5e-4 above plane — within declared tolerance "
        "but rejected by kernel's hardcoded 1e-7 internal projection tolerance"
    ),
)

# Host PLANE z=0
orig = f.cartesian_point((0.0, 0.0, 0.0), name="origin")
zdir = f.direction((0.0, 0.0, 1.0), name="+z")
xdir = f.direction((1.0, 0.0, 0.0), name="+x")
plc = f.axis2_placement_3d(orig, zdir, xdir, name="axes")
plane = f.plane(plc, name="high_tolerance")

# Quad face boundary (1x1 square)
pv0 = f.cartesian_point((0.0, 0.0, 0.0), name="v0")
vv0 = f.vertex_point(pv0)
pv1 = f.cartesian_point((1.0, 0.0, 0.0), name="v1")
vv1 = f.vertex_point(pv1)
pv2 = f.cartesian_point((1.0, 1.0, 0.0), name="v2")
vv2 = f.vertex_point(pv2)
pv3 = f.cartesian_point((0.0, 1.0, 0.0), name="v3")
vv3 = f.vertex_point(pv3)

dx = f.direction((1.0, 0.0, 0.0), name="+x")
vx = f.vector(dx, 1.0)
lx = f.line(pv0, vx)
e0 = f.edge_curve(vv0, vv1, lx)

dy = f.direction((0.0, 1.0, 0.0), name="+y")
vy = f.vector(dy, 1.0)
ly = f.line(pv1, vy)
e1 = f.edge_curve(vv1, vv2, ly)

dmx = f.direction((-1.0, 0.0, 0.0), name="-x")
vmx = f.vector(dmx, 1.0)
lmx = f.line(pv2, vmx)
e2 = f.edge_curve(vv2, vv3, lmx)

dmy = f.direction((0.0, -1.0, 0.0), name="-y")
vmy = f.vector(dmy, 1.0)
lmy = f.line(pv3, vmy)
e3 = f.edge_curve(vv3, vv0, lmy)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="bloated")

# Free point: 5.0e-4 mm above the plane (closer than declared tol 1.0e-3)
_free_pt = f.cartesian_point((0.5, 0.5, 5.0E-4), name="test_pt_5e-4_above_plane")

shell = f.open_shell([face], name="bloated_shell")
sbsm = f.shell_based_surface_model([shell])
# Declared tolerance: 1.0e-3 mm vertex tolerance (loose — the key defect)
f.add_product_chain(sbsm, uncertainty=1.0E-3)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N046.stp")
