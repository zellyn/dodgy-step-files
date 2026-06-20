"""Twi120 — ShapeAnalysis_Wire.CheckShapeConnect 4-way orientation encoding.

Catalog claim: Wire boundary where edges should be merged at hub vertex;
CheckShapeConnect's DONE2/3/4 status codes encode 4 specific orientation merge
templates. Radial edges meeting at center with mixed pattern (--,++,-+) hits no
branch condition, silent merge-decision miss. Status propagation undefined.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with four radial
edges meeting at a center hub vertex at (0,0,0). Mixed orientation pattern
(--,++,-+) creates a situation where none of DONE2/DONE3/DONE4 branch conditions
match, causing a silent merge-decision miss:
  - e1: hub→tip1 (0,0,0)→(5,0,0), oriented FORWARD  (+)
  - e2: hub→tip2 (0,0,0)→(0,5,0), oriented FORWARD  (+)  [reversed in loop]
  - e3: tip3→hub (5,5,0)→(0,0,0), oriented FORWARD  (+)
  - e4: tip4→hub (-5,0,0)→(0,0,0), oriented REVERSED (-)  [loop uses reversed sense]
The mixed --,++,-+ orientation pattern at the hub hits no DONE2/3/4 branch.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi120",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 radial edges "
        "meeting at hub vertex (0,0,0); "
        "mixed orientation pattern (--,++,-+) at hub IS defect; "
        "e1: FORWARD (0,0,0)→(5,0,0) tip1; "
        "e2: FORWARD (0,0,0)→(0,5,0) tip2 (reversed in loop); "
        "e3: FORWARD (5,5,0)→(0,0,0) — convergent; "
        "e4: FORWARD (-5,0,0)→(0,0,0) reversed-sense in loop — divergent; "
        "CheckShapeConnect DONE2/3/4 status templates miss mixed orientation; "
        "silent merge-decision miss — status propagation undefined; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Hub vertex at center ──────────────────────────────────────────────────────
HUB = (0.0,  0.0, 0.0)
TIP1 = (5.0,  0.0, 0.0)   # e1 far end
TIP2 = (0.0,  5.0, 0.0)   # e2 far end
TIP3 = (5.0,  5.0, 0.0)   # e3 start (convergent to hub)
TIP4 = (-5.0, 0.0, 0.0)   # e4 start (reversed-sense in loop)

v_hub  = f.vertex_point(f.cartesian_point(HUB))
v_tip1 = f.vertex_point(f.cartesian_point(TIP1))
v_tip2 = f.vertex_point(f.cartesian_point(TIP2))
v_tip3 = f.vertex_point(f.cartesian_point(TIP3))
v_tip4 = f.vertex_point(f.cartesian_point(TIP4))


def _line(src, dst):
    dx, dy, dz = dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )


# e1: hub → tip1, oriented FORWARD in loop (+)
e1  = f.edge_curve(v_hub,  v_tip1, _line(HUB,  TIP1))
oe1 = f.oriented_edge(e1, True)   # FORWARD

# e2: hub → tip2, stored as hub→tip2 but used REVERSED in loop (-)
e2  = f.edge_curve(v_hub,  v_tip2, _line(HUB,  TIP2))
oe2 = f.oriented_edge(e2, False)  # REVERSED — tip2→hub in loop

# e3: tip3 → hub, oriented FORWARD in loop (+) — convergent
e3  = f.edge_curve(v_tip3, v_hub,  _line(TIP3, HUB))
oe3 = f.oriented_edge(e3, True)   # FORWARD

# e4: tip4 → hub, used REVERSED in loop (-) — mixed pattern at hub
e4  = f.edge_curve(v_tip4, v_hub,  _line(TIP4, HUB))
oe4 = f.oriented_edge(e4, False)  # REVERSED — hub→tip4 in loop

# ── EDGE_LOOP: mixed orientation pattern at hub ───────────────────────────────
loop = f.edge_loop([oe1, oe2, oe3, oe4])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi120.stp")
