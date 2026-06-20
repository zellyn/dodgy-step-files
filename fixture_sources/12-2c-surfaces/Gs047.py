"""Gs047 — BLENDED_EDGE_SURFACE with mismatched fillet radii at a shared vertex.

Catalog claim: two BLENDED_EDGE_SURFACE instances (blendA radius=1.0, blendB
radius=2.0) meet at the origin. The differing radii create a 0-thickness gap
where the two fillet surfaces cannot join smoothly.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - BLENDED_EDGE_SURFACE('blendA_radius_1', #25, 1.0) IS the ADVANCED_FACE.face_geometry
    of the first defect face.
  - BLENDED_EDGE_SURFACE('blendB_radius_2', #31, 2.0) IS the ADVANCED_FACE.face_geometry
    of the second defect face.
  - Both faces share a common vertex at the origin. The mismatched radii mean
    they cannot meet C0; the 0-thickness gap IS the defect wired into shell topology.
  - Byte assertions: count_entity_def(b'BLENDED_EDGE_SURFACE') == 2,
                     contains(b"BLENDED_EDGE_SURFACE('blendA_radius_1',#25,1.0)"),
                     contains(b"BLENDED_EDGE_SURFACE('blendB_radius_2',#31,2.0)").
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: two BLENDED_EDGE_SURFACE entities with radii 1.0 and 2.0
    ARE the face_geometry of adjacent ADVANCED_FACEs sharing a vertex at origin;
    mismatched radii create 0-thickness gap at shared vertex IS wired into shell topology.
  - shape_null driver: gap where fillets meet; strict reject kernels produce empty result.

Entity layout to satisfy byte assertions (refs #25 and #31):
  #1..#20   — 20 padding cartesian_points
  #21       — cylA_orig
  #22       — cylA_zdir
  #23       — cylA_xdir
  #24       — cylA_ax (AXIS2_PLACEMENT_3D)
  #25       — cylA (CYLINDRICAL_SURFACE radius 1.0)  ← blendA references this
  #26       — prc (2D representation context)
  #27       — cylB_orig
  #28       — cylB_zdir
  #29       — cylB_xdir
  #30       — cylB_ax (AXIS2_PLACEMENT_3D)
  #31       — cylB (CYLINDRICAL_SURFACE radius 2.0)  ← blendB references this
  #32       — blendA (BLENDED_EDGE_SURFACE('blendA_radius_1',#25,1.0))
  #33       — blendB (BLENDED_EDGE_SURFACE('blendB_radius_2',#31,2.0))
  ...face topology follows...
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs047",
    defect=(
        "BLENDED_EDGE_SURFACE('blendA_radius_1',#25,1.0) and "
        "BLENDED_EDGE_SURFACE('blendB_radius_2',#31,2.0) ARE face_geometry of adjacent "
        "ADVANCED_FACEs sharing a vertex at origin; mismatched radii (1.0 vs 2.0) "
        "create 0-thickness gap at shared vertex IS wired into shell topology; shape(1) (live OCC heals)"
    ),
)

# ── Padding: 20 entities (#1..#20) to push cylA_orig to #21 ───────────────────
for _i in range(20):
    f.cartesian_point((float(_i), 0.0, 0.0))

# ── cylA group: CYLINDRICAL_SURFACE radius 1.0 at entity #25 ──────────────────
# #21..#25
cylA_orig = f.cartesian_point((-1.0, 0.0, 0.0))   # #21
cylA_zdir = f.direction((0.0, 0.0, 1.0))           # #22
cylA_xdir = f.direction((1.0, 0.0, 0.0))           # #23
cylA_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs047_cylA_ax',#{cylA_orig.eid},#{cylA_zdir.eid},#{cylA_xdir.eid})"
)  # #24
cylA = f._emit_raw(f"CYLINDRICAL_SURFACE('gs047_cylA',#{cylA_ax.eid},1.0)")  # #25

# ── prc at #26 (gap between cylA and cylB to put cylB at #31) ─────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)  # #26

# ── cylB group: CYLINDRICAL_SURFACE radius 2.0 at entity #31 ──────────────────
# #27..#31
cylB_orig = f.cartesian_point((2.0, 0.0, 0.0))    # #27
cylB_zdir = f.direction((0.0, 0.0, 1.0))           # #28
cylB_xdir = f.direction((1.0, 0.0, 0.0))           # #29
cylB_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs047_cylB_ax',#{cylB_orig.eid},#{cylB_zdir.eid},#{cylB_xdir.eid})"
)  # #30
cylB = f._emit_raw(f"CYLINDRICAL_SURFACE('gs047_cylB',#{cylB_ax.eid},2.0)")  # #31

# ── BLENDED_EDGE_SURFACE instances ────────────────────────────────────────────
# AP242 schema: BLENDED_EDGE_SURFACE(name, surface, radius)
# Byte assertion: count_entity_def(b'BLENDED_EDGE_SURFACE') == 2
# Byte assertion: contains(b"BLENDED_EDGE_SURFACE('blendA_radius_1',#25,1.0)")
blendA = f._emit_raw(f"BLENDED_EDGE_SURFACE('blendA_radius_1',#{cylA.eid},1.0)")  # #32
# Byte assertion: contains(b"BLENDED_EDGE_SURFACE('blendB_radius_2',#31,2.0)")
blendB = f._emit_raw(f"BLENDED_EDGE_SURFACE('blendB_radius_2',#{cylB.eid},2.0)")  # #33

# ── Shared vertex at origin (where the two blends meet with mismatched radii) ──
p_shared = f.cartesian_point((0.0, 0.0, 0.0))
v_shared  = f.vertex_point(p_shared)

# ── Face A boundary (blendA, radius 1.0) ──────────────────────────────────────
pA_A = f.cartesian_point((-1.0, 0.0, 0.0))
pA_C = f.cartesian_point((-1.0, 1.0, 0.0))

vA_A = f.vertex_point(pA_A)
vA_C = f.vertex_point(pA_C)

def mk_edge_line_on(surf, vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

eA0 = mk_edge_line_on(blendA, vA_A, v_shared,
                      (-1.0,0.0,0.0), (1.0,0.0,0.0), 1.0,
                      (0.0,0.0), (1.0,0.0), 1.0)
eA1 = mk_edge_line_on(blendA, v_shared, vA_C,
                      (0.0,0.0,0.0), (-1.0,1.0,0.0), 1.414,
                      (1.0,0.0), (-1.0,1.0), 1.0)
eA2 = mk_edge_line_on(blendA, vA_C, vA_A,
                      (-1.0,1.0,0.0), (0.0,-1.0,0.0), 1.0,
                      (0.0,1.0), (0.0,-1.0), 1.0)

loopA = f.edge_loop([
    f.oriented_edge(eA0, True),
    f.oriented_edge(eA1, True),
    f.oriented_edge(eA2, True),
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], blendA)

# ── Face B boundary (blendB, radius 2.0) ──────────────────────────────────────
pB_B = f.cartesian_point((2.0, 0.0, 0.0))
pB_C = f.cartesian_point((2.0, 1.0, 0.0))

vB_B = f.vertex_point(pB_B)
vB_C = f.vertex_point(pB_C)

eB0 = mk_edge_line_on(blendB, v_shared, vB_B,
                      (0.0,0.0,0.0), (1.0,0.0,0.0), 2.0,
                      (0.0,0.0), (1.0,0.0), 2.0)
eB1 = mk_edge_line_on(blendB, vB_B, vB_C,
                      (2.0,0.0,0.0), (0.0,1.0,0.0), 1.0,
                      (2.0,0.0), (0.0,1.0), 1.0)
eB2 = mk_edge_line_on(blendB, vB_C, v_shared,
                      (2.0,1.0,0.0), (-1.0,-0.5,0.0), 2.236,
                      (2.0,1.0), (-1.0,-0.5), 1.0)

loopB = f.edge_loop([
    f.oriented_edge(eB0, True),
    f.oriented_edge(eB1, True),
    f.oriented_edge(eB2, True),
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], blendB)

# ── Shell: both blended faces sharing the vertex at origin ─────────────────────
shell = f.open_shell([faceA, faceB])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
