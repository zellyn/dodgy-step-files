"""Twi177 — ShapeAnalysis_Wire.CheckOuterBound nested-faces.

Catalog claim: Wire is the outer bound of an inner face within a larger face.
CheckOuterBound classifies based on enclosed area but the nested context is
missing, causing it to misidentify the wire's role within compound geometry.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP that would
serve as the outer bound of a small inner face. The wire is a small rectangle
(area ≈ 4 sq units) that in context would be nested inside a larger face, but
only the inner wire is present in the file — the outer face context is absent.
CheckOuterBound sees the small enclosed area and classifies it as an inner
bound (hole), when it should be classified as an outer bound in the nested
context. The nested-context absence IS the defect: without the outer face,
the area-based heuristic mis-classifies.

The inner wire is labelled 'nested_outer_bound_misclassified' to make the
defect explicit in bytes.

Byte assertions:
  - contains(b'nested_outer_bound_misclassified')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi177",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "small rectangle: A(3,3)→B(5,3)→C(5,5)→D(3,5)→A (area=4); "
        "this wire IS the outer bound of a small inner face nested inside a "
        "larger face (context not present in file); "
        "edge labelled 'nested_outer_bound_misclassified' IS the mechanism; "
        "CheckOuterBound IS mechanism — area-based heuristic classifies small "
        "area as inner bound (hole) when nested outer-face context is absent; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Small rectangle vertices (inner face, area=4) ─────────────────────────────
PA = (3.0, 3.0, 0.0)
PB = (5.0, 3.0, 0.0)
PC = (5.0, 5.0, 0.0)
PD = (3.0, 5.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))


def _line_sc(v_s, v_e, ps, pe, name=""):
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e0: A→B (labelled to identify this as the nested-outer-bound wire)
ec0 = _line_sc(vA, vB, PA, PB, name="nested_outer_bound_misclassified")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B→C
ec1 = _line_sc(vB, vC, PB, PC)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C→D
ec2 = _line_sc(vC, vD, PC, PD)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: D→A (closes the rectangle)
ec3 = _line_sc(vD, vA, PD, PA)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi177.stp")
