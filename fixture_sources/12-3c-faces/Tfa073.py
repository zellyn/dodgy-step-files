"""Tfa073 — ShapeFix_FixSmallFace.ComputeSharedEdgeForStripFace asymmetry.

Catalog claim: Strip-face shared-edge construction with asymmetric endpoint-pair
merging. V1 merged to V3 (dev < tol), but V2 not merged to V4 (dev > tol),
creating a degenerate edge with one matched vertex and one unmatched.

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE.
Two edge candidates E1=(V1,V2) and E2=(V3,V4) appear inside the face topology.
V1 and V3 are 0.00005 apart (< tolerance 0.001), V2 and V4 are 1.5 apart
(>> tolerance). The shared-edge construction merges V1↔V3 but not V2↔V4,
producing a degenerate edge spanning (V3, V4) with broken topology.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa073",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "strip-face topology: two candidate shared edges E1=(V1,V2), E2=(V3,V4); "
        "dev(V1,V3)=0.00005 < tol(0.001) → V1 merged to V3; "
        "dev(V2,V4)=1.5 >> tol(0.001) → V2 not merged to V4; "
        "asymmetric merging: shared edge constructed as (V3,V4) with V2 unmatched; "
        "degenerate edge breaks strip-face topology; "
        "ComputeSharedEdgeForStripFace should merge both endpoints or neither; "
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

# ── Vertices: V1 near V3 (0.00005 apart), V2 far from V4 (1.5 apart) ────────
# V1 at (0.0, 0.0, 0.0), V3 at (0.00005, 0.0, 0.0) — dev < tol 0.001 → merged
# V2 at (5.0, 0.0, 0.0), V4 at (5.0, 1.5, 0.0) — dev = 1.5 >> tol → not merged
cp_v1 = f.cartesian_point((0.0,     0.0, 0.0))
cp_v2 = f.cartesian_point((5.0,     0.0, 0.0))
cp_v3 = f.cartesian_point((0.00005, 0.0, 0.0))
cp_v4 = f.cartesian_point((5.0,     1.5, 0.0))

vV1 = f._emit_raw(f"VERTEX_POINT('V1',#{cp_v1.eid})")
vV2 = f._emit_raw(f"VERTEX_POINT('V2',#{cp_v2.eid})")
vV3 = f._emit_raw(f"VERTEX_POINT('V3',#{cp_v3.eid})")
vV4 = f._emit_raw(f"VERTEX_POINT('V4',#{cp_v4.eid})")

# ── Edge E1: V1 → V2 along the strip bottom ───────────────────────────────────
import math as _math
dx12 = 5.0 - 0.0
dy12 = 0.0 - 0.0
mag12 = _math.hypot(dx12, dy12)
d_e1  = f.direction((dx12 / mag12, 0.0, 0.0))
v_e1  = f.vector(d_e1, mag12)
ln_e1 = f.line(cp_v1, v_e1)
ec_e1 = f._emit_raw(f"EDGE_CURVE('E1',#{vV1.eid},#{vV2.eid},#{ln_e1.eid},.T.)")

# ── Edge E2: V3 → V4 — asymmetric partner ────────────────────────────────────
dx34 = 5.0 - 0.00005
dy34 = 1.5 - 0.0
mag34 = _math.hypot(dx34, dy34)
d_e2  = f.direction((dx34 / mag34, dy34 / mag34, 0.0))
v_e2  = f.vector(d_e2, mag34)
ln_e2 = f.line(cp_v3, v_e2)
ec_e2 = f._emit_raw(f"EDGE_CURVE('E2',#{vV3.eid},#{vV4.eid},#{ln_e2.eid},.T.)")

# ── Close the strip: two closing edges connecting the open ends ───────────────
# Close1: V2 → V4 (the unmerged gap)
dx24 = 5.0 - 5.0
dy24 = 1.5 - 0.0
mag24 = _math.hypot(dx24, dy24) if _math.hypot(dx24, dy24) > 0 else 1.5
d_c1  = f.direction((0.0, 1.0, 0.0))
v_c1  = f.vector(d_c1, 1.5)
ln_c1 = f.line(cp_v2, v_c1)
ec_c1 = f._emit_raw(f"EDGE_CURVE('close1',#{vV2.eid},#{vV4.eid},#{ln_c1.eid},.T.)")

# Close2: V3 → V1 (the near-merged end)
dx31 = 0.0 - 0.00005
dy31 = 0.0
mag31 = _math.hypot(dx31, dy31) if _math.hypot(dx31, dy31) > 0 else 0.00005
d_c2  = f.direction((-1.0, 0.0, 0.0))
v_c2  = f.vector(d_c2, 0.00005)
ln_c2 = f.line(cp_v3, v_c2)
ec_c2 = f._emit_raw(f"EDGE_CURVE('close2',#{vV3.eid},#{vV1.eid},#{ln_c2.eid},.T.)")

# ── Wire: E1 → close1(rev) → E2(rev) → close2 ───────────────────────────────
oe_e1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_c1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_c1.eid},.T.)")
oe_e2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.F.)")
oe_c2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_c2.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e1.eid},#{oe_c1.eid},#{oe_e2.eid},#{oe_c2.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af  = f._emit_raw(f"ADVANCED_FACE('strip_face',(#{fob.eid}),#{plane.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa073.stp")
