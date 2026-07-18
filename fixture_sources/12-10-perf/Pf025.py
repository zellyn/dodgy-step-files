"""Pf025 — ADVANCED_FACE with internal-vertex VERTEX_LOOP FACE_BOUND (.U.) causes outer-wire-detection infinite loop (IFC-derived).

Catalog claim: an ADVANCED_FACE carrying two FACE_BOUND entries — a normal
outer rectangular bound plus a VERTEX_LOOP-based internal-vertex FACE_BOUND
(often with orientation .U.) wrapping a single VERTEX_POINT inside the outer
wire — caused outer-wire-detection (ShapeAnalysis::OuterWire()) to spin
indefinitely.

The fixture encodes exactly that pattern: one ADVANCED_FACE with a normal
outer rectangular FACE_OUTER_BOUND (four edges, four corner points) plus an
additional FACE_BOUND wrapping a VERTEX_LOOP around a single interior
VERTEX_POINT at the centre of the rectangle.  The interior VERTEX_LOOP
FACE_BOUND is the structural element that defeats outer-wire detection.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 5
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf025",
    defect=(
        "ADVANCED_FACE with outer rectangular FACE_OUTER_BOUND + internal "
        "VERTEX_LOOP FACE_BOUND (.U.) at centre: ShapeAnalysis::OuterWire() "
        "spins indefinitely iterating over sub-shapes including the vertex bound; "
        "the defect entity is emitted but sits unreachable from the shape-rep root (product chain roots a GEOMETRIC_CURVE_SET stub), so OCC loads only a 1-vertex stub (shape(1)); byte-present but oracle-invisible to the load-time shape-count oracles"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Outer rectangle: four corners at (0,0), (4,0), (4,3), (0,3).
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((4.0, 0.0, 0.0))
p2 = f.cartesian_point((4.0, 3.0, 0.0))
p3 = f.cartesian_point((0.0, 3.0, 0.0))
# Interior vertex at centre (2, 1.5).
p_int = f.cartesian_point((2.0, 1.5, 0.0))

v0    = f.vertex_point(p0)
v1    = f.vertex_point(p1)
v2    = f.vertex_point(p2)
v3    = f.vertex_point(p3)
v_int = f.vertex_point(p_int)

def line_edge(p_start, d_tuple, length, va, vb):
    d   = f.direction(d_tuple)
    vec = f.vector(d, length)
    ln  = f.line(p_start, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0,  0.0, 0.0), 4.0, v0, v1)
e1 = line_edge(p1, (0.0,  1.0, 0.0), 3.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 4.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 3.0, v3, v0)

outer_loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
outer_bound = f.face_outer_bound(outer_loop)

# Internal VERTEX_LOOP wrapping v_int — the IFC-derived defect entity.
vertex_loop = f._emit_raw(f"VERTEX_LOOP('',#{v_int.eid})")
# FACE_BOUND with orientation .U. (unknown/unset) — as seen in IFC→STEP output.
inner_bound = f._emit_raw(f"FACE_BOUND(#{vertex_loop.eid},.U.)")

# Plane (XY).
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ADVANCED_FACE with BOTH bounds: outer rect + interior VERTEX_LOOP FACE_BOUND.
face = f._emit_raw(
    f"ADVANCED_FACE('',(#{outer_bound.eid},#{inner_bound.eid}),#{plane.eid},.T.)"
)

shell = f.open_shell([], name="vertex_loop_shell")
# Rebuild the open shell with our raw face.
shell = f._emit_raw(f"OPEN_SHELL('vertex_loop_shell',(#{face.eid}))")
f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('vertex_loop_sbsm',(#{shell.eid}))")
