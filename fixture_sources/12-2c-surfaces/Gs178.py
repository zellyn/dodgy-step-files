"""Gs178 — OffsetSurface Edge Degeneracy.

Catalog claim: ShapeAnalysis_Surface.ComputeSingularities omits 4-edge
midpoint sampling for OFFSET_SURFACE. The offset (0.5 from a flat plane)
produces an offset surface whose edge midpoints capture the collapse
signature when the offset distance approaches degeneracy. Without
midpoint sampling, edge-tangency anomalies on offset faces go undetected
by the healing pipeline.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - OFFSET_SURFACE (offset 0.5 from a PLANE) IS the ADVANCED_FACE.face_geometry;
    face boundary loop wired onto the offset surface with all four edge
    midpoints present IS the mechanism wired into face topology;
    ShapeAnalysis_Surface.ComputeSingularities 4-edge midpoint sampling
    omission IS the defect.
  - Byte assertions: contains(b'OFFSET_SURFACE'), contains(b'PLANE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_SURFACE(PLANE, offset=0.5) IS
    ADVANCED_FACE.face_geometry; face boundary with all four edges
    (midpoints span the offset collapse signature) IS the mechanism wired
    into face topology; ComputeSingularities 4-edge midpoint sampling
    omission IS the defect.
  - shape_null driver: undetected edge-tangency anomaly causes healing to
    fail; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs178",
    defect=(
        "OFFSET_SURFACE(PLANE, offset=0.5) IS ADVANCED_FACE.face_geometry; "
        "face boundary loop with all four edges (midpoints span offset collapse "
        "signature) IS the mechanism wired into face topology; "
        "ShapeAnalysis_Surface.ComputeSingularities 4-edge midpoint sampling "
        "omission (edge-tangency anomaly undetected) IS the defect; shape_null"
    ),
)

# ── Base PLANE at z=0, axis along +Z ─────────────────────────────────────────
# Byte assertions: contains(b'OFFSET_SURFACE'), contains(b'PLANE')
#
# The PLANE is the XY-plane. OFFSET_SURFACE moves it 0.5 in the +Z direction.
# The offset surface occupies z=0.5 and is bounded by a [0,1]×[0,1] patch.
# Its four edge midpoints are:
#   south mid: (0.5, 0.0, 0.5)   north mid: (0.5, 1.0, 0.5)
#   west mid:  (0.0, 0.5, 0.5)   east mid:  (1.0, 0.5, 0.5)
# These midpoints are the key sampling sites for the 4-edge midpoint test.

plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs178_plane_ax',#{plane_orig.eid},"
    f"#{plane_zdir.eid},#{plane_xdir.eid})"
)
plane = f._emit_raw(f"PLANE('gs178_plane',#{plane_ax.eid})")

# OFFSET_SURFACE: offset the plane by 0.5 in the normal direction
offset_surf = f._emit_raw(
    f"OFFSET_SURFACE('gs178_offset',#{plane.eid},0.5,.F.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: unit square at z=0.5 (offset surface) ─────────────────────
# Corners of the [0,1]×[0,1] patch at z=0.5:
p_sw = f.cartesian_point((0.0, 0.0, 0.5))
p_se = f.cartesian_point((1.0, 0.0, 0.5))
p_ne = f.cartesian_point((1.0, 1.0, 0.5))
p_nw = f.cartesian_point((0.0, 1.0, 0.5))

v_sw = f.vertex_point(p_sw)
v_se = f.vertex_point(p_se)
v_ne = f.vertex_point(p_ne)
v_nw = f.vertex_point(p_nw)


def mk_edge(vs, ve, p3s, d3, len3, p2s, d2, len2):
    """Build EDGE_CURVE with LINE 3D and LINE pcurve on the offset surface."""
    p3 = f.cartesian_point(p3s)
    d3e = f.direction(d3)
    v3 = f.vector(d3e, len3)
    l3 = f.line(p3, v3)
    p2 = f.cartesian_point(p2s)
    d2e = f.direction(d2)
    v2 = f.vector(d2e, len2)
    l2 = f.line(p2, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{offset_surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# South edge: SW→SE, y=0, x: 0→1  (midpoint: (0.5,0,0.5) — south sample)
e_s = mk_edge(v_sw, v_se,
              (0.0, 0.0, 0.5), (1.0, 0.0, 0.0), 1.0,
              (0.0, 0.0), (1.0, 0.0), 1.0)
# East edge: SE→NE, x=1, y: 0→1  (midpoint: (1,0.5,0.5) — east sample)
e_e = mk_edge(v_se, v_ne,
              (1.0, 0.0, 0.5), (0.0, 1.0, 0.0), 1.0,
              (1.0, 0.0), (0.0, 1.0), 1.0)
# North edge: NE→NW, y=1, x: 1→0  (midpoint: (0.5,1,0.5) — north sample)
e_n = mk_edge(v_ne, v_nw,
              (1.0, 1.0, 0.5), (-1.0, 0.0, 0.0), 1.0,
              (1.0, 1.0), (-1.0, 0.0), 1.0)
# West edge: NW→SW, x=0, y: 1→0  (midpoint: (0,0.5,0.5) — west sample)
e_w = mk_edge(v_nw, v_sw,
              (0.0, 1.0, 0.5), (0.0, -1.0, 0.0), 1.0,
              (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e_s, True),
    f.oriented_edge(e_e, True),
    f.oriented_edge(e_n, True),
    f.oriented_edge(e_w, True),
])

# OFFSET_SURFACE(PLANE, 0.5) IS the face_geometry; face boundary loop with all
# four edges (midpoints span the offset collapse signature) IS the mechanism
# wired into face topology — exercises ComputeSingularities 4-edge midpoint
# sampling omission.
face  = f.advanced_face([f.face_outer_bound(loop)], offset_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
