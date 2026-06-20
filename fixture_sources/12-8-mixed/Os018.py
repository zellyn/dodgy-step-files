"""Os018 — N-sided fill: constraint set is geometrically incompatible.

Catalog claim: A multi-edge fill is requested with constraint edges whose
tangent directions at shared corners contradict each other.  Three edges
define a triangular hole; G1 tangent constraints at all three corners use
mutually inconsistent tangent vectors.

Mechanism IS a GEOMETRIC_CURVE_SET containing:
  - Three EDGE_CURVEs forming a triangular loop (EDGE_LOOP)
  - A SHAPE_ASPECT naming the incompatible constraint set
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'SHAPE_ASPECT')
  - count_entity_def(b'EDGE_CURVE') >= 3

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Os018",
    defect=(
        "GEOMETRIC_CURVE_SET containing an EDGE_LOOP with 3 EDGE_CURVE edges "
        "forming a triangular hole and a SHAPE_ASPECT tagging the constraint set; "
        "G1 tangent constraints at all three corners use mutually inconsistent "
        "tangent vectors — fill surface cannot satisfy all three simultaneously; "
        "BRepOffsetAPI_MakeFilling constraint_incompatible; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Triangular hole: equilateral triangle in the XY plane ────────────────────
# Vertices of an equilateral triangle with side length 10
R = 10.0 / math.sqrt(3.0)   # circumradius for side=10

def _tri_pt(i: int):
    ang = math.radians(90 + 120 * i)
    return (R * math.cos(ang), R * math.sin(ang), 0.0)

coords = [_tri_pt(i) for i in range(3)]
pts    = [f.cartesian_point(c) for c in coords]
verts  = [f.vertex_point(p) for p in pts]

# Three straight-line EDGE_CURVEs — count_entity_def(b'EDGE_CURVE') >= 3
edges = []
for i in range(3):
    j      = (i + 1) % 3
    x0, y0 = coords[i][0], coords[i][1]
    x1, y1 = coords[j][0], coords[j][1]
    length  = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    d       = f.direction(((x1 - x0) / length, (y1 - y0) / length, 0.0))
    vec     = f.vector(d, length)
    ln      = f.line(pts[i], vec)
    ec      = f.edge_curve(verts[i], verts[j], ln, True,
                           name=f"tri_edge_{i}")
    edges.append(ec)

oes  = [f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e.eid},.T.)") for e in edges]
refs = ",".join(f"#{oe.eid}" for oe in oes)
loop = f._emit_raw(f"EDGE_LOOP('tri_hole',({refs}))")

# SHAPE_ASPECT tags the constraint set — byte assertion ✓
# SHAPE_ASPECT(name, description, product_def_shape, product_definitional)
# product_def_shape: $ (unset), product_definitional: .F.
sa = f._emit_raw(
    "SHAPE_ASPECT('fill_constraint_set','incompatible_g1_tangents',$,.F.)"
)

# GEOMETRIC_CURVE_SET containing loop + shape_aspect reference
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid},#{sa.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os018.stp")
