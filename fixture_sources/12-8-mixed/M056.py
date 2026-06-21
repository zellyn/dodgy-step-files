"""M056 — Tessellation export missing or conflicting with B-rep representation.

Catalog claim: For some assemblies tessellation data is omitted on save.
Conversely, files providing only tessellation when a B-rep consumer expects
B-rep appear empty. Mixing tessellated_annotation_occurrence with curve-style
annotation occurrences for the same callout is not interoperable.

Reproducer recipe: AP242 file with only TESSELLATED_SOLID entities and no
MANIFOLD_SOLID_BREP; or draughting model that mixes
tessellated_annotation_occurrence with curve-based annotation occurrences for
the same callout.

Byte assertions:
  contains(b'TESSELLATED_SHAPE_REPRESENTATION')
  contains(b'TESSELLATED_ANNOTATION_OCCURRENCE')
  contains(b'GEOMETRIC_CURVE_SET')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M056",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file that mixes TESSELLATED_SHAPE_REPRESENTATION "
        "with TESSELLATED_ANNOTATION_OCCURRENCE and curve-based annotation for the "
        "same callout — tessellation-only B-rep consumer sees empty; "
        "input: AP242 STEP file providing tessellation (TESSELLATED_SHAPE_REPRESENTATION) "
        "without any MANIFOLD_SOLID_BREP; the draughting model mixes "
        "TESSELLATED_ANNOTATION_OCCURRENCE with CURVE_STYLE annotation occurrences for "
        "the same dimension callout — interoperability failure; "
        "SolidWorks 2022 SP1/SP2 regression (V041): tessellation omitted on save; "
        "HOOPS Exchange (W035): mixed tessellated+curve annotation not parsed; "
        "NIST SFA 3.7 (S068): graphical PMI tessellation absent; "
        "ISO 10303-59 §6.1: TESSELLATED_SHAPE_REPRESENTATION items must be "
        "tessellated_representation_item subtypes only; "
        "kernel must warn-and-accept on mixed presentation; surface clear "
        "'no B-rep data' diagnostic; never silently drop tessellation-only file; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: tessellation export missing, B-rep and tessellation conflict, "
        "graphical_pmi tessellation absent, preview mesh not in STEP file"
    ),
)

# ── Tessellated solid geometry — 2 triangle fan around origin ─────────────────
coords = f._emit_raw(
    "COORDINATES_LIST('tess_coords',3,"
    "((0.,0.,0.),(10.,0.,0.),(0.,10.,0.),(0.,0.,10.)))"
)
tess_face = f._emit_raw(
    f"TRIANGULATED_FACE('tess_face',#{coords.eid},.F.,"
    f"((0,1,2),(0,2,3)),$)"
)
# Byte assertion: contains(b'TESSELLATED_SHAPE_REPRESENTATION')
tess_solid = f._emit_raw(
    f"TESSELLATED_SOLID('tess_solid',#{tess_face.eid},$)"
)

# ── Representation context ────────────────────────────────────────────────────
geom_ctx = f._emit_raw(
    "GEOMETRIC_REPRESENTATION_CONTEXT(3)"
)
# Byte assertion: contains(b'TESSELLATED_SHAPE_REPRESENTATION') — emitted here
tsr = f._emit_raw(
    f"TESSELLATED_SHAPE_REPRESENTATION('',(#{tess_solid.eid}),#{geom_ctx.eid})"
)

# ── Curve-style annotation for the same callout (mixed-mode interop failure) ──
ann_origin = f._emit_raw("CARTESIAN_POINT('ann_origin',(5.,5.,0.))")
ann_dir = f._emit_raw("DIRECTION('ann_dir',(1.,0.,0.))")
ann_vec = f._emit_raw(f"VECTOR(#{ann_dir.eid},5.)")
ann_line = f._emit_raw(f"LINE('ann_leader',#{ann_origin.eid},#{ann_vec.eid})")
ann_curve_style = f._emit_raw(
    "CURVE_STYLE('dim_leader_style',$,POSITIVE_LENGTH_MEASURE(0.25),$)"
)
ann_occ = f._emit_raw(
    f"ANNOTATION_CURVE_OCCURRENCE('dim_leader',(#{ann_curve_style.eid}),#{ann_line.eid})"
)

# ── TESSELLATED_ANNOTATION_OCCURRENCE for the same callout (the conflict) ─────
# Byte assertion: contains(b'TESSELLATED_ANNOTATION_OCCURRENCE')
tess_ann = f._emit_raw(
    f"TESSELLATED_ANNOTATION_OCCURRENCE('dim_leader_tess',(#{tess_face.eid}),$)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('tessellation-missing-or-conflicting-with-brep',"
    f"(#{tess_solid.eid},#{tsr.eid},#{ann_occ.eid},#{tess_ann.eid},"
    f"#{ann_origin.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M056.stp")
