"""Twi122 — ShapeFix_Wire.FixTails wire-tail asymmetry.

Catalog claim: Wire with first edge 0.0001mm (very short) and final edge
normal-length (1.0mm). FixTails detects short trailing edges and removes them,
but fails to symmetrically validate leading edges. Repair chain should either
detect both or apply consistent threshold logic.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with three edges:
  - e1 (tail): very short LINE, 0.0001mm, from (0,0,0) to (0.0001,0,0)
  - e2: normal LINE, 1.0mm, from (0.0001,0,0) to (1.0001,0,0)
  - e3: return LINE, closing the wire, from (1.0001,0,0) to (0,0,0)
The short leading edge (e1) IS the tail defect. FixTails only detects trailing
short edges, not leading ones — asymmetric threshold logic IS the defect.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi122",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges; "
        "e1: very short LINE (0,0,0)→(0.0001,0,0) length=0.0001mm IS leading tail; "
        "e2: normal LINE (0.0001,0,0)→(1.0001,0,0) length=1.0mm; "
        "e3: closing LINE (1.0001,0,0)→(0,0,0) length≈1.0001mm; "
        "FixTails detects trailing short edges but not leading edges IS defect; "
        "asymmetric threshold logic — leading tail e1 IS undetected; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Wire vertex positions ─────────────────────────────────────────────────────
P0 = (0.0,    0.0, 0.0)   # loop start / tail end
P1 = (0.0001, 0.0, 0.0)   # after very short leading tail
P2 = (1.0001, 0.0, 0.0)   # end of normal-length edge

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))


def _line(src, dst):
    dx, dy, dz = dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )


# e1: very short leading tail — length 0.0001mm
e1  = f.edge_curve(v0, v1, _line(P0, P1))
oe1 = f.oriented_edge(e1, True)

# e2: normal length edge — 1.0mm
e2  = f.edge_curve(v1, v2, _line(P1, P2))
oe2 = f.oriented_edge(e2, True)

# e3: closing edge back to start
e3  = f.edge_curve(v2, v0, _line(P2, P0))
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP: short leading tail + normal + closing ──────────────────────────
loop = f.edge_loop([oe1, oe2, oe3])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi122.stp")
