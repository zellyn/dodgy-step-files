"""Ad101 — Wire edge-curve healing reads past end of edge list after edge removal (open EDGE_LOOP / non-closed 3-edge wire).

Catalog claim: a wire's edge-curves-fix pass iterates edges and reads
the next edge's first parameter. On an open wire (EDGE_LOOP whose
ORIENTED_EDGEs do not connect end-to-start, i.e. a non-closed wire)
whose last edge has been removed during the fix, the iterator continues
past end-of-vector and throws an out-of-range error. Fixture pattern:
EDGE_LOOP containing three ORIENTED_EDGEs forming a non-closed
v0->v1->v2->v3 chain.

Reproducer recipe: Open wire of three edges (EDGE_LOOP not closed);
first fix removes the last edge; subsequent step accesses edges[3].

Byte assertions:
  count_entity_def(b'ORIENTED_EDGE') >= 3
  contains(b'EDGE_LOOP')
  contains(b'EDGE_LOOP') and count_entity_def(b'ORIENTED_EDGE') >= 3

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad101",
    defect=(
        "open wire (non-closed EDGE_LOOP) with 3 ORIENTED_EDGEs forming "
        "v0->v1->v2->v3 chain; edge-curves-fix reads past end of edge "
        "vector after last edge removal; out-of-range OOB access; "
        "fix iteration must bounds-check after each edge modification; "
        "OCCT MANTIS#0030348, #0029780; See also Twi051, Twi064; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: non-closed open wire of 3 edges v0->v1->v2->v3.
# The chain does NOT connect v3 back to v0, so EDGE_LOOP is open.
# When the edge-curves-fix removes the last edge (index 2), subsequent
# access to edges[3] is out-of-range.
#
# Satisfies:
#   count_entity_def(b'ORIENTED_EDGE') >= 3
#   contains(b'EDGE_LOOP')

# Four vertices along the X-axis: v0=(0,0,0) v1=(1,0,0) v2=(2,0,0) v3=(3,0,0)
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="open_wire_v0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="open_wire_v1")
p2 = f.cartesian_point((2.0, 0.0, 0.0), name="open_wire_v2")
p3 = f.cartesian_point((3.0, 0.0, 0.0), name="open_wire_v3")

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Three straight edges along X: e01, e12, e23.
def _line_edge(pa, va, pb, vb):
    d = f.direction((1.0, 0.0, 0.0))
    mag = pb.args[1][0] - pa.args[1][0]
    vec = f.vector(d, mag)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln, same_sense=True)

e01 = _line_edge(p0, v0, p1, v1)
e12 = _line_edge(p1, v1, p2, v2)
e23 = _line_edge(p2, v2, p3, v3)

oe0 = f.oriented_edge(e01, True)
oe1 = f.oriented_edge(e12, True)
oe2 = f.oriented_edge(e23, True)

# EDGE_LOOP with open (non-closed) chain: v0->v1->v2->v3 (v3 != v0).
# This is the open-wire precondition that triggers the OOB access.
f.edge_loop([oe0, oe1, oe2], name="open_wire_loop")
