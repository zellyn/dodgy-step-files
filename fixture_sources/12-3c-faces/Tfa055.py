"""Tfa055 — Two distinct wires of one face cross each other in UV.

Catalog claim: An ADVANCED_FACE on a PLANE has an outer bound (a square) and
an inner bound (a square hole) whose pcurves cross in the surface's UV parameter
space. The "hole" actually pokes through the outer boundary.
Bug-reporter language: "wire intersects another wire", "hole crosses outer
boundary", "inner loop sticks out of face".

Mechanism: OPEN_SHELL with TWO faces:
  face[0] (defective): ADVANCED_FACE on 100×100 PLANE with:
    - FACE_OUTER_BOUND: 100×100 outer square (x=[0,100], y=[0,100])
    - FACE_BOUND: square inner bound that starts inside (x=[60,120], y=[40,80])
      — partially outside the outer square, so boundaries cross at x=100.
  face[1] (reference): valid 100×100 plane at y=200 (area > 9900).

The inner bound's right edge (at x=120) extends beyond the outer bound's right
edge (at x=100), so the two wires cross at x=100.

Tier-3 assertions:
  n_faces_total == 2
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"
  face[0].edge_count >= 4
  face[1].edge_count >= 4
  face[1].area > 9900

Expected: occt=shape(1)/shape(1) gmsh=shape(24) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Tfa055",
    defect=(
        "OPEN_SHELL: face[0] is 100×100 PLANE with FACE_OUTER_BOUND (0-100,0-100) "
        "and FACE_BOUND inner wire (60-120,40-80); inner wire's right edge at x=120 "
        "crosses outer bound's right edge at x=100 — UV intersection; "
        "face[1] is valid 100×100 plane at y=200 (area=10000 > 9900); "
        "BRepCheck_Face::IntersectingWires must detect the crossing; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)


def make_poly_loop(coords_xy, z=0.0):
    """Build an EDGE_LOOP from a list of (x,y) coordinates at given z."""
    n = len(coords_xy)
    cps = [f.cartesian_point((float(x), float(y), z)) for x, y in coords_xy]
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
        ec  = f.edge_curve(vs[i], vs[(i + 1) % n], f.line(cps[i], vec))
        ecs.append(ec)
    return f.edge_loop([f.oriented_edge(ec, True) for ec in ecs])


# ── PLANE at z=0 ──────────────────────────────────────────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
plane0   = f.plane(f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir))

# ── Outer bound: 100×100 square ───────────────────────────────────────────────
outer_loop = make_poly_loop([(0,0), (100,0), (100,100), (0,100)])

# ── Inner bound: square partly outside outer (crossing at x=100) ──────────────
# Inner wire from (60,40) to (120,40) to (120,80) to (60,80) — crosses at x=100
inner_loop = make_poly_loop([(60,40), (120,40), (120,80), (60,80)])

# face[0]: outer + inner (crossing) wires — the defective face
face0 = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(inner_loop, orientation=False),
], plane0)

# ── PLANE at z=0, offset y=200 ────────────────────────────────────────────────
pl1_orig = f.cartesian_point((0.0, 200.0, 0.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
plane1   = f.plane(f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir))

# face[1]: valid 100×100 reference face (area = 10000 > 9900)
ref_loop = make_poly_loop([(0,200), (100,200), (100,300), (0,300)])
face1 = f.advanced_face([f.face_outer_bound(ref_loop)], plane1)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa055.stp")
