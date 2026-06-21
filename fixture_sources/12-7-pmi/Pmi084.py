"""Pmi084 — Coordinate-system connection points for dimensions missing.

Catalog claim: AP242 dimensions reference coordinate-system connection
points (PRESENTED_ITEM chains pointing to AXIS2_PLACEMENT_3D anchors).
Older readers ignore the chain; the dimension's anchor falls back to the
part origin, which displaces text away from the dimensioned feature.

Reproducer recipe: PMI dimension with explicit connection-point chain
through three intermediate placements. Reader resolves only the leaf and
ignores the chain.

Byte assertions:
  count_entity_def(b'AXIS2_PLACEMENT_3D') == 3
  contains(b'DIMENSIONAL_LOCATION')
  contains(b'PRESENTED_ITEM_REPRESENTATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi084",
    schema="AP242",
    defect=(
        "DIMENSIONAL_LOCATION 'length_dim' has a connection-point chain through "
        "three AXIS2_PLACEMENT_3D anchors expressed via PRESENTED_ITEM_REPRESENTATION; "
        "older readers that do not walk the full chain fall back to the part origin "
        "(0,0,0) instead of the correct attachment point at (50,0,0); receivers must "
        "compose all transforms in the PRESENTED_ITEM chain to resolve the final "
        "dimension anchor; silently using the raw leaf placement without the chain "
        "is forbidden; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# ── Two SHAPE_ASPECTs for the two ends of the dimension ───────────────────────
asp_start = f._emit_raw("SHAPE_ASPECT('dim_start','start feature',#9055,.T.)")
asp_end = f._emit_raw("SHAPE_ASPECT('dim_end','end feature',#9055,.T.)")

# ── DIMENSIONAL_LOCATION (byte assertion: contains) ───────────────────────────
dim_loc = f._emit_raw(
    f"DIMENSIONAL_LOCATION('length_dim','linear distance',"
    f"#{asp_start.eid},#{asp_end.eid})"
)

# ── Three AXIS2_PLACEMENT_3D anchors (byte assertion: count == 3) ─────────────
# Chain: plc_a → plc_b → plc_c; leaf is plc_c at (50,0,0).
# Older readers resolve only plc_c and place text at (50,0,0);
# correct behaviour composes the full chain.
n1 = f._emit_raw("DIRECTION('n1',(0.0,0.0,1.0))")
x1 = f._emit_raw("DIRECTION('x1',(1.0,0.0,0.0))")
o1 = f._emit_raw("CARTESIAN_POINT('o1',(0.0,0.0,0.0))")
plc_a = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('anchor_a',#{o1.eid},#{n1.eid},#{x1.eid})"
)

n2 = f._emit_raw("DIRECTION('n2',(0.0,0.0,1.0))")
x2 = f._emit_raw("DIRECTION('x2',(1.0,0.0,0.0))")
o2 = f._emit_raw("CARTESIAN_POINT('o2',(25.0,0.0,0.0))")
plc_b = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('anchor_b',#{o2.eid},#{n2.eid},#{x2.eid})"
)

n3 = f._emit_raw("DIRECTION('n3',(0.0,0.0,1.0))")
x3 = f._emit_raw("DIRECTION('x3',(1.0,0.0,0.0))")
o3 = f._emit_raw("CARTESIAN_POINT('o3',(50.0,0.0,0.0))")
plc_c = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('anchor_c',#{o3.eid},#{n3.eid},#{x3.eid})"
)

# ── Connection-point representation for the chain ─────────────────────────────
# PRESENTED_ITEM links the dimension to its connection-point placements.
cp_rep = f._emit_raw(
    f"REPRESENTATION('conn_pt_rep',(#{plc_a.eid},#{plc_b.eid},#{plc_c.eid}),$)"
)

# ── PRESENTED_ITEM_REPRESENTATION (byte assertion: contains) ──────────────────
# DEFECT: readers that ignore this entity lose the chain and misplace dim text.
f._emit_raw(
    f"PRESENTED_ITEM_REPRESENTATION(#{cp_rep.eid},#{dim_loc.eid})"
)
