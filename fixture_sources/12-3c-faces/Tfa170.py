"""Tfa170 — ShapeFix_Face.FixWiresTwoCoincEdges asymmetric-tolerance-merge.

Catalog claim: Two inner wires with identical geometry but different per-vertex
tolerances (inner_tight_tol=0.001 vs inner_loose_tol=0.1). FixWiresTwoCoincEdges
merges coincident edges using the first wire's tolerance values and silently
discards the second wire's tighter constraints, potentially losing precision
requirements.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
face has a rectangular outer boundary (20×20) and two inner rectangular wires
of identical geometry (5×5 at (5,5)-(10,10)) but carrying different vertex
tolerances via VERTEX_POINT names. OCC sees a GEOMETRIC_CURVE_SET and returns
empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa170",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "outer wire: 20×20 rectangle; "
        "two inner wires with identical 5×5 geometry at (5,5)-(10,10) "
        "but differing vertex tolerance labels (tight=0.001, loose=0.1); "
        "FixWiresTwoCoincEdges merges using first wire tolerances, "
        "silently discarding second wire's constraints; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Outer wire: 20×20 rectangle ───────────────────────────────────────────────
op0 = f.cartesian_point((0.0,  0.0,  0.0))
op1 = f.cartesian_point((20.0, 0.0,  0.0))
op2 = f.cartesian_point((20.0, 20.0, 0.0))
op3 = f.cartesian_point((0.0,  20.0, 0.0))

ov0 = f._emit_raw(f"VERTEX_POINT('',#{op0.eid})")
ov1 = f._emit_raw(f"VERTEX_POINT('',#{op1.eid})")
ov2 = f._emit_raw(f"VERTEX_POINT('',#{op2.eid})")
ov3 = f._emit_raw(f"VERTEX_POINT('',#{op3.eid})")

od_px = f.direction((1.0,  0.0, 0.0))
od_py = f.direction((0.0,  1.0, 0.0))
od_nx = f.direction((-1.0, 0.0, 0.0))
od_ny = f.direction((0.0, -1.0, 0.0))

oln_b = f.line(op0, f.vector(od_px, 20.0))
oln_r = f.line(op1, f.vector(od_py, 20.0))
oln_t = f.line(op2, f.vector(od_nx, 20.0))
oln_l = f.line(op3, f.vector(od_ny, 20.0))

oec_b = f._emit_raw(f"EDGE_CURVE('oe_b',#{ov0.eid},#{ov1.eid},#{oln_b.eid},.T.)")
oec_r = f._emit_raw(f"EDGE_CURVE('oe_r',#{ov1.eid},#{ov2.eid},#{oln_r.eid},.T.)")
oec_t = f._emit_raw(f"EDGE_CURVE('oe_t',#{ov2.eid},#{ov3.eid},#{oln_t.eid},.T.)")
oec_l = f._emit_raw(f"EDGE_CURVE('oe_l',#{ov3.eid},#{ov0.eid},#{oln_l.eid},.T.)")

ooe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_b.eid},.T.)")
ooe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_r.eid},.T.)")
ooe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_t.eid},.T.)")
ooe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_l.eid},.T.)")

outer_loop = f._emit_raw(
    f"EDGE_LOOP('outer_loop',"
    f"(#{ooe_b.eid},#{ooe_r.eid},#{ooe_t.eid},#{ooe_l.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")

# ── Helper to build a 5×5 inner wire at (5,5)-(10,10) ────────────────────────
def make_inner_wire(tol_label: str):
    """Build a 5×5 rectangular inner wire with tolerance label in vertex names."""
    tp0 = f.cartesian_point((5.0,  5.0,  0.0))
    tp1 = f.cartesian_point((10.0, 5.0,  0.0))
    tp2 = f.cartesian_point((10.0, 10.0, 0.0))
    tp3 = f.cartesian_point((5.0,  10.0, 0.0))

    tv0 = f._emit_raw(f"VERTEX_POINT('{tol_label}',#{tp0.eid})")
    tv1 = f._emit_raw(f"VERTEX_POINT('{tol_label}',#{tp1.eid})")
    tv2 = f._emit_raw(f"VERTEX_POINT('{tol_label}',#{tp2.eid})")
    tv3 = f._emit_raw(f"VERTEX_POINT('{tol_label}',#{tp3.eid})")

    ld_px = f.direction((1.0,  0.0, 0.0))
    ld_py = f.direction((0.0,  1.0, 0.0))
    ld_nx = f.direction((-1.0, 0.0, 0.0))
    ld_ny = f.direction((0.0, -1.0, 0.0))

    ln_b = f.line(tp0, f.vector(ld_px, 5.0))
    ln_r = f.line(tp1, f.vector(ld_py, 5.0))
    ln_t = f.line(tp2, f.vector(ld_nx, 5.0))
    ln_l = f.line(tp3, f.vector(ld_ny, 5.0))

    ec_b = f._emit_raw(f"EDGE_CURVE('ib',#{tv0.eid},#{tv1.eid},#{ln_b.eid},.T.)")
    ec_r = f._emit_raw(f"EDGE_CURVE('ir',#{tv1.eid},#{tv2.eid},#{ln_r.eid},.T.)")
    ec_t = f._emit_raw(f"EDGE_CURVE('it',#{tv2.eid},#{tv3.eid},#{ln_t.eid},.T.)")
    ec_l = f._emit_raw(f"EDGE_CURVE('il',#{tv3.eid},#{tv0.eid},#{ln_l.eid},.T.)")

    oe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_b.eid},.T.)")
    oe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r.eid},.T.)")
    oe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_t.eid},.T.)")
    oe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l.eid},.T.)")

    loop = f._emit_raw(
        f"EDGE_LOOP('inner_{tol_label}',"
        f"(#{oe_b.eid},#{oe_r.eid},#{oe_t.eid},#{oe_l.eid}))"
    )
    return loop

# ── Two coincident inner wires: tight tolerance vs loose tolerance ─────────────
inner_tight = make_inner_wire("tight_tol_0.001")
inner_loose  = make_inner_wire("loose_tol_0.1")

fb_tight = f._emit_raw(f"FACE_BOUND('',#{inner_tight.eid},.F.)")
fb_loose  = f._emit_raw(f"FACE_BOUND('',#{inner_loose.eid},.F.)")

af = f._emit_raw(
    f"ADVANCED_FACE('coinc_tol_face',"
    f"(#{fob.eid},#{fb_tight.eid},#{fb_loose.eid}),"
    f"#{plane.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa170.stp")
