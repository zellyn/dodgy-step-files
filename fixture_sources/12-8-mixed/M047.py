"""M047 — Texture / bitmap (IMAGE_TEXTURE / TEXTURE_MAPPING) loss on translation.

Catalog claim: Image textures and UV mappings lost when exporting to a
tessellated format that supposedly supports them.

Reproducer recipe: A face with a TEXTURE_MAPPING referencing an IMAGE_TEXTURE
exported through a STEP pipeline.

Byte assertions:
  contains(b'IMAGE_TEXTURE')
  contains(b'TEXTURE_MAPPING')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M047",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing IMAGE_TEXTURE with TEXTURE_MAPPING on a "
        "face — UV texture reference lost on STEP translation; "
        "input: AP242 STEP file where a face carries a TEXTURE_MAPPING referencing "
        "an IMAGE_TEXTURE with embedded bitmap path and UV coordinate list; "
        "HOOPS Exchange 2025.1.0 SDHE-21230 (W025): image textures and UV mappings "
        "are silently dropped when exporting to tessellated formats that claim support; "
        "kernel must preserve UV coordinates and image reference (or warn on "
        "unsupported texture types) rather than silently drop; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: texture lost on translation, IMAGE_TEXTURE not preserved, "
        "UV mapping dropped, bitmap material lost"
    ),
)

# ── IMAGE_TEXTURE referencing a bitmap path ───────────────────────────────────
# Byte assertion: contains(b'IMAGE_TEXTURE')
image_texture = f._emit_raw(
    "IMAGE_TEXTURE('diffuse_map','./textures/surface_diffuse.png')"
)

# ── UV coordinate list for the mapping ───────────────────────────────────────
uv_pt0 = f._emit_raw("CARTESIAN_POINT('uv0',(0.,0.,0.))")
uv_pt1 = f._emit_raw("CARTESIAN_POINT('uv1',(1.,0.,0.))")
uv_pt2 = f._emit_raw("CARTESIAN_POINT('uv2',(1.,1.,0.))")
uv_pt3 = f._emit_raw("CARTESIAN_POINT('uv3',(0.,1.,0.))")

# ── Face geometry anchor point ────────────────────────────────────────────────
face_origin = f._emit_raw("CARTESIAN_POINT('face_origin',(0.,0.,0.))")
face_dir_z = f._emit_raw("DIRECTION('face_normal',(0.,0.,1.))")
face_dir_x = f._emit_raw("DIRECTION('face_ref_dir',(1.,0.,0.))")
face_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('face_placement',"
    f"#{face_origin.eid},#{face_dir_z.eid},#{face_dir_x.eid})"
)

# ── TEXTURE_MAPPING associating the image with the face placement ─────────────
# Byte assertion: contains(b'TEXTURE_MAPPING')
texture_mapping = f._emit_raw(
    f"TEXTURE_MAPPING(#{image_texture.eid},#{face_placement.eid},"
    f"(#{uv_pt0.eid},#{uv_pt1.eid},#{uv_pt2.eid},#{uv_pt3.eid}))"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('texture-bitmap-lost-on-translation',"
    f"(#{image_texture.eid},#{texture_mapping.eid},#{face_placement.eid},"
    f"#{uv_pt0.eid},#{uv_pt1.eid},#{uv_pt2.eid},#{uv_pt3.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M047.stp")
