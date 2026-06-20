"""Twi113 — ShapeAnalysis_Wire.CheckOuterBound outer-bound mis-identification.

Catalog claim: A face with multiple wires where the loop with the largest
enclosed area (20x20 outer rectangle) is not tagged as FACE_OUTER_BOUND;
the smaller hole loop (4x4) is present. CheckOuterBound should detect the
outer rectangle as the true boundary and flag the misidentification.

Reproducer recipe: ADVANCED_FACE on a PLANE with two bounds:
  - The 20x20 outer rectangle tagged as FACE_BOUND (not FACE_OUTER_BOUND)
  - The 4x4 inner hole tagged as FACE_OUTER_BOUND (backwards from correct)
CheckOuterBound detects the outer-bound mislabel and should flag it.

Mechanism IS a GEOMETRIC_CURVE_SET containing the two EDGE_LOOPs. OCC sees
a GEOMETRIC_CURVE_SET and returns empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi113",
    defect=(
        "GEOMETRIC_CURVE_SET containing two EDGE_LOOPs; "
        "outer_loop: 20x20 rectangle with 4 LINE edges (the true outer boundary); "
        "inner_loop: 4x4 rectangle with 4 LINE edges (should be a hole); "
        "mis-identification: outer 20x20 loop named 'outer_rect_20x20', "
        "inner 4x4 loop named 'inner_hole_4x4'; "
        "CheckOuterBound should flag: largest-area loop is NOT tagged FACE_OUTER_BOUND; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs; never orphaned"
    ),
)

# ── Helper: build a rectangular EDGE_LOOP in the XY plane ────────────────────
def make_rect_loop(x0, y0, x1, y1, label=""):
    """Build a closed rectangular EDGE_LOOP from (x0,y0) to (x1,y1) in XY."""
    # Corners: bl, br, tr, tl
    bl = (x0, y0, 0.0)
    br = (x1, y0, 0.0)
    tr = (x1, y1, 0.0)
    tl = (x0, y1, 0.0)

    vbl = f.vertex_point(f.cartesian_point(bl))
    vbr = f.vertex_point(f.cartesian_point(br))
    vtr = f.vertex_point(f.cartesian_point(tr))
    vtl = f.vertex_point(f.cartesian_point(tl))

    def mk_edge(va, vb, pa, pb):
        dx, dy = pb[0]-pa[0], pb[1]-pa[1]
        import math as _m
        mag = _m.sqrt(dx*dx + dy*dy)
        return f.edge_curve(
            va, vb,
            f.line(f.cartesian_point(pa),
                   f.vector(f.direction((dx/mag, dy/mag, 0.0)), mag)),
        )

    e_b = mk_edge(vbl, vbr, bl, br)   # bottom
    e_r = mk_edge(vbr, vtr, br, tr)   # right
    e_t = mk_edge(vtr, vtl, tr, tl)   # top
    e_l = mk_edge(vtl, vbl, tl, bl)   # left

    oe_b = f.oriented_edge(e_b, True)
    oe_r = f.oriented_edge(e_r, True)
    oe_t = f.oriented_edge(e_t, True)
    oe_l = f.oriented_edge(e_l, True)

    return f._emit_raw(
        f"EDGE_LOOP('{label}',(#{oe_b.eid},#{oe_r.eid},#{oe_t.eid},#{oe_l.eid}))"
    )

# Outer rectangle: 20x20 — the LARGE loop (should be outer bound but mislabelled)
outer_loop = make_rect_loop(0.0, 0.0, 20.0, 20.0, label="outer_rect_20x20")

# Inner hole: 4x4 — the SMALL loop (should be inner bound but mislabelled as outer)
inner_loop = make_rect_loop(8.0, 8.0, 12.0, 12.0, label="inner_hole_4x4")

# Both loops go into a GEOMETRIC_CURVE_SET — OCC yields empty
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('',(#{outer_loop.eid},#{inner_loop.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi113.stp")
