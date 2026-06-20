"""Twi100 — COMPOSITE_CURVE_ON_SURFACE LoadONBrep stub (BRL-CAD step-g).

Catalog claim: A topology entity whose underlying basis is a
COMPOSITE_CURVE_ON_SURFACE (a chain of COMPOSITE_CURVE_SEGMENTs, each
carrying a transition_code, all laid out on one host) loses both its 3D
geometry and its endpoint resolution: the LoadONBrep stub in
CompositeCurveOnSurface.cpp returns false, the inherited PointAtStart /
PointAtEnd stubs in CompositeCurve.cpp return null, and the ON_Brep ends up
with a zero-length trim.

Reproducer recipe:
  #80=COMPOSITE_CURVE_ON_SURFACE('chain',(#70,#71),.U.);
referenced from a topology entity; step-g stubs out.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP whose single
EDGE_CURVE uses a COMPOSITE_CURVE_ON_SURFACE as its underlying curve. The
two composite segments each reference a LINE on a PLANE. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'COMPOSITE_CURVE_ON_SURFACE')
  - contains(b'COMPOSITE_CURVE_SEGMENT')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi100",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with one EDGE_CURVE; "
        "underlying curve is COMPOSITE_CURVE_ON_SURFACE('chain') with two "
        "COMPOSITE_CURVE_SEGMENTs; step-g LoadONBrep stub returns false — "
        "segment list not walked, endpoint resolution stubs return null; "
        "ON_Brep ends up with zero-length trim; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Host plane (required by COMPOSITE_CURVE_ON_SURFACE) ───────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Segment 1: LINE from (0,0,0) to (5,0,0) ──────────────────────────────────
s1_orig = f.cartesian_point((0.0, 0.0, 0.0))
s1_dir  = f.direction((1.0, 0.0, 0.0))
s1_vec  = f.vector(s1_dir, 5.0)
seg1_curve = f.line(s1_orig, s1_vec)

# ── Segment 2: LINE from (5,0,0) to (10,0,0) ─────────────────────────────────
s2_orig = f.cartesian_point((5.0, 0.0, 0.0))
s2_dir  = f.direction((1.0, 0.0, 0.0))
s2_vec  = f.vector(s2_dir, 5.0)
seg2_curve = f.line(s2_orig, s2_vec)

# ── COMPOSITE_CURVE_SEGMENT entities ─────────────────────────────────────────
# COMPOSITE_CURVE_SEGMENT(transition_code, same_sense, parent_curve)
# Byte assertion: contains(b'COMPOSITE_CURVE_SEGMENT')
css1 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.DISCONTINUOUS.,#{seg1_curve.eid},.T.)"
)
css2 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.DISCONTINUOUS.,#{seg2_curve.eid},.T.)"
)

# ── COMPOSITE_CURVE_ON_SURFACE ────────────────────────────────────────────────
# COMPOSITE_CURVE_ON_SURFACE(name, segments, self_intersect)
# Byte assertion: contains(b'COMPOSITE_CURVE_ON_SURFACE')
ccos = f._emit_raw(
    f"COMPOSITE_CURVE_ON_SURFACE('chain',(#{css1.eid},#{css2.eid}),.U.)"
)

# ── Vertices at start and end of composite chain ──────────────────────────────
v_start = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_end   = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))

# ── EDGE_CURVE using COMPOSITE_CURVE_ON_SURFACE as underlying curve ───────────
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{ccos.eid},.T.)"
)
oe   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi100.stp")
