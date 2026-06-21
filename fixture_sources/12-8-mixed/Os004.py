"""Os004 — Offset request fails: source OPEN_SHELL contains spatially disconnected
ADVANCED_FACEs (no shared edge between groups).

Catalog claim: The shell submitted for offsetting consists of two or more
disconnected face groups; the offset algorithm cannot construct a connected
offset shell.

Mechanism: Two separate planar ADVANCED_FACEs (a small square each) that share
no edge/vertex, wrapped in a single OPEN_SHELL.  OCC loads as shape(1) because
it heals; conservative kernels should reject.

Tier-3 assertions:
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os004",
    defect=(
        "OPEN_SHELL cfs_faces lists two spatially-disconnected ADVANCED_FACEs "
        "(square A at origin, square B at x+20); no shared edge between groups; "
        "offset algorithm cannot construct connected offset shell — "
        "BRepOffset_MakeOffset NotConnectedShell; OCC heals/loads; "
        "conservative kernels must reject"
    ),
)

# ── helper: build one square ADVANCED_FACE on Z-plane ─────────────────────────
def _square_face(ox, oy, side):
    """Return an ADVANCED_FACE for a square in the XY plane at (ox,oy,0)."""
    pts = [
        f.cartesian_point((ox,         oy,         0.0)),
        f.cartesian_point((ox + side,  oy,         0.0)),
        f.cartesian_point((ox + side,  oy + side,  0.0)),
        f.cartesian_point((ox,         oy + side,  0.0)),
    ]
    vs = [f.vertex_point(p) for p in pts]

    def edge(ia, ib, dx, dy):
        length = side
        d = f.direction((dx, dy, 0.0))
        v = f.vector(d, length)
        return f.edge_curve(vs[ia], vs[ib], f.line(pts[ia], v))

    e0 = edge(0, 1,  1.0,  0.0)
    e1 = edge(1, 2,  0.0,  1.0)
    e2 = edge(2, 3, -1.0,  0.0)
    e3 = edge(3, 0,  0.0, -1.0)

    loop = f.edge_loop([
        f.oriented_edge(e0, True),
        f.oriented_edge(e1, True),
        f.oriented_edge(e2, True),
        f.oriented_edge(e3, True),
    ])
    fob = f.face_outer_bound(loop)

    plc  = f.axis2_placement_3d(
        f.cartesian_point((ox, oy, 0.0)),
        f.direction((0.0, 0.0, 1.0)),
        f.direction((1.0, 0.0, 0.0)),
    )
    plane = f.plane(plc)
    return f.advanced_face([fob], plane)

# ── Two disconnected faces — no shared edge ───────────────────────────────────
face_a = _square_face(0.0,  0.0, 5.0)   # square at origin
face_b = _square_face(20.0, 0.0, 5.0)   # square far away — disconnected

# Single OPEN_SHELL wrapping both disconnected faces — IS the defect
shell = f._emit_raw(
    f"OPEN_SHELL('os004_disconnected',(#{face_a.eid},#{face_b.eid}))"
)
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('os004_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os004.stp")
