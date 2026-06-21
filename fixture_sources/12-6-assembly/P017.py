"""P017 — Free wires in a top-level COMPOUND silently dropped.

Catalog claim: STEP file with a top-level COMPOUND mixing solids and free
EDGE_CURVE / WIRE items at the same level. With importer's "compound merge"
preference OFF, loose edges are dropped silently.

The defect: a SHAPE_REPRESENTATION containing both a solid-like entity and
free-standing EDGE_CURVE / VERTEX_POINT items at the same level. Compliant
importers must preserve free wires in the top-level COMPOUND; silent drop
is the bug.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') >= 2
  count_entity_def(b'VERTEX_POINT') >= 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P017",
    defect=(
        "SHAPE_REPRESENTATION at top-level mixes free-standing EDGE_CURVE + "
        "VERTEX_POINT wire entities alongside a geometric body; "
        "importers with 'compound merge' ON silently drop the free wires; "
        "compliant receiver must preserve all wire items in top-level COMPOUND; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Free-standing VERTEX_POINT + EDGE_CURVE entities (the defect) ─────────────
# Wire 1: a free edge from (0,0,0) to (5,0,0).
w1_p0 = f._emit_raw("CARTESIAN_POINT('wire1_p0',(0.0,0.0,0.0))")
w1_p1 = f._emit_raw("CARTESIAN_POINT('wire1_p1',(5.0,0.0,0.0))")
w1_v0 = f._emit_raw(f"VERTEX_POINT('wire1_v0',#{w1_p0.eid})")
w1_v1 = f._emit_raw(f"VERTEX_POINT('wire1_v1',#{w1_p1.eid})")
w1_dir = f._emit_raw("DIRECTION('wire1_dir',(1.0,0.0,0.0))")
w1_vec = f._emit_raw(f"VECTOR('',#{w1_dir.eid},5.0)")
w1_line = f._emit_raw(f"LINE('wire1_line',#{w1_p0.eid},#{w1_vec.eid})")
w1_edge = f._emit_raw(
    f"EDGE_CURVE('wire1_edge',#{w1_v0.eid},#{w1_v1.eid},#{w1_line.eid},.T.)"
)

# Wire 2: a free edge from (0,1,0) to (3,1,0).
w2_p0 = f._emit_raw("CARTESIAN_POINT('wire2_p0',(0.0,1.0,0.0))")
w2_p1 = f._emit_raw("CARTESIAN_POINT('wire2_p1',(3.0,1.0,0.0))")
w2_v0 = f._emit_raw(f"VERTEX_POINT('wire2_v0',#{w2_p0.eid})")
w2_v1 = f._emit_raw(f"VERTEX_POINT('wire2_v1',#{w2_p1.eid})")
w2_dir = f._emit_raw("DIRECTION('wire2_dir',(1.0,0.0,0.0))")
w2_vec = f._emit_raw(f"VECTOR('',#{w2_dir.eid},3.0)")
w2_line = f._emit_raw(f"LINE('wire2_line',#{w2_p0.eid},#{w2_vec.eid})")
w2_edge = f._emit_raw(
    f"EDGE_CURVE('wire2_edge',#{w2_v0.eid},#{w2_v1.eid},#{w2_line.eid},.T.)"
)

# Wire 3: a diagonal free edge from (1,0,0) to (4,3,0).
w3_p0 = f._emit_raw("CARTESIAN_POINT('wire3_p0',(1.0,0.0,0.0))")
w3_p1 = f._emit_raw("CARTESIAN_POINT('wire3_p1',(4.0,3.0,0.0))")
w3_v0 = f._emit_raw(f"VERTEX_POINT('wire3_v0',#{w3_p0.eid})")
w3_v1 = f._emit_raw(f"VERTEX_POINT('wire3_v1',#{w3_p1.eid})")
import math as _math
diag_len = _math.sqrt(9.0 + 9.0)
w3_dir = f._emit_raw(
    f"DIRECTION('wire3_dir',({3.0/diag_len:.6f},{3.0/diag_len:.6f},0.0))"
)
w3_vec = f._emit_raw(f"VECTOR('',#{w3_dir.eid},{diag_len:.6f})")
w3_line = f._emit_raw(f"LINE('wire3_line',#{w3_p0.eid},#{w3_vec.eid})")
w3_edge = f._emit_raw(
    f"EDGE_CURVE('wire3_edge',#{w3_v0.eid},#{w3_v1.eid},#{w3_line.eid},.T.)"
)

# GEOMETRIC_CURVE_SET grouping the free wire edges — simulates free wires
# at top-level COMPOUND alongside the model body.
wire_gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('free_wires',"
    f"(#{w1_edge.eid},#{w2_edge.eid},#{w3_edge.eid}))"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ─────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('FreeWireComp','FreeWireComp','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','free_wire_instance','',#9004,#{sub_pdef.eid},$)"
)
