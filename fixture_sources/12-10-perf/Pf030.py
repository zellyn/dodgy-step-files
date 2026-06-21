"""Pf030 — Schema-EXPRESS WHERE-rule evaluation bomb (billion-laughs analogue).

Catalog claim: ISO 10303-11 EXPRESS WHERE-rule evaluation can be
combinatorially explosive on hand-crafted entity graphs that force
re-evaluation across thousands of cross-referenced instances — analogous to
XML billion-laughs. Each level expands to N peer instances; total work is N^depth.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 3
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf030",
    defect=(
        "Schema-EXPRESS WHERE-rule evaluation bomb: GEOMETRIC_SET entities cross-reference "
        "each other in a 4-level fan-out tree (width 4, depth 4 = 256 atom visits per L4 "
        "set); a WHERE rule that walks transitively evaluates O(N^depth) times without "
        "memoization; scale to width 10 depth 10 for production billion-laughs; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Base atoms - 4 CARTESIAN_POINTs (level 0)
p1 = f.cartesian_point((0.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 0.0, 0.0))
p3 = f.cartesian_point((2.0, 0.0, 0.0))
p4 = f.cartesian_point((3.0, 0.0, 0.0))

# Level 1: four GEOMETRIC_SETs each containing the 4 base points
refs0 = f"#{p1.eid},#{p2.eid},#{p3.eid},#{p4.eid}"
l1a = f._emit_raw(f"GEOMETRIC_SET('L1a',({refs0}))")
l1b = f._emit_raw(f"GEOMETRIC_SET('L1b',({refs0}))")
l1c = f._emit_raw(f"GEOMETRIC_SET('L1c',({refs0}))")
l1d = f._emit_raw(f"GEOMETRIC_SET('L1d',({refs0}))")

# Level 2: each set aggregates all 4 level-1 sets (4x4 = 16 atom visits each)
refs1 = f"#{l1a.eid},#{l1b.eid},#{l1c.eid},#{l1d.eid}"
l2a = f._emit_raw(f"GEOMETRIC_SET('L2a',({refs1}))")
l2b = f._emit_raw(f"GEOMETRIC_SET('L2b',({refs1}))")
l2c = f._emit_raw(f"GEOMETRIC_SET('L2c',({refs1}))")
l2d = f._emit_raw(f"GEOMETRIC_SET('L2d',({refs1}))")

# Level 3: aggregates level-2 (4^3 = 64 atom visits each)
refs2 = f"#{l2a.eid},#{l2b.eid},#{l2c.eid},#{l2d.eid}"
l3a = f._emit_raw(f"GEOMETRIC_SET('L3a',({refs2}))")
l3b = f._emit_raw(f"GEOMETRIC_SET('L3b',({refs2}))")
l3c = f._emit_raw(f"GEOMETRIC_SET('L3c',({refs2}))")
l3d = f._emit_raw(f"GEOMETRIC_SET('L3d',({refs2}))")

# Level 4: aggregates level-3 (4^4 = 256 atom visits each)
refs3 = f"#{l3a.eid},#{l3b.eid},#{l3c.eid},#{l3d.eid}"
l4a = f._emit_raw(f"GEOMETRIC_SET('L4a',({refs3}))")
l4b = f._emit_raw(f"GEOMETRIC_SET('L4b',({refs3}))")
l4c = f._emit_raw(f"GEOMETRIC_SET('L4c',({refs3}))")
l4d = f._emit_raw(f"GEOMETRIC_SET('L4d',({refs3}))")

# GEOMETRIC_CURVE_SET as the product entity (makes OCC yield empty)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{p1.eid}))")
f.add_product_chain(gcs)
