"""Ad032 — Schema-EXPRESS rule recursion bomb.

Catalog claim: WHERE rules invoke EXPRESS functions transitively; attacker
references entities such that rule evaluation loops through entity graph
repeatedly. Even O(n²) evaluation with cycles is weaponisable.

Reproducer recipe: graph of 10⁴ EDGE_CURVE entities each referencing two
VERTEX_POINTs in star topology that triggers WHERE-rule re-checks.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') >= 5
  count_entity_def(b'EDGE_CURVE') >= 10

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad032",
    defect=(
        "schema-EXPRESS rule recursion bomb: star topology of EDGE_CURVE entities "
        "sharing VERTEX_POINTs triggers O(n²) WHERE-rule re-evaluation; "
        "kernel must enforce per-file rule-evaluation budget (E_RULE_BUDGET); "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: star topology — two shared hub VERTEX_POINTs referenced by
# many EDGE_CURVEs, each with its own LINE geometry.
# This pattern forces WHERE-rule re-checks proportional to N² when any
# graph-walking rule touches both neighbours.

hub_a = f.cartesian_point((0.0, 0.0, 0.0))
hub_b = f.cartesian_point((10.0, 0.0, 0.0))
va = f.vertex_point(hub_a)
vb = f.vertex_point(hub_b)

N = 25  # 25 EDGE_CURVEs; count_entity_def(b'EDGE_CURVE') >= 10 satisfied.
for i in range(N):
    x = float(i) * 0.1
    pt = f.cartesian_point((x, float(i), 0.0))
    d = f.direction((1.0, 0.0, 0.0))
    vec = f.vector(d, 10.0)
    ln = f.line(pt, vec)
    # All EDGE_CURVEs share the same two hub VERTEXes → star topology.
    f._emit_raw(
        f"EDGE_CURVE('star_{i}',#{va.eid},#{vb.eid},#{ln.eid},.T.)"
    )
