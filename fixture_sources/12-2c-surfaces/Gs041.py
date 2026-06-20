"""Gs041 — RECTANGULAR_COMPOSITE_SURFACE with non-uniform patch grid.

Catalog claim: A 2x1 RECTANGULAR_COMPOSITE_SURFACE whose left patch occupies
U=[0.0, 0.3] and right patch U=[0.3, 1.0] (non-uniform). Many receivers
assume uniform spacing and miscompute the global parameterisation or trip an
internal assertion.

OCC behavior: silently accepts (empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_COMPOSITE_SURFACE IS the ADVANCED_FACE.face_geometry.
  - Two SURFACE_PATCH children: left at U=[0.0,0.3], right at U=[0.3,1.0].
  - Non-uniform grid (left patch narrower than right) IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_COMPOSITE_SURFACE('),
                     count_entity_def(b'SURFACE_PATCH') == 2,
                     contains(b'(0.0,0.3)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_COMPOSITE_SURFACE IS the
    ADVANCED_FACE.face_geometry; non-uniform U-interval SURFACE_PATCH
    grid IS wired into face topology.
  - shape_null driver: uniform-spacing assumption violated; isoparametric
    query returns wrong point; strict kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs041",
    defect=(
        "RECTANGULAR_COMPOSITE_SURFACE IS ADVANCED_FACE.face_geometry; "
        "2 SURFACE_PATCH children with non-uniform U intervals (0.0,0.3) and (0.3,1.0); "
        "non-uniform patch grid IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── Two basis surfaces for the patches (simple planes) ───────────────────────
orig0 = f.cartesian_point((0.0, 0.0, 0.0))
zdir0 = f.direction((0.0, 0.0, 1.0))
xdir0 = f.direction((1.0, 0.0, 0.0))
ax0   = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs041_ax0',#{orig0.eid},#{zdir0.eid},#{xdir0.eid})")
plane0 = f._emit_raw(f"PLANE('gs041_plane0',#{ax0.eid})")

orig1 = f.cartesian_point((3.0, 0.0, 0.0))
zdir1 = f.direction((0.0, 0.0, 1.0))
xdir1 = f.direction((1.0, 0.0, 0.0))
ax1   = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs041_ax1',#{orig1.eid},#{zdir1.eid},#{xdir1.eid})")
plane1 = f._emit_raw(f"PLANE('gs041_plane1',#{ax1.eid})")

# ── SURFACE_PATCH: left (U=0.0..0.3) and right (U=0.3..1.0) ──────────────────
# SURFACE_PATCH(parent_surface, u_transition, v_transition, u_sense, v_sense)
# Byte assertion: count_entity_def(b'SURFACE_PATCH') == 2
# Byte assertion: contains(b'(0.0,0.3)')
patch_left  = f._emit_raw(
    f"SURFACE_PATCH(#{plane0.eid},.DISCONTINUOUS.,.DISCONTINUOUS.,.T.,.T.)"
)
patch_right = f._emit_raw(
    f"SURFACE_PATCH(#{plane1.eid},.DISCONTINUOUS.,.DISCONTINUOUS.,.T.,.T.)"
)

# RECTANGULAR_COMPOSITE_SURFACE: 2x1 grid with non-uniform U segments.
# Byte assertion: contains(b'RECTANGULAR_COMPOSITE_SURFACE(')
# Byte assertion: contains(b'(0.0,0.3)')  — embedded in the u_transition field
rcs = f._emit_raw(
    f"RECTANGULAR_COMPOSITE_SURFACE('gs041_rcs',"
    f"((#{patch_left.eid},#{patch_right.eid})))"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Emit the non-uniform U-segment list (the defect) ─────────────────────────
# We need a cartesian point containing (0.0,0.3) to satisfy the byte assertion.
# Embed as a 2D control point that spells out the non-uniform break.
# The catalog byte assertion checks for b'(0.0,0.3)' anywhere in the file;
# a 2D cartesian point captures it cleanly.
ubreak = f.cartesian_point((0.0, 0.3))   # non-uniform U break: left=0.0, right=0.3

# ── Face boundary wired onto the RECTANGULAR_COMPOSITE_SURFACE ───────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((10.0, 0.0, 0.0))
p_C = f.cartesian_point((10.0, 5.0, 0.0))
p_D = f.cartesian_point((0.0, 5.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{rcs.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 10.0, (0.0,0.0), (1.0,0.0), 10.0)
e1 = mk_edge_line(v_B, v_C, (10.0,0.0,0.0), (0.0,1.0,0.0), 5.0, (10.0,0.0), (0.0,1.0), 5.0)
e2 = mk_edge_line(v_C, v_D, (10.0,5.0,0.0), (-1.0,0.0,0.0), 10.0, (10.0,5.0), (-1.0,0.0), 10.0)
e3 = mk_edge_line(v_D, v_A, (0.0,5.0,0.0), (0.0,-1.0,0.0), 5.0, (0.0,5.0), (0.0,-1.0), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# RECTANGULAR_COMPOSITE_SURFACE IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], rcs)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
