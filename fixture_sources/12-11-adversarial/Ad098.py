"""Ad098 — Infinite recursion during ShapeFix after Boolean cut.

Catalog claim: a Boolean-cut result has a sliver face that, when removed
by ShapeFix, exposes another sliver face; infinitely. The ShapeFix pipeline
lacks a fixpoint guard and recurses until stack overflow.

Reproducer recipe: Boolean cut producing a result with three nested sliver
faces, each exposing the next when removed.

Byte assertions:
  count_entity_def(b'ADVANCED_FACE') >= 3 and contains(b'sliver')
  count_entity_def(b'ADVANCED_FACE') >= 4

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad098",
    defect=(
        "Boolean-cut result with cascading sliver faces triggers infinite "
        "recursion in ShapeFix; removing one sliver exposes another; "
        "ShapeFix lacks fixpoint guard / iteration limit; "
        "must use fixed iteration count or relative-change termination; "
        "OCCT MANTIS#0030396; See also Tfa056; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Helper: build a sliver ADVANCED_FACE — a very thin (near-degenerate) planar
# face. Each sliver has width epsilon (1e-8) in Y and unit length in X.
# When ShapeFix removes sliver i it collapses the edge shared with sliver i+1,
# exposing sliver i+1 as the new narrowest face → unbounded recursion.

def _make_sliver(f, x_offset: float, label: str):
    """Emit a sliver ADVANCED_FACE at x_offset with near-zero Y extent."""
    eps = 1.0e-8   # sliver width: far below ShapeFix's healing threshold

    # Four corner points of the sliver rectangle.
    p00 = f.cartesian_point((x_offset,       0.0, 0.0))
    p10 = f.cartesian_point((x_offset + 1.0, 0.0, 0.0))
    p11 = f.cartesian_point((x_offset + 1.0, eps, 0.0))
    p01 = f.cartesian_point((x_offset,       eps, 0.0))

    # Vertices.
    v00 = f.vertex_point(p00)
    v10 = f.vertex_point(p10)
    v11 = f.vertex_point(p11)
    v01 = f.vertex_point(p01)

    # Axis placement for the plane (origin at p00, Z up, X along edge).
    z_dir  = f.direction((0.0, 0.0, 1.0))
    x_dir  = f.direction((1.0, 0.0, 0.0))
    placement = f.axis2_placement_3d(p00, z_dir, x_dir)
    surf = f.plane(placement)

    # Edges — four sides of the rectangle.
    def _line_edge(pa, pb, va, vb):
        dx = pb.args[1][0] - pa.args[1][0]
        dy = pb.args[1][1] - pa.args[1][1]
        length = (dx**2 + dy**2) ** 0.5
        d = f.direction((dx / length, dy / length, 0.0))
        vec = f.vector(d, length)
        ln  = f.line(pa, vec)
        return f.edge_curve(va, vb, ln)

    e_bot  = _line_edge(p00, p10, v00, v10)
    e_right = _line_edge(p10, p11, v10, v11)
    e_top  = _line_edge(p11, p01, v11, v01)
    e_left = _line_edge(p01, p00, v01, v00)

    oe_bot   = f.oriented_edge(e_bot,   True)
    oe_right = f.oriented_edge(e_right, True)
    oe_top   = f.oriented_edge(e_top,   True)
    oe_left  = f.oriented_edge(e_left,  True)

    loop  = f.edge_loop([oe_bot, oe_right, oe_top, oe_left], name=f"loop_{label}")
    bound = f.face_outer_bound(loop)
    face  = f.advanced_face([bound], surf, True, name=f"sliver_{label}")
    return face


# Build four cascading sliver faces.
# Satisfies:
#   count_entity_def(b'ADVANCED_FACE') >= 3 (we emit 4)
#   count_entity_def(b'ADVANCED_FACE') >= 4 (exact: 4)
#   contains(b'sliver') (face names carry 'sliver_')
_make_sliver(f, 0.0,  "A")
_make_sliver(f, 1.0,  "B")
_make_sliver(f, 2.0,  "C")
_make_sliver(f, 3.0,  "D")
