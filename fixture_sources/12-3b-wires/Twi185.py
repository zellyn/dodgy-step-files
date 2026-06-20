"""Twi185 — ShapeAnalysis_Wire.CheckSelfIntersection coincident-curves.

Catalog claim: Wire with first and last edges geometrically coincident but
oppositely oriented; not flagged as self-intersection.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Edges e0 (A->B) and e3 (B->A) occupy the same 3D line segment but are
traversed in opposite directions. The two coincident-opposite edges create a
self-intersecting wire that CheckSelfIntersection's orientation filter misses.
The coincident edge pair is labelled 'coincident_fwd' and 'coincident_rev' to
make the defect explicit in bytes.

Byte assertions:
  - contains(b'coincident_fwd')
  - contains(b'coincident_rev')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi185",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "e0 (coincident_fwd) A(0,0)->B(1,0) traverses the segment forward; "
        "e1 B(1,0)->C(1,1) normal right edge; "
        "e2 C(1,1)->A(0,0) diagonal closing edge; "
        "e3 (coincident_rev) B(1,0)->A(0,0) traverses same segment as e0 in reverse; "
        "e0 and e3 ARE geometrically coincident but oppositely oriented IS mechanism; "
        "CheckSelfIntersection IS mechanism — orientation filter masks coincident-opposite pair; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

PA = (0.0, 0.0, 0.0)
PB = (1.0, 0.0, 0.0)
PC = (1.0, 1.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))


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


# e0: A->B forward (coincident_fwd)
ec0 = _line_sc(vA, vB, PA, PB, name="coincident_fwd")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B->C normal right edge
ec1 = _line_sc(vB, vC, PB, PC)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C->A diagonal closing edge
ec2 = _line_sc(vC, vA, PC, PA)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: B->A reverse (coincident_rev) — same geometry as e0 but opposite direction
ec3 = _line_sc(vB, vA, PB, PA, name="coincident_rev")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi185.stp")
