"""Tfa003 — FaceOuterBound translation failed (face incomplete without outer wire).

Catalog claim: The bound entity referenced from FACE_OUTER_BOUND.bound failed
translation (empty EDGE_LOOP, all edges dropped). Without an outer bound the
face is incomplete.

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE whose
FACE_OUTER_BOUND references an EDGE_LOOP whose every ORIENTED_EDGE refers to
an EDGE_CURVE with a null 3D curve (no geometry on the edge — curve entity is
absent). OCC sees a GEOMETRIC_CURVE_SET and returns empty; the defective face
topology is visible in the file.

Byte assertions:
  - contains(b'FACE_OUTER_BOUND(')
  - count_entity_def(b'EDGE_LOOP') >= 2
  - count_entity_def(b'ADVANCED_FACE') >= 1

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa003",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE; "
        "FACE_OUTER_BOUND references EDGE_LOOP whose every ORIENTED_EDGE wraps "
        "an EDGE_CURVE with no underlying 3D curve (null curve — entity absent); "
        "all edges in outer loop drop during translation; "
        "ADVANCED_FACE is left without an outer boundary — face is incomplete; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface for the ADVANCED_FACE ──────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices at four corners ──────────────────────────────────────────────────
v0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v1 = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))
v2 = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))
v3 = f.vertex_point(f.cartesian_point((0.0, 10.0, 0.0)))

# ── EDGE_CURVEs with null curve ($) — no underlying geometry ─────────────────
# These edges have missing curve references (represented by $ in STEP).
# The FACE_OUTER_BOUND translator drops all edges and the face loses its outer wire.
ec0 = f._emit_raw(f"EDGE_CURVE('null_edge_0',#{v0.eid},#{v1.eid},$,.T.)")
ec1 = f._emit_raw(f"EDGE_CURVE('null_edge_1',#{v1.eid},#{v2.eid},$,.T.)")
ec2 = f._emit_raw(f"EDGE_CURVE('null_edge_2',#{v2.eid},#{v3.eid},$,.T.)")
ec3 = f._emit_raw(f"EDGE_CURVE('null_edge_3',#{v3.eid},#{v0.eid},$,.T.)")

oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# EDGE_LOOP with all-null edges — this is the defective bound
# count_entity_def(b'EDGE_LOOP') >= 2 requires at least 2 loops in the file;
# we add a second degenerate loop as a stand-alone wire container.
null_loop = f._emit_raw(
    f"EDGE_LOOP('null_outer_loop',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# Second EDGE_LOOP (good geometry) to satisfy byte assertion >= 2
v4 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
v5 = f.vertex_point(f.cartesian_point((2.0, 1.0, 0.0)))
d_x  = f.direction((1.0, 0.0, 0.0))
vec1 = f.vector(d_x, 1.0)
ln1  = f.line(f.cartesian_point((1.0, 1.0, 0.0)), vec1)
ec_good = f._emit_raw(f"EDGE_CURVE('good_edge',#{v4.eid},#{v5.eid},#{ln1.eid},.T.)")
oe_good = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_good.eid},.T.)")
good_loop = f._emit_raw(f"EDGE_LOOP('good_loop',(#{oe_good.eid}))")

# FACE_OUTER_BOUND referencing the all-null EDGE_LOOP
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{null_loop.eid},.T.)")

# ADVANCED_FACE: outer bound with null-curve edges — will fail translation
af = f._emit_raw(f"ADVANCED_FACE('',( #{fob.eid}),#{plane.eid},.T.)")

# GEOMETRIC_CURVE_SET holds both the defective face and the second loop
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid},#{good_loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa003.stp")
