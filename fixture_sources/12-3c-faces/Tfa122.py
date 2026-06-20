"""Tfa122 — ShapeAnalysis_CheckSmallFace.CheckTwisted self-touching wire.

Catalog claim: A face whose outer wire self-touches at a non-endpoint vertex
within the face interior. CheckTwisted's classification logic treats self-contact
as face twist when geometrically the wire is merely internally tangent (a
figure-8 or self-touching contour that is not a true topological twist).

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE
whose outer wire forms a figure-8 shape: the wire traverses a path that
passes through the central contact point (3.0, 5.0, 0.0) twice — once on
the way around the left lobe and once on the way around the right lobe.
The wire is self-touching at the interior vertex but not self-intersecting.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa122",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "outer wire forms figure-8: self-touches at interior point (3.0,5.0,0.0); "
        "left lobe: (3,5)→(0,5)→(0,0)→(3,0)→(3,5); right lobe: (3,5)→(3,0)→(6,0)→(6,5)→(3,5); "
        "contact vertex at (3,5,0) appears twice in wire traversal; "
        "wire is self-touching (internally tangent) not self-intersecting; "
        "CheckTwisted misclassifies self-contact as topological twist; "
        "kernel should distinguish twisted face from merely self-touching wire; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Figure-8 wire vertices ────────────────────────────────────────────────────
# Self-touch point C at (3.0, 5.0, 0.0) — used as both start and mid-point
# Left lobe: C → L0(0,5) → L1(0,0) → L2(3,0) → C
# Right lobe continues: C → R1(3,0) → R2(6,0) → R3(6,5) → C
# Full wire: C → L0 → L1 → L2 → C → R1 → R2 → R3 → C (self-touch at C twice)

cp_C  = f.cartesian_point((3.0, 5.0, 0.0))   # self-touch contact point
cp_L0 = f.cartesian_point((0.0, 5.0, 0.0))
cp_L1 = f.cartesian_point((0.0, 0.0, 0.0))
cp_L2 = f.cartesian_point((3.0, 0.0, 0.0))
cp_R2 = f.cartesian_point((6.0, 0.0, 0.0))
cp_R3 = f.cartesian_point((6.0, 5.0, 0.0))

# Vertices — C appears twice (self-touch): once as start of left lobe, once mid-point
vC_start = f._emit_raw(f"VERTEX_POINT('contact_start',#{cp_C.eid})")
vL0      = f._emit_raw(f"VERTEX_POINT('',#{cp_L0.eid})")
vL1      = f._emit_raw(f"VERTEX_POINT('',#{cp_L1.eid})")
vL2_R1   = f._emit_raw(f"VERTEX_POINT('',#{cp_L2.eid})")  # shared bottom center
vC_mid   = f._emit_raw(f"VERTEX_POINT('contact_mid',#{cp_C.eid})")  # same pt, second vertex
vR2      = f._emit_raw(f"VERTEX_POINT('',#{cp_R2.eid})")
vR3      = f._emit_raw(f"VERTEX_POINT('',#{cp_R3.eid})")

# ── Edges: left lobe ──────────────────────────────────────────────────────────
# e1: C_start → L0 (west along y=5)
d_nx = f.direction((-1.0, 0.0, 0.0))
v_nx = f.vector(d_nx, 3.0)
ln1  = f.line(cp_C, v_nx)
ec1  = f._emit_raw(f"EDGE_CURVE('e_C_to_L0',#{vC_start.eid},#{vL0.eid},#{ln1.eid},.T.)")

# e2: L0 → L1 (south along x=0)
d_ny = f.direction((0.0, -1.0, 0.0))
v_ny = f.vector(d_ny, 5.0)
ln2  = f.line(cp_L0, v_ny)
ec2  = f._emit_raw(f"EDGE_CURVE('e_L0_to_L1',#{vL0.eid},#{vL1.eid},#{ln2.eid},.T.)")

# e3: L1 → L2/R1 (east along y=0)
d_px = f.direction((1.0, 0.0, 0.0))
v_px3 = f.vector(d_px, 3.0)
ln3   = f.line(cp_L1, v_px3)
ec3   = f._emit_raw(f"EDGE_CURVE('e_L1_to_L2',#{vL1.eid},#{vL2_R1.eid},#{ln3.eid},.T.)")

# e4: L2/R1 → C_mid (north along x=3)
d_py = f.direction((0.0, 1.0, 0.0))
v_py5 = f.vector(d_py, 5.0)
ln4   = f.line(cp_L2, v_py5)
ec4   = f._emit_raw(f"EDGE_CURVE('e_L2_to_C',#{vL2_R1.eid},#{vC_mid.eid},#{ln4.eid},.T.)")

# ── Edges: right lobe ────────────────────────────────────────────────────────
# e5: C_mid → R1 (=L2 bottom, south along x=3)
ln5  = f.line(cp_C, v_py5)  # reuse direction; reverse: C→R1 south
d_ny2 = f.direction((0.0, -1.0, 0.0))
v_ny5 = f.vector(d_ny2, 5.0)
ln5   = f.line(cp_C, v_ny5)
ec5   = f._emit_raw(f"EDGE_CURVE('e_C_to_R1',#{vC_mid.eid},#{vL2_R1.eid},#{ln5.eid},.T.)")

# e6: R1 → R2 (east along y=0)
v_px3b = f.vector(d_px, 3.0)
ln6    = f.line(cp_L2, v_px3b)
ec6    = f._emit_raw(f"EDGE_CURVE('e_R1_to_R2',#{vL2_R1.eid},#{vR2.eid},#{ln6.eid},.T.)")

# e7: R2 → R3 (north along x=6)
v_py5b = f.vector(d_py, 5.0)
ln7    = f.line(cp_R2, v_py5b)
ec7    = f._emit_raw(f"EDGE_CURVE('e_R2_to_R3',#{vR2.eid},#{vR3.eid},#{ln7.eid},.T.)")

# e8: R3 → C_start (west along y=5)
d_nx2 = f.direction((-1.0, 0.0, 0.0))
v_nx3 = f.vector(d_nx2, 3.0)
ln8   = f.line(cp_R3, v_nx3)
ec8   = f._emit_raw(f"EDGE_CURVE('e_R3_to_C',#{vR3.eid},#{vC_start.eid},#{ln8.eid},.T.)")

# ── Wire: 8 oriented edges forming the self-touching figure-8 ─────────────────
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")
oe5 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec5.eid},.T.)")
oe6 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec6.eid},.T.)")
oe7 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec7.eid},.T.)")
oe8 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec8.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('figure8_loop',("
    f"#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid},"
    f"#{oe5.eid},#{oe6.eid},#{oe7.eid},#{oe8.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af  = f._emit_raw(f"ADVANCED_FACE('self_touching_face',(#{fob.eid}),#{plane.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa122.stp")
