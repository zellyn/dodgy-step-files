"""Ad102 — Crash transferring HLR-created shapes via STEP writer.

Catalog claim: a shape produced by Hidden Line Removal (HLR) consists of
2D edges in 3D space (no faces, no surfaces). The STEP writer's
topology-to-STEP translator expects every edge to belong to a face;
segfaults on the bare-edge HLR result.

Reproducer recipe: Compound of EDGE_CURVEs with no incident face; pass
to STEP writer.

Byte assertions:
  contains(b'EDGE_CURVE') and contains(b'hlr')
  contains(b'EDGE_CURVE') and contains(b'VERTEX_POINT')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad102",
    defect=(
        "bare-edge HLR shape: EDGE_CURVEs with no incident face; "
        "STEP writer expects every edge to belong to a face; "
        "segfaults on bare-edge / bare-vertex HLR result; "
        "writer must handle bare shapes via WIRE_SHELL representation "
        "with no face references; must not crash on bare shapes; "
        "OCCT MANTIS#0027070; See also Tsh037; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: a compound of bare EDGE_CURVEs with no FACE or SURFACE.
# This mimics the output of Hidden Line Removal (HLR) — a set of 2D edges
# in 3D space that are not attached to any face. The STEP writer crashes
# because it expects all edges to have incident faces.
#
# Satisfies:
#   contains(b'EDGE_CURVE') and contains(b'hlr')
#   contains(b'EDGE_CURVE') and contains(b'VERTEX_POINT')

# HLR result: three silhouette-edge EDGE_CURVEs in the XY plane.
# No ADVANCED_FACE, no surface reference — pure bare-edge compound.

# Silhouette edge 1: a horizontal line at y=1 (visible top edge of a sphere).
hlr_p0 = f.cartesian_point((-1.0, 1.0, 0.0), name="hlr_p0")
hlr_p1 = f.cartesian_point(( 1.0, 1.0, 0.0), name="hlr_p1")
hlr_v0 = f.vertex_point(hlr_p0, name="hlr_v0")
hlr_v1 = f.vertex_point(hlr_p1, name="hlr_v1")
d_x   = f.direction((1.0, 0.0, 0.0))
vec1  = f.vector(d_x, 2.0)
ln1   = f.line(hlr_p0, vec1, name="hlr_silhouette_line1")
ec1   = f.edge_curve(hlr_v0, hlr_v1, ln1, same_sense=True, name="hlr_edge1")

# Silhouette edge 2: a horizontal line at y=-1 (visible bottom edge).
hlr_p2 = f.cartesian_point((-1.0, -1.0, 0.0), name="hlr_p2")
hlr_p3 = f.cartesian_point(( 1.0, -1.0, 0.0), name="hlr_p3")
hlr_v2 = f.vertex_point(hlr_p2, name="hlr_v2")
hlr_v3 = f.vertex_point(hlr_p3, name="hlr_v3")
vec2  = f.vector(d_x, 2.0)
ln2   = f.line(hlr_p2, vec2, name="hlr_silhouette_line2")
ec2   = f.edge_curve(hlr_v2, hlr_v3, ln2, same_sense=True, name="hlr_edge2")

# Silhouette edge 3: a vertical contour line at x=0 (profile edge).
hlr_p4 = f.cartesian_point((0.0, -1.0, 0.0), name="hlr_p4")
hlr_p5 = f.cartesian_point((0.0,  1.0, 0.0), name="hlr_p5")
hlr_v4 = f.vertex_point(hlr_p4, name="hlr_v4")
hlr_v5 = f.vertex_point(hlr_p5, name="hlr_v5")
d_y   = f.direction((0.0, 1.0, 0.0))
vec3  = f.vector(d_y, 2.0)
ln3   = f.line(hlr_p4, vec3, name="hlr_silhouette_line3")
ec3   = f.edge_curve(hlr_v4, hlr_v5, ln3, same_sense=True, name="hlr_edge3")

# Group the bare edges into a GEOMETRIC_CURVE_SET named 'hlr_result'.
# This is the model entity the STEP writer receives: no face topology at all.
# Satisfies: contains(b'hlr') via entity names; contains(b'EDGE_CURVE')
f._emit_raw(
    f"GEOMETRIC_CURVE_SET('hlr_result',({ec1.ref()},{ec2.ref()},{ec3.ref()}))"
)
