"""Twi096 — Wire with internal cross-loop translates incorrectly.

Catalog claim: A STEP wire encodes a self-crossing path: edges visit a shared
vertex twice, forming a figure-eight or a small detour loop. The reader builds
a wire object that conflates the two visits, dropping the second occurrence;
geometry is lost.

Reproducer recipe: Seven-edge wire whose vertex sequence is
A → B → C → D → B → E → F → A. Vertex B appears twice (figure-eight cross).
Reader collapses to a six-edge wire A → B → C → D → E → F → A.
The edge from D to B is named 'D_to_B_again'. The edge from B to E is named
'B_to_E'. The first edge A→B is named 'A_to_B'.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'D_to_B_again')
  - contains(b'B_to_E')
  - contains(b'A_to_B')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi096",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 7 LINE edges; "
        "vertex sequence A→B→C→D→B→E→F→A (figure-eight: vertex B visited twice); "
        "edges: 'A_to_B'(A→B), B→C, C→D, 'D_to_B_again'(D→B), 'B_to_E'(B→E), E→F, F→A; "
        "wire reader collapses the second visit to B, dropping D→B or B→E segment; "
        "cross-loop in wire causes geometry loss — figure-eight topology not preserved; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Coordinates for figure-eight vertices ────────────────────────────────────
# A=(0,0,0), B=(2,1,0) [cross-point], C=(4,2,0), D=(3,3,0)
# E=(1,3,0), F=(-1,2,0), back to A=(0,0,0)
coords = {
    "A": (0.0,  0.0, 0.0),
    "B": (2.0,  1.0, 0.0),  # visited twice — figure-eight cross
    "C": (4.0,  2.0, 0.0),
    "D": (3.0,  3.0, 0.0),
    "E": (1.0,  3.0, 0.0),
    "F": (-1.0, 2.0, 0.0),
}

vA = f.vertex_point(f.cartesian_point(coords["A"]))
vB = f.vertex_point(f.cartesian_point(coords["B"]))
vC = f.vertex_point(f.cartesian_point(coords["C"]))
vD = f.vertex_point(f.cartesian_point(coords["D"]))
vE = f.vertex_point(f.cartesian_point(coords["E"]))
vF = f.vertex_point(f.cartesian_point(coords["F"]))


def make_oe(va_entity, vb_entity, va_coords, vb_coords, label=""):
    """Build an ORIENTED_EDGE for a line segment from va to vb."""
    ax, ay, az = va_coords
    bx, by, bz = vb_coords
    dx, dy, dz = bx - ax, by - ay, bz - az
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ec = f.edge_curve(
        va_entity, vb_entity,
        f.line(f.cartesian_point((ax, ay, az)),
               f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag)),
        name=label,
    )
    return f.oriented_edge(ec, True)


# ── Seven edges: A→B→C→D→B→E→F→A ────────────────────────────────────────────
oe_AB = make_oe(vA, vB, coords["A"], coords["B"], label="A_to_B")    # byte assertion
oe_BC = make_oe(vB, vC, coords["B"], coords["C"])
oe_CD = make_oe(vC, vD, coords["C"], coords["D"])
oe_DB = make_oe(vD, vB, coords["D"], coords["B"], label="D_to_B_again")  # byte assertion
oe_BE = make_oe(vB, vE, coords["B"], coords["E"], label="B_to_E")    # byte assertion
oe_EF = make_oe(vE, vF, coords["E"], coords["F"])
oe_FA = make_oe(vF, vA, coords["F"], coords["A"])

# ── EDGE_LOOP: B appears at positions 2 and 5 — figure-eight topology ────────
loop = f._emit_raw(
    f"EDGE_LOOP('',"
    f"(#{oe_AB.eid},#{oe_BC.eid},#{oe_CD.eid},#{oe_DB.eid},"
    f"#{oe_BE.eid},#{oe_EF.eid},#{oe_FA.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi096.stp")
