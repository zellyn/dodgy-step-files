"""Gs176 — RectangularTrimmedSurface Null Basis.

Catalog claim: Geom_RectangularTrimmedSurface.BasisSurface unwrap skips the
null check after Down_cast succeeds. When BasisSurface() returns null (e.g.
because the underlying B-spline reference has been silently overwritten),
GeomAdaptor dereferences a null pointer, causing undefined behavior. OCC
accepts the trimmed geometry token but produces no coherent shape.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - RECTANGULAR_TRIMMED_SURFACE wrapping a B_SPLINE_SURFACE_WITH_KNOTS
    (3×3 control points, deg-2×2) IS the ADVANCED_FACE.face_geometry;
    face boundary loop wired onto the trimmed surface IS the mechanism
    wired into face topology; BasisSurface() null check omission on the
    trimmed wrapper IS the defect.
  - Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE'),
                     contains(b'B_SPLINE_SURFACE_WITH_KNOTS').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: RECTANGULAR_TRIMMED_SURFACE(B_SPLINE_SURFACE_WITH_KNOTS)
    IS ADVANCED_FACE.face_geometry; face boundary loop IS the mechanism wired
    into face topology; BasisSurface() null-check omission IS the defect.
  - shape_null driver: null basis dereference in GeomAdaptor causes undefined
    behavior; strict kernels produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs176",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE(B_SPLINE_SURFACE_WITH_KNOTS 3×3 deg-2) IS "
        "ADVANCED_FACE.face_geometry; face boundary loop IS the mechanism wired "
        "into face topology; Geom_RectangularTrimmedSurface.BasisSurface() "
        "null-check omission after Down_cast (null basis triggers undefined "
        "GeomAdaptor behavior) IS the defect; shape_null"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS 3×3 control points, deg-2×2 ──────────────────
# Byte assertions: contains(b'RECTANGULAR_TRIMMED_SURFACE'),
#                  contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
#
# A flat 3×3 deg-2 B-spline on [0,1]×[0,1] provides the basis surface.
# The RECTANGULAR_TRIMMED_SURFACE trims it to [0.2,0.8]×[0.2,0.8].
# The null-check defect: when BasisSurface() is called on the trimmed
# surface, the implementation Down_casts and skips the null guard.

# Control points: 3×3 flat grid at z=0
cp_rows = [
    [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 0.0, 0.0)],
    [(0.0, 0.5, 0.0), (0.5, 0.5, 0.0), (1.0, 0.5, 0.0)],
    [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (1.0, 1.0, 0.0)],
]
cp_eids = []
for row in cp_rows:
    row_eids = [f.cartesian_point(pt).eid for pt in row]
    cp_eids.append(row_eids)

# Format control point grid for STEP
cp_grid = "(" + ",".join(
    "(" + ",".join(f"#{e}" for e in row) + ")"
    for row in cp_eids
) + ")"

# Knot vectors for deg-2, 3 control points: [0,0,0,1,1,1] → mults (3,3), knots (0.0,1.0)
bspl = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs176_bspl',2,2,{cp_grid},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# RECTANGULAR_TRIMMED_SURFACE trims the B-spline to [0.2,0.8]×[0.2,0.8]
trimmed = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gs176_trim',#{bspl.eid},"
    f"0.2,0.8,0.2,0.8,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangular loop on trimmed surface [0.2,0.8]×[0.2,0.8] ───
# Corners in 3D (flat z=0 surface):
p_sw = f.cartesian_point((0.2, 0.2, 0.0))
p_se = f.cartesian_point((0.8, 0.2, 0.0))
p_ne = f.cartesian_point((0.8, 0.8, 0.0))
p_nw = f.cartesian_point((0.2, 0.8, 0.0))

v_sw = f.vertex_point(p_sw)
v_se = f.vertex_point(p_se)
v_ne = f.vertex_point(p_ne)
v_nw = f.vertex_point(p_nw)


def mk_edge(vs, ve, p3s, d3, len3, p2s, d2, len2):
    """Build EDGE_CURVE with LINE 3D and LINE pcurve on the trimmed surface."""
    p3 = f.cartesian_point(p3s)
    d3e = f.direction(d3)
    v3 = f.vector(d3e, len3)
    l3 = f.line(p3, v3)
    p2 = f.cartesian_point(p2s)
    d2e = f.direction(d2)
    v2 = f.vector(d2e, len2)
    l2 = f.line(p2, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{trimmed.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# South edge: SW→SE, y=0.2, x: 0.2→0.8
e_s = mk_edge(v_sw, v_se,
              (0.2, 0.2, 0.0), (1.0, 0.0, 0.0), 0.6,
              (0.2, 0.2), (1.0, 0.0), 0.6)
# East edge: SE→NE, x=0.8, y: 0.2→0.8
e_e = mk_edge(v_se, v_ne,
              (0.8, 0.2, 0.0), (0.0, 1.0, 0.0), 0.6,
              (0.8, 0.2), (0.0, 1.0), 0.6)
# North edge: NE→NW, y=0.8, x: 0.8→0.2
e_n = mk_edge(v_ne, v_nw,
              (0.8, 0.8, 0.0), (-1.0, 0.0, 0.0), 0.6,
              (0.8, 0.8), (-1.0, 0.0), 0.6)
# West edge: NW→SW, x=0.2, y: 0.8→0.2
e_w = mk_edge(v_nw, v_sw,
              (0.2, 0.8, 0.0), (0.0, -1.0, 0.0), 0.6,
              (0.2, 0.8), (0.0, -1.0), 0.6)

loop = f.edge_loop([
    f.oriented_edge(e_s, True),
    f.oriented_edge(e_e, True),
    f.oriented_edge(e_n, True),
    f.oriented_edge(e_w, True),
])

# RECTANGULAR_TRIMMED_SURFACE(B_SPLINE_SURFACE_WITH_KNOTS) IS the face_geometry;
# face boundary loop IS the mechanism wired into face topology — exercises
# BasisSurface() null-check omission in Geom_RectangularTrimmedSurface.
face  = f.advanced_face([f.face_outer_bound(loop)], trimmed)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
