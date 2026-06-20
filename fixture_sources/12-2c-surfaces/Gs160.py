"""Gs160 — GeomAdaptor_Surface offset-surface misclassification.

Catalog claim: Type switch in GeomAdaptor_Surface covers 5 standard types
(plane, cylinder, cone, sphere, torus) but omits the offset-surface branch.
Offset surfaces fall to default case (LOther), losing semantic grouping and
confusing downstream algorithms expecting elementary surfaces.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - OFFSET_SURFACE (offset 0.5 from PLANE_SURFACE) IS the
    ADVANCED_FACE.face_geometry; face boundary edge pcurves referencing the
    offset surface IS the mechanism wired into face topology;
    GeomAdaptor_Surface missing offset-surface branch in type switch IS the
    defect.
  - Byte assertions: contains(b'OFFSET_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_SURFACE (0.5 from PLANE_SURFACE) IS
    ADVANCED_FACE.face_geometry; face boundary edge pcurves on offset surface
    IS the mechanism wired into face topology; GeomAdaptor_Surface type-switch
    omission (offset branch missing) IS the defect.
  - shape_null driver: offset surface classified as LOther; downstream
    algorithm confused; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs160",
    defect=(
        "OFFSET_SURFACE (offset 0.5 from PLANE_SURFACE) IS "
        "ADVANCED_FACE.face_geometry; face boundary edge pcurves on offset "
        "surface IS the mechanism wired into face topology; "
        "GeomAdaptor_Surface type-switch missing offset-surface branch IS "
        "the defect; shape_null"
    ),
)

# ── PLANE_SURFACE as offset basis, then OFFSET_SURFACE ────────────────────────
# Byte assertion: contains(b'OFFSET_SURFACE')
# The type switch in GeomAdaptor_Surface has branches for plane/cyl/cone/sphere/
# torus but no offset branch. The offset surface falls to LOther default,
# losing semantic grouping.
plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_norm = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs160_pl_ax',#{plane_orig.eid},#{plane_norm.eid},#{plane_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs160_plane',#{plane_ax.eid})")

# OFFSET_SURFACE(name, basis_surface, distance, self_intersect)
offset_surf = f._emit_raw(
    f"OFFSET_SURFACE('gs160_offset',#{plane.eid},0.5,.F.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square in XY, pcurves in [0,1]x[0,1] ─────────────────
# The offset surface (z=0.5 plane) has same UV parameterization as basis plane.
p_A = f.cartesian_point((0.0, 0.0, 0.5))
p_B = f.cartesian_point((1.0, 0.0, 0.5))
p_C = f.cartesian_point((1.0, 1.0, 0.5))
p_D = f.cartesian_point((0.0, 1.0, 0.5))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{offset_surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom: A→B
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.5), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# Right: B→C
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.5), (0.0, 1.0, 0.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# Top: C→D
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 1.0, 0.5), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# Left: D→A
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 1.0, 0.5), (0.0, -1.0, 0.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# OFFSET_SURFACE IS the face_geometry; face boundary edge pcurves on the offset
# surface IS the mechanism wired into face topology — exercises
# GeomAdaptor_Surface type-switch offset-branch omission.
face  = f.advanced_face([f.face_outer_bound(loop)], offset_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
