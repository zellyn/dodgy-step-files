"""Tfa039 — Face has multiple wires that intersect in UV.

Catalog claim: An ADVANCED_FACE has an outer wire and one or more inner wires
whose 2D pcurves cross each other in the host surface's parameter space. The
wires are not nested; they overlap. The face cannot bound a simple region.

Mechanism: A 10×10 square ADVANCED_FACE on a PLANE at z=0. The face has:
  - face[0] outer bound: 10×10 square border (x=[0,10], y=[0,10])
  - Two "inner" FACE_BOUND wires that are diagonal parallelograms crossing:
      wire_a: (2,2)→(8,4)→(8,8)→(2,6) — slanted NE
      wire_b: (2,8)→(8,6)→(8,2)→(2,4) — slanted SE (crosses wire_a at center)

The two inner wires are not nested (they intersect each other in UV),
which is the defect that FixIntersectingWires must detect and repair.

Additional valid reference face at y=12 to ensure adequate edge/vertex counts.

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  n_vertices_total >= 16

Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Tfa039",
    defect=(
        "OPEN_SHELL: face[0] is 10×10 PLANE with outer FACE_OUTER_BOUND "
        "plus two non-nested inner FACE_BOUND wires that cross each other in UV; "
        "wire_a slanted quad (2,2)→(8,4)→(8,8)→(2,6); "
        "wire_b slanted quad (2,8)→(8,6)→(8,2)→(2,4) — crosses wire_a at center; "
        "FixIntersectingWires / IntersectionTool must detect UV crossing and "
        "split or reject; defect IS on live OPEN_SHELL traversal path"
    ),
)


def mk_poly_loop(coords_xy):
    """Build a closed EDGE_LOOP from a list of (x,y) 2D coordinates at z=0."""
    n = len(coords_xy)
    cps = [f.cartesian_point((float(x), float(y), 0.0)) for x, y in coords_xy]
    vs  = [f.vertex_point(cp) for cp in cps]
    ecs = []
    for i in range(n):
        x0, y0 = coords_xy[i]
        x1, y1 = coords_xy[(i + 1) % n]
        dx = x1 - x0
        dy = y1 - y0
        mag = math.sqrt(dx*dx + dy*dy)
        d   = f.direction((dx/mag, dy/mag, 0.0))
        vec = f.vector(d, mag)
        ec  = f.edge_curve(vs[i], vs[(i+1) % n], f.line(cps[i], vec))
        ecs.append(ec)
    return f.edge_loop([f.oriented_edge(ec, True) for ec in ecs])


# ── PLANE at z=0 ──────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane0  = f.plane(pl_plc)

# ── Outer 10×10 bound ─────────────────────────────────────────────────────────
outer_loop = mk_poly_loop([(0,0), (10,0), (10,10), (0,10)])

# ── Inner wire A: slanted parallelogram (NE direction) ────────────────────────
wire_a_loop = mk_poly_loop([(2,2), (8,4), (8,8), (2,6)])

# ── Inner wire B: slanted parallelogram (SE direction, crosses wire A) ────────
wire_b_loop = mk_poly_loop([(2,8), (8,6), (8,2), (2,4)])

# Both inner bounds have orientation=False (inner boundary convention)
face0 = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(wire_a_loop, orientation=False),
    f.face_bound(wire_b_loop, orientation=False),
], plane0)

# ── Valid reference face (10×10 square at y=12) to meet tier-3 vertex count ──
pl2_orig = f.cartesian_point((0.0, 12.0, 0.0))
pl2_zdir = f.direction((0.0, 0.0, 1.0))
pl2_xdir = f.direction((1.0, 0.0, 0.0))
pl2_plc  = f.axis2_placement_3d(pl2_orig, pl2_zdir, pl2_xdir)
plane1   = f.plane(pl2_plc)
ref_loop = mk_poly_loop([(0,12), (10,12), (10,22), (0,22)])
face1    = f.advanced_face([f.face_outer_bound(ref_loop)], plane1)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa039.stp")
