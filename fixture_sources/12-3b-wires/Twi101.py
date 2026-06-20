"""Twi101 — POLYLINE basis curve LoadONBrep stub (BRL-CAD step-g).

Catalog claim: Polyline.cpp has a working Load that fills the in-memory model
with the list of CARTESIAN_POINTs, but no LoadONBrep override exists; the
call falls through to the base stub which prints "not implemented for
Polyline" and returns false. A topology entity using POLYLINE as its
underlying basis loses the geometry: only the start/end vertices remain.
The receiver builds a zero-length topology entity or fails to build the wire.

Reproducer recipe:
  #20=POLYLINE('chamfer_basis',(#10,#11,#12));
referenced from a topology entity via its underlying-curve slot; step-g
loads the polyline points but the LoadONBrep stub drops the basis.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. The single
EDGE_CURVE uses a POLYLINE named 'chamfer_basis' (3 control points forming
a chamfered corner) as its underlying curve. OCC sees a GEOMETRIC_CURVE_SET
and returns empty.

Byte assertions:
  - contains(b'POLYLINE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi101",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with one EDGE_CURVE; "
        "underlying curve is POLYLINE 'chamfer_basis' with 3 CARTESIAN_POINTs "
        "forming a chamfered corner: (0,0,0)->(1,0,0)->(2,1,0); "
        "step-g Polyline.cpp has Load but no LoadONBrep override; "
        "call falls through to base stub 'not implemented for Polyline'; "
        "geometry is lost — only start/end vertices remain; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── POLYLINE control points: chamfered-corner broken-line ────────────────────
# Three points: start of chamfer bevel, corner, end of chamfer bevel
p0 = f.cartesian_point((0.0, 0.0, 0.0))   # start
p1 = f.cartesian_point((1.0, 0.0, 0.0))   # chamfer midpoint
p2 = f.cartesian_point((2.0, 1.0, 0.0))   # end

# ── POLYLINE: 'chamfer_basis' — byte assertion: contains(b'POLYLINE') ────────
polyline = f._emit_raw(
    f"POLYLINE('chamfer_basis',(#{p0.eid},#{p1.eid},#{p2.eid}))"
)

# ── Vertices at start and end of polyline ────────────────────────────────────
v_start = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_end   = f.vertex_point(f.cartesian_point((2.0, 1.0, 0.0)))

# ── EDGE_CURVE using POLYLINE as its underlying curve ────────────────────────
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{polyline.eid},.T.)"
)
oe   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi101.stp")
