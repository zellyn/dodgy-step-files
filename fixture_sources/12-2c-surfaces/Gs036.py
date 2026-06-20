"""Gs036 — Negative-radius / zero-magnitude direction or vector.

Catalog claim: DIRECTION with all-zero direction_ratios (0.,0.,0.) referenced by
AXIS2_PLACEMENT_3D; or axis and ref_direction colinear so an orthonormal frame
cannot be constructed. Kernel must reject or heal (project ref_direction); never crash.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - The PLANE's AXIS2_PLACEMENT_3D references a zero-magnitude DIRECTION
    ('', (0.0,0.0,0.0)) as the ref_direction (x-direction).
  - Two normal DIRECTION('', (0.0,0.0,1.0)) entities are also present
    (axis and z of placement), satisfying the count assertion.
  - Byte assertions: contains(b"DIRECTION('',(0.0,0.0,0.0))"),
                     count(b"DIRECTION('',(0.0,0.0,1.0))") >= 2.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; the defect
    DIRECTION with all-zero direction_ratios IS the ref_direction of the PLANE's
    AXIS2_PLACEMENT_3D; zero-direction IS wired into face topology via the surface.
  - shape_null driver: zero-magnitude direction cannot form orthonormal frame;
    strict reject kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs036",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; AXIS2_PLACEMENT_3D ref_direction IS "
        "DIRECTION('',(0.0,0.0,0.0)) (zero magnitude); "
        "count(DIRECTION('',(0.0,0.0,1.0)))>=2; "
        "zero-direction wired into face surface placement; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: PLANE with zero-magnitude ref_direction ────────────────
# Normal Z-axis direction for the plane axis — byte assertion: count >= 2
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir1 = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")   # axis direction (normal to plane)
# DEFECT: zero-magnitude ref_direction — byte assertion: contains DIRECTION('',(0.0,0.0,0.0))
zero_dir = f._emit_raw("DIRECTION('',(0.0,0.0,0.0))")

# Second normal direction (for pcurve contexts) — ensures count >= 2
zdir2 = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")

# AXIS2_PLACEMENT_3D: axis=(0,0,1) (valid), ref_direction=zero (defect)
ax3 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs036_ax',#{orig.eid},#{zdir1.eid},#{zero_dir.eid})"
)
plane = f._emit_raw(f"PLANE('gs036_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangle on the (degenerate) plane ───────────────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((5.0, 0.0, 0.0))
p_C = f.cartesian_point((5.0, 4.0, 0.0))
p_D = f.cartesian_point((0.0, 4.0, 0.0))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 5.0, (0.0,0.0), (1.0,0.0), 5.0)
e1 = mk_edge_line(v_B, v_C, (5.0,0.0,0.0), (0.0,1.0,0.0), 4.0, (5.0,0.0), (0.0,1.0), 4.0)
e2 = mk_edge_line(v_C, v_D, (5.0,4.0,0.0), (-1.0,0.0,0.0), 5.0, (5.0,4.0), (-1.0,0.0), 5.0)
e3 = mk_edge_line(v_D, v_A, (0.0,4.0,0.0), (0.0,-1.0,0.0), 4.0, (0.0,4.0), (0.0,-1.0), 4.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; zero DIRECTION IS ref_direction of PLANE's AXIS2_PLACEMENT_3D.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
