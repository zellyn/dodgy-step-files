"""N047 — Linear and angular tolerance for same-surface face merging not user-specifiable

Same-domain face-merge logic uses fixed linear and angular tolerances. For a
coarse-mesh-derived shape (linear tolerance ~0.1 mm), the fixed thresholds are
too tight and merges fail. Two coplanar faces with native vertex tolerance
~0.1 mm share a common edge. Algorithm uses fixed 1e-7 threshold and refuses
to merge them despite sharing the same plane.

Byte assertions:
  contains(b'BC_shared')
  contains(b'coarse')
  count_entity_def(b'ADVANCED_FACE') == 2

Tier-3: face[0].surface_type == "plane"
Tier-3: n_edges_total >= 8
Tier-3: face[1].surface_type == "plane"
Tier-3: n_vertices_total >= 16
Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N047",
    defect=(
        "two coplanar ADVANCED_FACEs share a common EDGE_CURVE (BC_shared); "
        "declared vertex tolerance 0.1 mm; UnifySameDomain uses fixed 1e-7 "
        "threshold and refuses to merge the faces despite same underlying PLANE"
    ),
)

# Single PLANE shared by both faces
orig = f.cartesian_point((0.0, 0.0, 0.0), name="origin")
zdir = f.direction((0.0, 0.0, 1.0), name="+z")
xdir = f.direction((1.0, 0.0, 0.0), name="+x")
plc = f.axis2_placement_3d(orig, zdir, xdir, name="axes")
plane = f.plane(plc, name="coarse")

# Vertices: A=(0,0,0), B=(1,0,0), C=(1,1,0), D=(0,1,0), E=(2,0,0), F=(2,1,0)
pA = f.cartesian_point((0.0, 0.0, 0.0), name="A")
vA = f.vertex_point(pA, name="A")
pB = f.cartesian_point((1.0, 0.0, 0.0), name="B")
vB = f.vertex_point(pB, name="B")
pC = f.cartesian_point((1.0, 1.0, 0.0), name="C")
vC = f.vertex_point(pC, name="C")
pD = f.cartesian_point((0.0, 1.0, 0.0), name="D")
vD = f.vertex_point(pD, name="D")
pE = f.cartesian_point((2.0, 0.0, 0.0), name="E")
vE = f.vertex_point(pE, name="E")
pF = f.cartesian_point((2.0, 1.0, 0.0), name="F")
vF = f.vertex_point(pF, name="F")

# Edges
dx = f.direction((1.0, 0.0, 0.0), name="+x")
vx = f.vector(dx, 1.0, name="vx")
dy = f.direction((0.0, 1.0, 0.0), name="+y")
vy = f.vector(dy, 1.0, name="vy")
dmx = f.direction((-1.0, 0.0, 0.0), name="-x")
vmx = f.vector(dmx, 1.0, name="vmx")
dmy = f.direction((0.0, -1.0, 0.0), name="-y")
vmy = f.vector(dmy, 1.0, name="vmy")

eAB = f.edge_curve(vA, vB, f.line(pA, vx), name="AB")
eBC = f.edge_curve(vB, vC, f.line(pB, vy), name="BC_shared")  # shared edge — the defect site
eCD = f.edge_curve(vC, vD, f.line(pC, vmx), name="CD")
eDA = f.edge_curve(vD, vA, f.line(pD, vmy), name="DA")
eBE = f.edge_curve(vB, vE, f.line(pB, vx), name="BE")
eEF = f.edge_curve(vE, vF, f.line(pE, vy), name="EF")
eFC = f.edge_curve(vF, vC, f.line(pF, vmx), name="FC")

# Face 1: A->B->C->D->A
loop1 = f.edge_loop([
    f.oriented_edge(eAB, True),
    f.oriented_edge(eBC, True),   # BC shared edge forward
    f.oriented_edge(eCD, True),
    f.oriented_edge(eDA, True),
])
fob1 = f.face_outer_bound(loop1)
face1 = f.advanced_face([fob1], plane, name="left_face")

# Face 2: B->E->F->C->B (shares edge BC with face 1, reversed)
loop2 = f.edge_loop([
    f.oriented_edge(eBE, True),
    f.oriented_edge(eEF, True),
    f.oriented_edge(eFC, True),
    f.oriented_edge(eBC, False),   # shared BC reversed — defect: same plane, shared edge
])
fob2 = f.face_outer_bound(loop2)
face2 = f.advanced_face([fob2], plane, name="right_face")

shell = f.open_shell([face1, face2], name="wrap_shell")
sbsm = f.shell_based_surface_model([shell])
# Coarse vertex tolerance 0.1 mm — algorithm should use this but uses fixed 1e-7
f.add_product_chain(sbsm, uncertainty=0.1)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N047.stp")
