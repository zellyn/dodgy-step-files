"""Pmi056 — Tessellated alongside curve annotations for the same callout (AP242 ed2 conflict).

Catalog claim: A draughting_model mixes tessellated_annotation_occurrence and
curve-style annotation_*_occurrence for the same callout. Even within one PMI
item this duplication breaks counting and association.

Reproducer recipe: One draughting_callout referencing both tessellated and
polyline forms of the same FCF.

Byte assertions:
  contains(b'TESSELLATED_ANNOTATION_OCCURRENCE')
  contains(b'ANNOTATION_CURVE_OCCURRENCE')
  contains(b'COMPLEX_TRIANGULATED_SURFACE_SET')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi056",
    schema="AP242",
    defect=(
        "DRAUGHTING_CALLOUT references both a TESSELLATED_ANNOTATION_OCCURRENCE and "
        "an ANNOTATION_CURVE_OCCURRENCE for the same callout; AP242 ed.2 forbids "
        "mixing tessellated and curve annotation styles for the same PMI item; "
        "this duplication breaks annotation counting and association; receivers must "
        "normalize one form as canonical and warn; silently accepting the duplicate "
        "is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Presentation style (shared).
colour = f._emit_raw("COLOUR_RGB('anno_colour',0.0,0.0,0.0)")
curve_style = f._emit_raw(
    f"CURVE_STYLE('',FONT_SELECT($),LENGTH_MEASURE(0.25),#{colour.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{curve_style.eid}))"
)

# ── Form 1: polyline ANNOTATION_CURVE_OCCURRENCE ─────────────────────────────
pt_a = f.cartesian_point((0.0, 0.0, 0.0))
pt_b = f.cartesian_point((10.0, 0.0, 0.0))
polyline = f._emit_raw(
    f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))"
)
curve_occ = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('fcf_curve',(#{polyline.eid}),#{psa.eid})"
)

# ── Form 2: tessellated TESSELLATED_ANNOTATION_OCCURRENCE (same FCF) ─────────
# COMPLEX_TRIANGULATED_SURFACE_SET: represents the tessellated form of the FCF.
coords = f._emit_raw(
    "COORDINATES_LIST('tess_coords',3,"
    "((0.0,5.0,0.0),(5.0,5.0,0.0),(2.5,8.0,0.0)))"
)
# COMPLEX_TRIANGULATED_SURFACE_SET(name, coordinates, triangles)
ctss = f._emit_raw(
    f"COMPLEX_TRIANGULATED_SURFACE_SET('fcf_tess',#{coords.eid},"
    f"((0,1,2)),.F.,$)"
)
tess_occ = f._emit_raw(
    f"TESSELLATED_ANNOTATION_OCCURRENCE('fcf_tess_occ',(#{psa.eid}),#{ctss.eid})"
)

# Defect: single DRAUGHTING_CALLOUT references BOTH the curve and tessellated
# occurrences for the same FCF — the AP242 ed.2 conflict.
f._emit_raw(
    f"DRAUGHTING_CALLOUT('fcf_callout',(#{curve_occ.eid},#{tess_occ.eid}))"
)
