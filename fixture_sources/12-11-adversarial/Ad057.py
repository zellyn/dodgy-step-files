"""Ad057 — Memory leak / unbounded RSS after STEP assembly read.

Catalog claim: typed-value / enum tables not freed — every distinct BOOLEAN
slot (.T. / .F.) parsed grows a per-process table that isn't released.
Common stress shape: many EDGE_CURVE entries with alternating .T./.F.
BOOLEAN orientation slots stress the enum-table allocator; RSS does not
return to baseline after read+destruct.

Reproducer recipe: ReadFile→Transfer→destruct; observe RSS; file contains
many EDGE_CURVE entries with alternating .T./.F. orientation fields.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') >= 5
  count(b'.T.') + count(b'.F.') >= 5

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad057",
    defect=(
        "memory leak / unbounded RSS: typed-value/enum tables not freed; "
        "each distinct BOOLEAN .T./.F. slot grows per-process table; "
        "ShapeFix on huge shells also leaks; "
        "LSAN reports STEPControl_Controller::Init enum allocations; "
        "See also Ad027; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: many EDGE_CURVE entities with alternating .T./.F. BOOLEAN
# orientation slots to stress the enum-table allocator.
# We need shared VERTEX_POINT endpoints for the edges.
hub_a = f.cartesian_point((0.0, 0.0, 0.0))
hub_b = f.cartesian_point((1.0, 0.0, 0.0))
va = f.vertex_point(hub_a)
vb = f.vertex_point(hub_b)

# 20 EDGE_CURVEs — satisfies count_entity_def(b'EDGE_CURVE') >= 5.
# Alternating .T./.F. satisfies count(b'.T.') + count(b'.F.') >= 5.
N = 20
for i in range(N):
    pt = f._emit_raw(f"CARTESIAN_POINT('p{i}',({float(i) * 0.1},0.0,0.0))")
    d = f._emit_raw("DIRECTION('d',(1.,0.,0.))")
    vec = f._emit_raw(f"VECTOR(#{d.eid},1.0)")
    ln = f._emit_raw(f"LINE(#{pt.eid},#{vec.eid})")
    # Alternate between .T. and .F. to stress the enum-table allocator.
    orientation = ".T." if i % 2 == 0 else ".F."
    f._emit_raw(
        f"EDGE_CURVE('ec{i}',#{va.eid},#{vb.eid},#{ln.eid},{orientation})"
    )
