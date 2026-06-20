"""Twi098 — FixTails removes wire tail edges incorrectly.

Catalog claim: A wire-cleanup pass intended to remove "tail" edges (short
detours) is applied to a wire whose tails are deliberately significant;
feature edges encoding small chamfers or fillets. The algorithm classifies
them as removable noise and drops them, simplifying geometry beyond intent.

Reproducer recipe: Wire of 6 edges, two of which are short (1 mm each, vs
others at 100 mm). Tails-fix removes both short edges.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP named
'hex_with_two_short_features' with 6 LINE edges. Edges e3 and e6 are each
1 mm long (chamfer/fillet marker) while e1,e2,e4,e5 are 100 mm long.
Edge e3 is named 'e3_short_1mm_chamfer'; e6 is named 'e6_short_1mm_fillet_marker'.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'e3_short_1mm_chamfer')
  - contains(b'e6_short_1mm_fillet_marker')
  - contains(b'hex_with_two_short_features')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi098",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'hex_with_two_short_features'; "
        "6 LINE edges: e1(100mm),e2(100mm),e3='e3_short_1mm_chamfer'(1mm),"
        "e4(100mm),e5(100mm),e6='e6_short_1mm_fillet_marker'(1mm); "
        "FixTails classifies 1mm edges as removable tails despite encoding chamfer/fillet; "
        "correct kernel preserves short feature edges above tolerance threshold; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertex layout: hexagonal-ish wire with two short feature edges ─────────────
# Layout (not a closed loop; open chain to keep geometry simple):
#   v0=(0,0,0) --100mm--> v1=(100,0,0) --100mm--> v2=(200,0,0)
#   --1mm chamfer--> v3=(201,0,0) --100mm--> v4=(301,0,0)
#   --100mm--> v5=(401,0,0) --1mm fillet--> v6=(402,0,0)
# Byte assertions: names on edges

def mk_vertex(pt):
    return f.vertex_point(f.cartesian_point(pt))

def mk_oe(v_a, v_b, pa, pb, label=""):
    dx = pb[0] - pa[0]
    dy = pb[1] - pa[1]
    dz = pb[2] - pa[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ec = f.edge_curve(
        v_a, v_b,
        f.line(f.cartesian_point(pa),
               f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag)),
        name=label,
    )
    return f.oriented_edge(ec, True)

coords = [
    (0.0,   0.0, 0.0),   # v0
    (100.0, 0.0, 0.0),   # v1
    (200.0, 0.0, 0.0),   # v2
    (201.0, 0.0, 0.0),   # v3 — after 1mm chamfer
    (301.0, 0.0, 0.0),   # v4
    (401.0, 0.0, 0.0),   # v5
    (402.0, 0.0, 0.0),   # v6 — after 1mm fillet
]

vs = [mk_vertex(c) for c in coords]

oe1 = mk_oe(vs[0], vs[1], coords[0], coords[1])                          # e1: 100mm
oe2 = mk_oe(vs[1], vs[2], coords[1], coords[2])                          # e2: 100mm
oe3 = mk_oe(vs[2], vs[3], coords[2], coords[3], "e3_short_1mm_chamfer")  # e3: 1mm
oe4 = mk_oe(vs[3], vs[4], coords[3], coords[4])                          # e4: 100mm
oe5 = mk_oe(vs[4], vs[5], coords[4], coords[5])                          # e5: 100mm
oe6 = mk_oe(vs[5], vs[6], coords[5], coords[6], "e6_short_1mm_fillet_marker")  # e6: 1mm

# Byte assertion: contains(b'hex_with_two_short_features')
loop = f._emit_raw(
    f"EDGE_LOOP('hex_with_two_short_features',"
    f"(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid},#{oe5.eid},#{oe6.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi098.stp")
