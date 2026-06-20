"""Twi258 — self-loop-small-edge

Catalog claim: Self-loop with length 0.05 (below tolerance). CheckSmall must
filter before counting; without filter, spurious loop.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with a self-loop edge
'small_loop_e' whose V1==V2 and whose LINE has magnitude 0.05 (below the
default ShapeAnalysis tolerance of ~0.1). A second normal edge 'normal_e'
connects two distinct vertices. When ShapeAnalysis_Wire::CheckLoop counts
vertex extents, it must invoke CheckSmall on each self-loop edge first; if
CheckSmall is skipped the small self-loop inflates the vertex degree and
triggers a spurious loop detection IS the defect.

Byte assertions:
  - contains(b'small_loop_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi258",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with small self-loop and normal edge; "
        "small_loop_e: EDGE_CURVE V0->V0 (same vertex) LINE magnitude=0.05 below tolerance IS small-loop defect; "
        "normal_e: EDGE_CURVE V0->V1 LINE magnitude=6 IS normal edge; "
        "CheckLoop must call CheckSmall on self-loop before counting vertex extent; "
        "without CheckSmall filter, small self-loop inflates vertex degree IS spurious-loop defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# Vertices
vV0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vV1 = f.vertex_point(f.cartesian_point((6.0, 0.0, 0.0)))

# small_loop_e: self-loop with magnitude 0.05 (below tolerance) IS the defect
sl_dir = f.direction((1.0, 0.0, 0.0))
sl_vec = f.vector(sl_dir, 0.05)
sl_ln  = f.line(f.cartesian_point((0.0, 0.0, 0.0)), sl_vec)
ec_sl  = f._emit_raw(
    f"EDGE_CURVE('small_loop_e',#{vV0.eid},#{vV0.eid},#{sl_ln.eid},.T.)"
)

# normal_e: distinct endpoints, magnitude=6
n_dir = f.direction((1.0, 0.0, 0.0))
n_vec = f.vector(n_dir, 6.0)
n_ln  = f.line(f.cartesian_point((0.0, 0.0, 0.0)), n_vec)
ec_n  = f._emit_raw(
    f"EDGE_CURVE('normal_e',#{vV0.eid},#{vV1.eid},#{n_ln.eid},.T.)"
)

oe_sl = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_sl.eid},.T.)")
oe_n  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_n.eid},.T.)")

loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_sl.eid},#{oe_n.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi258.stp")
