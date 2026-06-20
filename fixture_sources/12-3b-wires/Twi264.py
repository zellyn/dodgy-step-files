"""Twi264 — FixConnected gap-skip

Catalog claim: Wire with vertex mismatch at edge junction; FixConnected skips
repair when vertices within tolerance but unequal.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with two edges
'conn_e1' and 'conn_e2'. The edges share a junction where the end vertex of
conn_e1 and the start vertex of conn_e2 are distinct VERTEX_POINT entities
both placed at (1.0, 0.0, 0.0) — within tolerance but not the same entity.
ShapeFix_Wire::FixConnected is supposed to merge such near-coincident vertices,
but skips repair when the gap is below the precision threshold yet the vertices
are not identical pointers. The distinct-but-coincident vertex pair IS the
gap-skip defect trigger. GEOMETRIC_CURVE_SET yields empty on import.

Byte assertions:
  - contains(b'conn_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi264",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with two edges sharing coincident but distinct junction vertices; "
        "conn_e1: (0,0,0)->(1,0,0) end vertex vV1a; conn_e2: start vertex vV1b at (1,0,0)->(2,0,0); "
        "vV1a and vV1b are distinct VERTEX_POINT entities placed at identical coordinates; "
        "FixConnected skips repair when vertices within tolerance but unequal pointers IS gap-skip defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# conn_e1: (0,0,0) -> (1,0,0) — end at vV1a
vV0  = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1a = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))  # end of conn_e1

# conn_e2: (1,0,0) -> (2,0,0) — start at vV1b (distinct entity, same coords)
vV1b = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))  # start of conn_e2 — gap-skip trigger
vV2  = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))

# conn_e1: V0 -> V1a
d1  = f.direction((1.0, 0.0, 0.0))
v1  = f.vector(d1, 1.0)
ln1 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), v1)
ec1 = f._emit_raw(
    f"EDGE_CURVE('conn_e1',#{vV0.eid},#{vV1a.eid},#{ln1.eid},.T.)"
)

# conn_e2: V1b -> V2 (V1b distinct from V1a IS the defect)
d2  = f.direction((1.0, 0.0, 0.0))
v2  = f.vector(d2, 1.0)
ln2 = f.line(f.cartesian_point((1.0, 0.0, 0.0)), v2)
ec2 = f._emit_raw(
    f"EDGE_CURVE('conn_e2',#{vV1b.eid},#{vV2.eid},#{ln2.eid},.T.)"
)

oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi264.stp")
