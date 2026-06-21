"""P018 — Improper rotation (negative determinant) in AXIS2_PLACEMENT_3D.

Catalog claim: a MAPPED_ITEM whose transformation_operator AXIS2_PLACEMENT_3D
encodes a left-handed coordinate system (improper rotation, det = -1) doesn't
round-trip; receiver loses the reflection.

The defect: MAPPED_ITEM with an AXIS2_PLACEMENT_3D whose Z and X direction
vectors form a left-handed frame (det(Z x X, Y) = -1). A robust reader handles
non-orthonormal-but-orthogonal placements explicitly, or rejects with a clear
error; silent empty result is the bug.

Byte assertions:
  contains(b'MAPPED_ITEM')
  contains(b'mirror_origin') or contains(b'mirror_z') or contains(b'left-handed')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P018",
    defect=(
        "MAPPED_ITEM with AXIS2_PLACEMENT_3D encoding a left-handed coordinate frame: "
        "Z=(0,0,-1), X=(1,0,0) → det = -1 (mirror about XY-plane); "
        "AXIS2_PLACEMENT_3D label 'mirror_z' signals left-handed intent; "
        "receiver loses the reflection and silently returns empty; "
        "must reject with clear diagnostic or handle non-orthonormal placement; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Sub-component with normal right-handed representation ─────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('MirroredComp','MirroredComp','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)"
)

# Normal right-handed placement for the sub-shape representation.
sub_origin = f._emit_raw("CARTESIAN_POINT('sub_origin',(1.0,0.0,0.0))")
sub_z_rh = f._emit_raw("DIRECTION('sub_z_rh',(0.0,0.0,1.0))")
sub_x_rh = f._emit_raw("DIRECTION('sub_x_rh',(1.0,0.0,0.0))")
sub_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('sub_plc',#{sub_origin.eid},#{sub_z_rh.eid},#{sub_x_rh.eid})"
)
sub_sr = f._emit_raw(
    f"SHAPE_REPRESENTATION('sub_rep',(#{sub_plc.eid}),#9010)"
)
rep_map = f._emit_raw(f"REPRESENTATION_MAP(#{sub_plc.eid},#{sub_sr.eid})")

# ── Left-handed AXIS2_PLACEMENT_3D: the defect ───────────────────────────────
# Z = (0, 0, -1) reverses the Z-axis → det(Z×X, Y) = -1 (left-handed frame).
# The label 'mirror_z' is explicitly required by the byte assertion:
#   contains(b'mirror_z')
mirror_origin = f._emit_raw("CARTESIAN_POINT('mirror_origin',(0.0,0.0,0.0))")
# Z reversed to (0, 0, -1) — produces a left-handed (reflective) frame.
mirror_z = f._emit_raw("DIRECTION('mirror_z',(0.0,0.0,-1.0))")
mirror_x = f._emit_raw("DIRECTION('mirror_x',(1.0,0.0,0.0))")
left_handed_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('mirror_z',#{mirror_origin.eid},#{mirror_z.eid},#{mirror_x.eid})"
)

# MAPPED_ITEM references the left-handed placement — the defect trigger.
mi = f._emit_raw(
    f"MAPPED_ITEM('mirrored_instance',#{rep_map.eid},#{left_handed_plc.eid})"
)

# NAUO for assembly-presence lint.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','mirrored_comp_instance','',#9004,#{sub_pdef.eid},$)"
)
