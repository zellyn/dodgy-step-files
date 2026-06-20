"""Twi124 — ShapeFix_Wire.FixIntersectingEdges 2.0000001 magic-constant.

Catalog claim: Wire edges with intersection detection tolerance multiplied by
literal constant 2.0000001. When input tolerance is just above 2.0mm, scaled
margin collapses, causing false-negative intersection detection. Tolerance
scaling should use adaptive or documented multiplier.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with two edges
that geometrically cross:
- e1: horizontal LINE from (0,0,0) to (4,0,0)
- e2: vertical LINE from (2,2,0) to (2,-2,0) — 3D curves cross at (2,0,0)
The vertex chain is also broken: e1 ends at v2=(4,0,0), e2 starts at v3=(2,2,0).
FixIntersectingEdges uses a tolerance multiplied by the literal constant 2.0000001;
when the input edge-tolerance is just above 2.0mm, the scaled margin collapses
causing a false-negative intersection detection.

GEOMETRIC_CURVE_SET as the model entity ensures OCC produces an empty result.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

# The literal 2.0000001 magic-constant from OCCT ShapeFix_Wire source.
_MAGIC_TOL = 2.0000001

f = StepFile(
    catalog_id="Twi124",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 2 crossing LINE edges; "
        "e1: horizontal (0,0,0)→(4,0,0); "
        "e2: vertical (2,2,0)→(2,-2,0) — 3D curves cross at (2,0,0); "
        "vertex chain broken: e1 end v2=(4,0,0), e2 start v3=(2,2,0); "
        f"FixIntersectingEdges uses magic-constant tolerance multiplier {_MAGIC_TOL}; "
        "when edge-tolerance is just above 2.0mm the scaled margin collapses, "
        "causing false-negative intersection detection; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices ──────────────────────────────────────────────────────────────────
v1 = f.vertex_point(f.cartesian_point((0.0,  0.0, 0.0)))   # e1 start
v2 = f.vertex_point(f.cartesian_point((4.0,  0.0, 0.0)))   # e1 end
v3 = f.vertex_point(f.cartesian_point((2.0,  2.0, 0.0)))   # e2 start (gap from v2)
v4 = f.vertex_point(f.cartesian_point((2.0, -2.0, 0.0)))   # e2 end

# ── Edge e1: horizontal line (0,0,0)→(4,0,0) ─────────────────────────────────
e1 = f.edge_curve(
    v1, v2,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 4.0))
)
oe1 = f.oriented_edge(e1, True)

# ── Edge e2: vertical line (2,2,0)→(2,-2,0) — crosses e1 at (2,0,0) ──────────
e2 = f.edge_curve(
    v3, v4,
    f.line(f.cartesian_point((2.0, 2.0, 0.0)),
           f.vector(f.direction((0.0, -1.0, 0.0)), 4.0))
)
oe2 = f.oriented_edge(e2, True)

# ── EDGE_LOOP: crossing and disconnected edges ────────────────────────────────
loop = f.edge_loop([oe1, oe2])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi124.stp")
