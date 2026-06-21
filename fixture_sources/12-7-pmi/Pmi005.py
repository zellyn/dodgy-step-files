"""Pmi005 — Mixing Polyline and Tessellated PMI presentation in one file.

Catalog claim: AP242 permits both polyline ANNOTATION_CURVE_OCCURRENCE and
TESSELLATED_ANNOTATION_OCCURRENCE, but most viewers pick one representation
and silently drop the other. A file mixing both is interoperability-hostile.

Reproducer: two annotations under the same draughting_model — one realized
as basic polylines, the other as tessellated triangles.

Byte assertions:
  contains(b'TESSELLATED_ANNOTATION_OCCURRENCE')
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  contains(b'TRIANGULATED_FACE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi005",
    schema="AP242",
    defect=(
        "polyline ANNOTATION_CURVE_OCCURRENCE and TESSELLATED_ANNOTATION_OCCURRENCE "
        "mixed under the same DRAUGHTING_MODEL; viewers pick one and drop the other; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9060=geom_ctx

# Presentation style.
pres_style = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── Annotation 1: polyline ANNOTATION_CURVE_OCCURRENCE ───────────────────────
pl_p1 = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
pl_p2 = f._emit_raw("CARTESIAN_POINT('',(10.0,0.0,0.0))")
polyline = f._emit_raw(
    f"POLYLINE('diam_line',(#{pl_p1.eid},#{pl_p2.eid}))"
)
curve_occ = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('diam_polyline_occ',(#{pres_style.eid}),#{polyline.eid})"
)

# ── Annotation 2: tessellated TESSELLATED_ANNOTATION_OCCURRENCE ──────────────
# Minimal TRIANGULATED_FACE: 3 coords, 1 triangle.
# coordinates_list: 3 points
coords = f._emit_raw(
    "COORDINATES_LIST('tess_coords',3,"
    "((0.0,5.0,0.0),(5.0,5.0,0.0),(2.5,8.0,0.0)))"
)
# TRIANGULATED_FACE: name, coordinates, normal_count, normals, triangle_count, triangles
tess_face = f._emit_raw(
    f"TRIANGULATED_FACE('tess_face',#{coords.eid},$,$,"
    f"1,((1,2,3)))"
)
tess_occ = f._emit_raw(
    f"TESSELLATED_ANNOTATION_OCCURRENCE('par_tess_occ',(#{pres_style.eid}),#{tess_face.eid})"
)

# Both under the same DRAUGHTING_MODEL — the defect.
f._emit_raw(
    f"DRAUGHTING_MODEL('mixed_pmi',(#{curve_occ.eid},#{tess_occ.eid}),#9060)"
)
