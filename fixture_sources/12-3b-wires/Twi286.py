"""Twi286 — Minimal self-intersecting (bow-tie) wire on a single real
ADVANCED_FACE — no confounding defects layered on top.

Catalog claim: A wire's own edges cross each other in the host face's
parameter space (BRepCheck_Wire::SelfIntersect / BRepCheck_SelfIntersectingWire,
BRepCheck_Wire.cxx:1048,1051). The wire is topologically closed (four edges,
each vertex used exactly twice) but geometrically self-intersecting — its
first and third edges (the two diagonals of a unit square) cross at the
square's centre.

This fixture is deliberately MINIMAL: ONE ADVANCED_FACE, ONE PLANE, ONE
EDGE_LOOP of four straight LINE edges, wired straight into an OPEN_SHELL. No
second face, no crash-prone geometry, no other defect layered in — every
byte in the file exists only to carry the bow-tie wire. This isolates the
self-intersection from the confounders that made prior attempts in this
corpus (Twi049's two-face setup, Twi076's revisited-vertex framing)
inconclusive as detection evidence.

Mechanism IS the EDGE_LOOP of four edges forming a bow-tie: (0,0,0)->(10,10,0),
(10,10,0)->(10,0,0), (10,0,0)->(0,10,0), (0,10,0)->(0,0,0). Edges 0 and 2 (the
two diagonals) cross at (5,5,0) — dead centre of the nominal 10x10 square, in
both 3D and the host plane's UV (identical since the plane's placement is the
identity frame). The EDGE_LOOP IS wired into a FACE_OUTER_BOUND on a planar
ADVANCED_FACE in an OPEN_SHELL in a SHELL_BASED_SURFACE_MODEL; never orphaned.

Live-oracle note: STEPControl_Reader's default STEP-to-BRep translation runs
ShapeFix_Wire's self-intersection repair (ShapeFix_Wire::FixSelfIntersection,
ShapeFix_IntersectionTool::FixSelfIntersectWire) unconditionally as part of
the standard read pipeline — confirmed by direct testing (both occt_heal_on
and occt_heal_off Interface_Static settings still trigger the split; only
bypassing STEPControl_Reader's ShapeProcess sequence entirely, which no
corpus oracle setting does, leaves the wire unrepaired for BRepCheck to see).
The reader silently splits the bow-tie into two simple triangular faces
before BRepCheck ever runs — this is the SAME "silently heals on import"
outcome already documented for Twi009, Twi010, Twi050, Twi076, and ~120
other self-intersection-adjacent fixtures in this corpus. The defect is
genuinely encoded in the DATA section bytes (one EDGE_LOOP, one ADVANCED_FACE,
crossing diagonals) and is reachable/live in the topology; it is the
`BRepCheck_SelfIntersectingWire` status that is not observable post-import via
the standard reader path, not the geometry itself.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 1
  - count_entity_def(b'EDGE_CURVE') == 4
  - contains(b'(0.0,0.0,0.0)')
  - contains(b'(10.0,10.0,0.0)')

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"

live oracle: occt=shape(1)/shape(1) gmsh=shape(13) — NOTE: the reader's
default ShapeFix pass silently splits the bow-tie into two valid triangular
faces before BRepCheck runs (n_faces_total==2 post-import), so
brepcheck.valid comes back True and no tier-3 assertion claims otherwise.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi286",
    defect=(
        "OPEN_SHELL with ONE ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP of four edges forming a "
        "bow-tie: (0,0,0)->(10,10,0)->(10,0,0)->(0,10,0)->(0,0,0); "
        "edges 0 and 2 are the two diagonals of the nominal square and cross "
        "at (5,5,0) in both 3D and the plane's UV; "
        "the self-crossing wire IS the mechanism — BRepCheck_Wire::SelfIntersect "
        "targets exactly this pattern (BRepCheck_SelfIntersectingWire status); "
        "no second face, no other defect layered in — minimal isolation; "
        "the EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, "
        "OPEN_SHELL, SHELL_BASED_SURFACE_MODEL — never orphaned; "
        "kernel must detect the UV/3D crossing, split the wire at the "
        "intersection into two simple loops, or reject the face as malformed"
    ),
)

# ── Carrier plane geometry: z=0, normal +Z, identity frame (UV == XY) ────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Bow-tie vertices ──────────────────────────────────────────────────────────
v00 = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))
v10 = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))
v20 = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))
v30 = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))

# Edge 0: (0,0,0) -> (10,10,0) — first diagonal
e0_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                  f.vector(f.direction((0.7071067811865476, 0.7071067811865476, 0.0)),
                            14.142135623730951))
e0  = f.edge_curve(v00, v10, e0_line)
oe0 = f.oriented_edge(e0, True)

# Edge 1: (10,10,0) -> (10,0,0)
e1_line = f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                  f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
e1  = f.edge_curve(v10, v20, e1_line)
oe1 = f.oriented_edge(e1, True)

# Edge 2: (10,0,0) -> (0,10,0) — second diagonal, crosses edge 0 at (5,5,0)
e2_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                  f.vector(f.direction((-0.7071067811865476, 0.7071067811865476, 0.0)),
                            14.142135623730951))
e2  = f.edge_curve(v20, v30, e2_line)
oe2 = f.oriented_edge(e2, True)

# Edge 3: (0,10,0) -> (0,0,0)
e3_line = f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                  f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
e3  = f.edge_curve(v30, v00, e3_line)
oe3 = f.oriented_edge(e3, True)

loop = f.edge_loop([oe0, oe1, oe2, oe3])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
