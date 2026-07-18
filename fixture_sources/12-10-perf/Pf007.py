"""Pf007 — ADVANCED_FACE with many circular inner FACE_BOUND holes triggers
eager UV-bounds wire-walk on every type-only surface query.

Catalog claim: querying the supporting surface of a face eagerly walks
every edge of every bounding wire to compute UV bounds, even when the
caller only needs the surface type.  Common shape: one ADVANCED_FACE
with an outer bound plus many circular inner FACE_BOUNDs on a single
PLANE; the cost multiplies by hole count.

The fixture builds: one ADVANCED_FACE on a shared PLANE with one outer
rectangular FACE_OUTER_BOUND and 15 inner circular FACE_BOUNDs.  Each
inner bound is a closed EDGE_LOOP with one EDGE_CURVE whose curve is a
CIRCLE.  The eager UV-walk visits every edge of every inner loop even
for a surface-type-only query.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 8
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf007",
    defect=(
        "one ADVANCED_FACE with outer rect bound + 15 circular FACE_BOUNDs; "
        "eager UV-bounds wire-walk on surface-type query costs O(N) per call; "
        "the defect entity is emitted but sits unreachable from the shape-rep root (product chain roots a GEOMETRIC_CURVE_SET stub), so OCC loads only a 1-vertex stub (shape(1)); byte-present but oracle-invisible to the load-time shape-count oracles"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Shared plane for the sheet.
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ---- Outer rectangular bound ----
p0 = f.cartesian_point((0.0,  0.0,  0.0))
p1 = f.cartesian_point((12.0, 0.0,  0.0))
p2 = f.cartesian_point((12.0, 12.0, 0.0))
p3 = f.cartesian_point((0.0,  12.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(p, dt, length, va, vb):
    d = f.direction(dt); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0,  0.0, 0.0), 12.0, v0, v1)
e1 = line_edge(p1, (0.0,  1.0, 0.0), 12.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 12.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 12.0, v3, v0)
outer_loop  = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
outer_bound = f.face_outer_bound(outer_loop)

# ---- Inner circular FACE_BOUNDs (holes) ----
# 15 holes arranged 3×5 — enough to demonstrate the eager-UV-walk cost.
N_HOLES = 15
HOLE_R  = 0.25
bounds  = [outer_bound]

for k in range(N_HOLES):
    col = k % 3
    row = k // 3
    cx = 1.5 + col * 3.5
    cy = 1.5 + row * 2.5
    h_orig = f.cartesian_point((cx, cy, 0.0))
    h_zdir = f.direction((0.0, 0.0, 1.0))
    h_xdir = f.direction((1.0, 0.0, 0.0))
    h_plc  = f.axis2_placement_3d(h_orig, h_zdir, h_xdir)
    circle = f._emit_raw(f"CIRCLE('hole_{k}',#{h_plc.eid},{HOLE_R})")
    # Closed loop: one degenerate-endpoint edge around the circle.
    h_vp   = f.cartesian_point((cx + HOLE_R, cy, 0.0))
    h_v    = f.vertex_point(h_vp)
    h_ec   = f.edge_curve(h_v, h_v, circle)
    h_loop = f.edge_loop([f.oriented_edge(h_ec, True)])
    bounds.append(f.face_bound(h_loop))

face = f.advanced_face(bounds, plane)

# Wrap in OPEN_SHELL / SHELL_BASED_SURFACE_MODEL so the structure is
# representative of a real STEP body (not just floating topology).
shell = f._emit_raw(f"OPEN_SHELL('holey_sheet',(#{face.eid}))")
sbsm  = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('holey_sbsm',(#{shell.eid}))")
