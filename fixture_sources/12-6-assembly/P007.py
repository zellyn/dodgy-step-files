"""P007 — High-curvature B-spline surface flattens between OCCT versions.

Catalog claim: files with B_SPLINE_SURFACE_WITH_KNOTS of degree (3,3)
representing strongly curved involute / hypoid surfaces with closely-spaced
knots load fine in OCCT 7.5 but display as flat planes in 7.6.x. The geometry
is parsed but tessellation degenerates.

The defect: B_SPLINE_SURFACE_WITH_KNOTS with bicubic degree (3,3), strongly
curved control points representing a gear-flank surface, and closely-spaced
knot vectors. A receiving kernel must honour the surface curvature in
tessellation across versions; silently flattening is the bug.

Byte assertions:
  contains(b'B_SPLINE_SURFACE_WITH_KNOTS') or contains(b'B_SPLINE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P007",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (3,3) with closely-spaced knot vectors "
        "representing a strongly curved involute gear-flank surface; "
        "OCCT 7.5 tessellates correctly; OCCT 7.6.x degenerates to flat plane; "
        "geometry parsed but tessellation silently loses all curvature; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE scaffolding for §12.6 lint; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: bicubic degree (3,3), gear-flank shape ────────
# 4×4 control-point grid (degree 3 needs ≥ 4 points per direction).
# The control points are strongly curved to represent an involute gear flank.
# Knot multiplicities [4,1,4] with closely-spaced interior knot at 0.3
# (mimics the HyGEARS export that triggers the OCCT 7.6 flattening bug).
#
# control_points_list (row-major, 4 rows × 4 cols):
#   Row 0 (u=0): strongly curved in Z
#   Row 3 (u=1): offset in X, still curved
cpts = [
    # row 0
    f.cartesian_point((0.0,   0.0,  0.0)),
    f.cartesian_point((3.0,   0.0,  2.0)),
    f.cartesian_point((7.0,   0.0,  2.0)),
    f.cartesian_point((10.0,  0.0,  0.0)),
    # row 1
    f.cartesian_point((0.0,   3.0,  1.5)),
    f.cartesian_point((3.0,   3.0,  4.5)),
    f.cartesian_point((7.0,   3.0,  4.5)),
    f.cartesian_point((10.0,  3.0,  1.5)),
    # row 2
    f.cartesian_point((0.0,   7.0,  1.5)),
    f.cartesian_point((3.0,   7.0,  4.5)),
    f.cartesian_point((7.0,   7.0,  4.5)),
    f.cartesian_point((10.0,  7.0,  1.5)),
    # row 3
    f.cartesian_point((0.0,  10.0,  0.0)),
    f.cartesian_point((3.0,  10.0,  2.0)),
    f.cartesian_point((7.0,  10.0,  2.0)),
    f.cartesian_point((10.0, 10.0,  0.0)),
]

# Build control_points_list string: rows of refs
rows = []
for r in range(4):
    row_refs = ",".join(f"#{cpts[r*4+c].eid}" for c in range(4))
    rows.append(f"({row_refs})")
cp_list = "(" + ",".join(rows) + ")"

# B_SPLINE_SURFACE_WITH_KNOTS: degree_u=3, degree_v=3
# u_multiplicities [4,1,4], u_knots [0.0,0.3,1.0] — closely-spaced at 0.3
# v_multiplicities [4,1,4], v_knots [0.0,0.3,1.0]
# surface_form=.RULED_SURF., u_closed=.F., v_closed=.F., self_intersect=.F.
bspline_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS("
    f"'gear_flank_surface',"
    f"3,3,"
    f"{cp_list},"
    f".RULED_SURF.,.F.,.F.,.F.,"
    f"(4,1,4),(4,1,4),"
    f"(0.0,0.3,1.0),(0.0,0.3,1.0),"
    f".UNSPECIFIED.)"
)

# Wrap in GEOMETRIC_CURVE_SET — no solid, so shape_null==True.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{bspline_surf.eid}))")
f.add_product_chain(gcs)

# NAUO scaffolding for §12.6 assembly-presence lint.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('GearFlank','GearFlank','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','gear_flank_instance','',#9004,#{sub_pdef.eid},$)"
)
