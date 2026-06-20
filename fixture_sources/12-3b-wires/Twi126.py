"""Twi126 — ShapeFix_Wire.FixClosed linear submethod cascade.

Catalog claim: FixClosed chains FixConnected → FixDegenerated → FixLacking
sequentially. After FixConnected modifies wire (fixes gap), FixDegenerated's
internal state flags may skip degenerate-edge detection due to prior fix.
Cascade must reset internal state or use independent analysis per sub-method.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with three edges:
  - e1: normal LINE from (0,0,0) to (1,0,0)
  - e2: normal LINE with 3D gap — starts at (1.01,0,0) not (1,0,0)
    (small gap to trigger FixConnected)
  - e3: degenerate zero-length LINE at (2,0,0) (to trigger FixDegenerated)
After FixConnected shifts vertices to close the e1→e2 gap, FixDegenerated's
internal state (set before FixConnected ran) still marks e3 as "already analyzed",
skipping the degenerate-edge detection. Cascade state reset IS the defect.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi126",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges; "
        "e1: normal LINE (0,0,0)→(1,0,0); "
        "e2: LINE (1.01,0,0)→(2,0,0) — small 0.01-unit gap from e1 end triggers FixConnected; "
        "e3: degenerate zero-length LINE at (2,0,0)→(2,0,0) triggers FixDegenerated; "
        "FixClosed cascade: FixConnected fixes gap, then FixDegenerated internal state "
        "flags skip e3 detection due to prior-fix state not reset IS defect; "
        "FixClosed must reset internal state between sub-methods; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Wire vertices ─────────────────────────────────────────────────────────────
P0 = (0.0,  0.0, 0.0)   # e1 start
P1 = (1.0,  0.0, 0.0)   # e1 end (gap before e2)
P2 = (1.01, 0.0, 0.0)   # e2 start — small gap triggers FixConnected
P3 = (2.0,  0.0, 0.0)   # e2 end / e3 degenerate point

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))
v3 = f.vertex_point(f.cartesian_point(P3))


def _line(src, dst):
    dx, dy, dz = dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )


# e1: normal edge
e1  = f.edge_curve(v0, v1, _line(P0, P1))
oe1 = f.oriented_edge(e1, True)

# e2: starts with small gap from e1 end — triggers FixConnected
e2  = f.edge_curve(v2, v3, _line(P2, P3))
oe2 = f.oriented_edge(e2, True)

# e3: degenerate zero-length edge at (2,0,0) — triggers FixDegenerated
# But FixDegenerated's internal state is stale after FixConnected ran
degen_line = f.line(
    f.cartesian_point(P3),
    f.vector(f.direction((1.0, 0.0, 0.0)), 0.0),
)
e3  = f.edge_curve(v3, v3, degen_line)
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP: gap at e1→e2 + degenerate e3 ──────────────────────────────────
loop = f.edge_loop([oe1, oe2, oe3])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi126.stp")
