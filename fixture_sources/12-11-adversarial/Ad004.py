"""Ad004 — Cyclic complex-entity reference graph causes infinite recursion.

Catalog claim: complex entity #A=(B(..) C(#A)) references itself, or longer
cycle #A→#B→…→#A. Resolver recurses until stack exhausted. Three cycle
patterns are present, including a REPRESENTATION_RELATIONSHIP to satisfy the
byte assertion regex.

Byte assertions:
  matches(rb'(?s)#\\d+=\\([A-Z_]+\\([^)]*\\)[^;]+#\\d+[^;]+\\);.*REPRESENTATION_RELATIONSHIP')
  matches(rb'#\\d+=\\(')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad004",
    defect=(
        "cyclic complex-entity reference graph; "
        "self-cycle in complex entity; two-node cycle; "
        "cycle via REPRESENTATION_RELATIONSHIP; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payloads:
# (1) Self-cycle: complex entity whose sub-entity references the outer ID.
# We need to know the next ID before emitting. f._next_id gives us that.
self_id = f._next_id
# Emit: #self_id=(NAMED_UNIT(*) DERIVED_UNIT_ELEMENT(#self_id, 1.0));
# This satisfies matches(rb'#\d+=\(') and the (?s) multi-line regex when
# combined with REPRESENTATION_RELATIONSHIP emitted below.
f._emit_raw(f"(NAMED_UNIT(*) DERIVED_UNIT_ELEMENT(#{self_id}, 1.0))")

# (2) Two-node cycle between regular (non-complex) entities.
node_a_id = f._next_id       # e.g. self_id + 1
node_b_id = node_a_id + 1   # e.g. self_id + 2
f._emit_raw(f"GROUP_ASSIGNMENT(#{node_b_id})")
f._emit_raw(f"GROUP_ASSIGNMENT(#{node_a_id})")

# (3) Cycle involving REPRESENTATION_RELATIONSHIP (required by byte assertion).
# Two SHAPE_REPRESENTATIONs cross-linked by two REPRESENTATION_RELATIONSHIPs.
geom_ctx_id = f._next_id
f._emit_raw("AXIS2_PLACEMENT_3D('',#1,$,$)")  # #1 = origin (CARTESIAN_POINT)

sr_a_id = f._next_id
f._emit_raw(f"SHAPE_REPRESENTATION('a',(#{origin.eid}),#{geom_ctx_id})")
sr_b_id = f._next_id
f._emit_raw(f"SHAPE_REPRESENTATION('b',(#{origin.eid}),#{geom_ctx_id})")

f._emit_raw(
    f"REPRESENTATION_RELATIONSHIP('forward','',#{sr_a_id},#{sr_b_id})"
)
f._emit_raw(
    f"REPRESENTATION_RELATIONSHIP('back','',#{sr_b_id},#{sr_a_id})"
)
