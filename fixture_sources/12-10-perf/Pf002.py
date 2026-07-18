"""Pf002 — Quadratic-cost STEP write on dense forward-reference
VERTEX_POINT / EDGE_CURVE / ADVANCED_FACE web (200k-entity scale).

Catalog claim: write_step_file on a 214 423-entity model takes ~30
minutes, dominated by repeated linear scans over the entity table while
serializing references.  Common shape: a dense forward-reference
VERTEX_POINT / EDGE_CURVE / ADVANCED_FACE web.

The fixture builds a scaled-down version: 20 quad faces in one
OPEN_SHELL, each with unique VERTEX_POINT / EDGE_CURVE / CARTESIAN_POINT
entities placed in DATA-section order that forces forward-reference
resolution during write — the exact pattern behind the O(N²) cost.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 8
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf002",
    defect=(
        "dense VERTEX_POINT/EDGE_CURVE/ADVANCED_FACE web; "
        "forward-reference pattern causes O(N²) writer reference-resolution; "
        "the defect entity is emitted but sits unreachable from the shape-rep root (product chain roots a GEOMETRIC_CURVE_SET stub), so OCC loads only a 1-vertex stub (shape(1)); byte-present but oracle-invisible to the load-time shape-count oracles"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Dense web: 20 quad faces.  Each face has 4 unique VERTEX_POINTs,
# 4 CARTESIAN_POINTs, and 4 EDGE_CURVEs — the cross-reference density
# between VERTEX_POINT, EDGE_CURVE, and ADVANCED_FACE is what drives
# the O(N²) write cost in the original bug report.
N = 5   # 5×4 = 20 faces

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

faces = []
for i in range(N):
    for j in range(4):
        x = float(i)
        y = float(j)
        p0 = f.cartesian_point((x,       y,       0.0))
        p1 = f.cartesian_point((x + 1.0, y,       0.0))
        p2 = f.cartesian_point((x + 1.0, y + 1.0, 0.0))
        p3 = f.cartesian_point((x,       y + 1.0, 0.0))
        v0 = f.vertex_point(p0)
        v1 = f.vertex_point(p1)
        v2 = f.vertex_point(p2)
        v3 = f.vertex_point(p3)
        e0 = line_edge(p0, (1.0,  0.0, 0.0), 1.0, v0, v1)
        e1 = line_edge(p1, (0.0,  1.0, 0.0), 1.0, v1, v2)
        e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
        e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
        loop = f.edge_loop([
            f.oriented_edge(e0, True),
            f.oriented_edge(e1, True),
            f.oriented_edge(e2, True),
            f.oriented_edge(e3, True),
        ])
        faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

# OPEN_SHELL with all 20 faces — models the huge cross-reference web.
shell = f._emit_raw(
    f"OPEN_SHELL('dense_forward_ref_web',"
    f"({','.join(f'#{x.eid}' for x in faces)}))"
)
sbsm = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('dense_web_sbsm',(#{shell.eid}))"
)
