"""Pf006 — Quadratic self-intersection check dominates STEP read on
perforated sheets.

Catalog claim: ~90% of STEP read time on sheet-metal parts with thousands
of holes is spent inside shape-healing's wire self-intersection check,
which almost never finds real defects but is paid per wire per face.
Common shape: flat sheet with > 1000 small circular holes, each a
closed circular FACE_BOUND on a single PLANE.

The fixture builds a scaled-down version: 12 circular-hole FACE_BOUNDs
on one ADVANCED_FACE (one outer rectangular bound + 12 inner circular
bounds).  Each inner bound is a closed EDGE_LOOP with one EDGE_CURVE
whose curve is a CIRCLE — the analytic-curve wire pattern that the
self-intersection checker is paid per wire per face.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 10
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf006",
    defect=(
        "perforated sheet: one ADVANCED_FACE with outer rect bound + "
        "12 circular FACE_BOUND holes; wire self-intersection checker "
        "paid O(N²) per face; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Shared plane for the sheet.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ---- Outer rectangular bound ----
p0 = f.cartesian_point((0.0,  0.0,  0.0))
p1 = f.cartesian_point((10.0, 0.0,  0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0,  10.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(p, dt, length, va, vb):
    d = f.direction(dt); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0,  0.0, 0.0), 10.0, v0, v1)
e1 = line_edge(p1, (0.0,  1.0, 0.0), 10.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 10.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 10.0, v3, v0)
outer_loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
outer_bound = f.face_outer_bound(outer_loop)

# ---- Inner circular FACE_BOUNDs (holes) ----
N_HOLES = 12
HOLE_R  = 0.3
bounds  = [outer_bound]

for k in range(N_HOLES):
    # Grid: 3 cols × 4 rows, spacing 2.5 mm.
    col = k % 3
    row = k // 3
    cx = 1.5 + col * 2.5
    cy = 1.5 + row * 2.5
    # Circle placement: centre at (cx, cy, 0), normal +Z.
    hole_orig  = f.cartesian_point((cx, cy, 0.0))
    hole_zdir  = f.direction((0.0, 0.0, 1.0))
    hole_xdir  = f.direction((1.0, 0.0, 0.0))
    hole_plc   = f.axis2_placement_3d(hole_orig, hole_zdir, hole_xdir)
    circle     = f._emit_raw(f"CIRCLE('hole_{k}',#{hole_plc.eid},{HOLE_R})")
    # Closed EDGE_LOOP with one degenerate-endpoint EDGE_CURVE (v→v).
    hole_vp    = f.cartesian_point((cx + HOLE_R, cy, 0.0))
    hole_v     = f.vertex_point(hole_vp)
    hole_ec    = f.edge_curve(hole_v, hole_v, circle)
    hole_loop  = f.edge_loop([f.oriented_edge(hole_ec, True)])
    bounds.append(f.face_bound(hole_loop))

face = f.advanced_face(bounds, plane)

# The face stands alone in an OPEN_SHELL.
shell = f._emit_raw(f"OPEN_SHELL('perforated_sheet',(#{face.eid}))")
sbsm  = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('perf_sbsm',(#{shell.eid}))")
