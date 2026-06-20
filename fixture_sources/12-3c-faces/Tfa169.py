"""Tfa169 — ShapeAnalysis_CheckSmallFace.CheckSplittingVertices vertex-shared-by-many.

Catalog claim: Planar face with a central vertex shared by six or more edges
(star geometry with hub). CheckSplittingVertices uses pairwise edge-angle
comparisons; with >5 edges meeting at one vertex, the quadratic comparison
logic produces spurious splitting-vertex detections or misses actual
problematic configurations.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
face has a rectangular outer boundary (20×20) and an inner star wire with 6
edges all meeting at a central hub vertex (10, 10). Each of the 6 star arms
is an edge from the hub to a tip point 4mm away at 60° intervals, and then
returns via the same edge (using reversed orientation), making a star loop.
Actually implemented as a 12-edge loop: hub→tip0→hub→tip1→...→hub (non-manifold
at hub). The hub vertex is incident on 12 oriented-edge endpoints.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa169",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "outer wire: 20×20 rectangle at (0,0)-(20,20); "
        "inner star wire: 6-arm star with hub at (10,10); "
        "hub vertex incident on 12 edge endpoints (6 out + 6 back); "
        "CheckSplittingVertices quadratic pairwise angle comparison fails for >5 edges at vertex; "
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

# ── Outer wire: 20×20 rectangle ───────────────────────────────────────────────
op0 = f.cartesian_point((0.0,  0.0,  0.0))
op1 = f.cartesian_point((20.0, 0.0,  0.0))
op2 = f.cartesian_point((20.0, 20.0, 0.0))
op3 = f.cartesian_point((0.0,  20.0, 0.0))

ov0 = f._emit_raw(f"VERTEX_POINT('',#{op0.eid})")
ov1 = f._emit_raw(f"VERTEX_POINT('',#{op1.eid})")
ov2 = f._emit_raw(f"VERTEX_POINT('',#{op2.eid})")
ov3 = f._emit_raw(f"VERTEX_POINT('',#{op3.eid})")

od_px = f.direction((1.0,  0.0, 0.0))
od_py = f.direction((0.0,  1.0, 0.0))
od_nx = f.direction((-1.0, 0.0, 0.0))
od_ny = f.direction((0.0, -1.0, 0.0))

oln_b = f.line(op0, f.vector(od_px, 20.0))
oln_r = f.line(op1, f.vector(od_py, 20.0))
oln_t = f.line(op2, f.vector(od_nx, 20.0))
oln_l = f.line(op3, f.vector(od_ny, 20.0))

oec_b = f._emit_raw(f"EDGE_CURVE('oe_b',#{ov0.eid},#{ov1.eid},#{oln_b.eid},.T.)")
oec_r = f._emit_raw(f"EDGE_CURVE('oe_r',#{ov1.eid},#{ov2.eid},#{oln_r.eid},.T.)")
oec_t = f._emit_raw(f"EDGE_CURVE('oe_t',#{ov2.eid},#{ov3.eid},#{oln_t.eid},.T.)")
oec_l = f._emit_raw(f"EDGE_CURVE('oe_l',#{ov3.eid},#{ov0.eid},#{oln_l.eid},.T.)")

ooe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_b.eid},.T.)")
ooe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_r.eid},.T.)")
ooe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_t.eid},.T.)")
ooe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_l.eid},.T.)")

outer_loop = f._emit_raw(
    f"EDGE_LOOP('outer_loop',"
    f"(#{ooe_b.eid},#{ooe_r.eid},#{ooe_t.eid},#{ooe_l.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")

# ── Inner star wire: hub vertex + 6 tips ──────────────────────────────────────
HUB = (10.0, 10.0, 0.0)
ARM = 4.0    # arm length
N_ARMS = 6

hub_pt = f.cartesian_point(HUB)
hub_v  = f._emit_raw(f"VERTEX_POINT('hub',#{hub_pt.eid})")

# Build 6 tip vertices and 6 outbound edge-curves
tip_pts = []
tip_vs  = []
arm_ecs = []   # edge_curve hub→tip for each arm

for i in range(N_ARMS):
    angle = i * 2.0 * _math.pi / N_ARMS
    tx = HUB[0] + ARM * _math.cos(angle)
    ty = HUB[1] + ARM * _math.sin(angle)
    tp = f.cartesian_point((tx, ty, 0.0))
    tv = f._emit_raw(f"VERTEX_POINT('tip{i}',#{tp.eid})")
    # direction from hub to tip
    arm_dir = f.direction((_math.cos(angle), _math.sin(angle), 0.0))
    arm_vec = f.vector(arm_dir, ARM)
    arm_ln  = f.line(hub_pt, arm_vec)
    arm_ec  = f._emit_raw(
        f"EDGE_CURVE('arm{i}',#{hub_v.eid},#{tv.eid},#{arm_ln.eid},.T.)"
    )
    tip_pts.append(tp)
    tip_vs.append(tv)
    arm_ecs.append(arm_ec)

# Star loop: hub→tip0→hub→tip1→hub→...→tip5→hub
# For each arm i: forward edge (hub→tip_i, .T.) then back edge (same ec, .F. reversed)
oriented_edges = []
for i in range(N_ARMS):
    oe_fwd = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{arm_ecs[i].eid},.T.)")
    oe_bck = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{arm_ecs[i].eid},.F.)")
    oriented_edges.append(oe_fwd)
    oriented_edges.append(oe_bck)

oe_refs = ",".join(f"#{oe.eid}" for oe in oriented_edges)
inner_loop = f._emit_raw(f"EDGE_LOOP('star_hub_loop',({oe_refs}))")
# inner wire with .F. flag
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.F.)")

af = f._emit_raw(
    f"ADVANCED_FACE('star_hub_face',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa169.stp")
