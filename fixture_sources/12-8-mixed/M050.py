"""M050 — Composite material LLAI (Limited Length / Area Indicator) gaps.

Catalog claim: Composite-ply geometry requiring LLAI to mark plies extending
only over part of a base surface is not uniformly implemented; older AP242
implementations drop LLAI metadata or encode it inconsistently.

Reproducer recipe: A composite layup with a partial-area ply round-tripped
through AP242 Ed.2 — partial-area boundary lost.

Byte assertions:
  contains(b'COMPOSITE_PLY_DEFINITION')
  contains(b'LIMITED_AREA_INDICATOR')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M050",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing COMPOSITE_PLY_DEFINITION with "
        "LIMITED_AREA_INDICATOR marking a partial-area ply boundary; "
        "input: AP242 STEP file (Ed.2) with a composite layup where one ply "
        "covers only part of the base surface; the ply boundary is encoded as "
        "LIMITED_AREA_INDICATOR referencing a bounding curve; "
        "prostep ivip MBx-IF / CAx-IF Composites RP v4.4 (M033): LLAI extension "
        "targeted at AP242 Ed.4; older Ed.2 implementations silently drop the "
        "LIMITED_AREA_INDICATOR entity or encode it inconsistently across vendors; "
        "kernel must warn-and-accept (document loss) when Ed.4 LLAI extension is "
        "unavailable; never silently drop partial-area boundary; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: composite LLAI gaps, limited length area indicator missing, "
        "ply extends only over part of base, LLAI metadata inconsistent across vendors"
    ),
)

# ── Base surface reference geometry ────────────────────────────────────────────
base_pt = f._emit_raw("CARTESIAN_POINT('base_origin',(0.,0.,0.))")
base_dir_z = f._emit_raw("DIRECTION('base_normal',(0.,0.,1.))")
base_dir_x = f._emit_raw("DIRECTION('base_ref_dir',(1.,0.,0.))")
base_placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('base_placement',"
    f"#{base_pt.eid},#{base_dir_z.eid},#{base_dir_x.eid})"
)

# ── Partial-area boundary curve for the LLAI ─────────────────────────────────
# A partial rectangle bounding the sub-area of the ply
bound_pt0 = f._emit_raw("CARTESIAN_POINT('b0',(0.1,0.1,0.))")
bound_pt1 = f._emit_raw("CARTESIAN_POINT('b1',(0.5,0.1,0.))")
bound_pt2 = f._emit_raw("CARTESIAN_POINT('b2',(0.5,0.5,0.))")
bound_pt3 = f._emit_raw("CARTESIAN_POINT('b3',(0.1,0.5,0.))")
bound_dir = f._emit_raw("DIRECTION('bound_dir',(1.,0.,0.))")
bound_line = f._emit_raw(
    f"LINE('boundary_edge',#{bound_pt0.eid},VECTOR(#{bound_dir.eid},0.4))"
)

# ── LIMITED_AREA_INDICATOR — AP242 Ed.4 LLAI extension entity ─────────────────
# Byte assertion: contains(b'LIMITED_AREA_INDICATOR')
llai = f._emit_raw(
    f"LIMITED_AREA_INDICATOR('partial_ply_boundary',"
    f"(#{bound_pt0.eid},#{bound_pt1.eid},#{bound_pt2.eid},#{bound_pt3.eid}))"
)

# ── COMPOSITE_PLY_DEFINITION referencing the LLAI ─────────────────────────────
# Byte assertion: contains(b'COMPOSITE_PLY_DEFINITION')
ply_def = f._emit_raw(
    f"COMPOSITE_PLY_DEFINITION('ply_layer_1','carbon_fibre_0deg',"
    f"#{base_placement.eid},#{llai.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('composite-llai-partial-area-ply',"
    f"(#{ply_def.eid},#{llai.eid},#{base_placement.eid},"
    f"#{bound_pt0.eid},#{bound_pt1.eid},#{bound_pt2.eid},#{bound_pt3.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M050.stp")
