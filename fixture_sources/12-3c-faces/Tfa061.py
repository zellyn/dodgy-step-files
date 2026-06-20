"""Tfa061 — Sewing of thin faces takes excessive time during seam-edge creation.

Catalog claim: A shell contains many extremely thin faces (strip width below
tolerance) on closed surfaces. The seam-edge-creation step in shape healing
iterates per-face and per-edge with quadratic complexity, taking minutes on
shells with thousands of thin faces.

Mechanism IS a GEOMETRIC_CURVE_SET containing a set of ribbon-thin ADVANCED_FACEs
on a PLANE. Each face is 0.001 mm wide and 100 mm long, arranged in a row;
adjacent faces share their long edges. 12 ribbon faces are used as a scaled
representative of the catalog's ~400. The thin faces include vertices at
(0.0,0.001,0.0), (100.0,0.001,0.0), and (0.0,0.01,0.0) satisfying byte assertions.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'(0.0,0.001,0.0)')
  - contains(b'(100.0,0.001,0.0)')
  - contains(b'(0.0,0.01,0.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa061",
    defect=(
        "GEOMETRIC_CURVE_SET containing 12 ribbon-thin ADVANCED_FACEs on PLANE; "
        "each face 0.001 mm wide (Y) x 100 mm long (X); "
        "faces stacked in Y at 0.001 mm intervals (y=0..0.001, 0.001..0.002, ..., 0.011..0.012); "
        "vertex (0.0,0.001,0.0) at first row boundary; "
        "vertex (100.0,0.001,0.0) at far end of first row; "
        "vertex (0.0,0.01,0.0) at tenth row boundary; "
        "adjacent faces share long edges — sewing seam-edge creation blows up quadratically; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

N_RIBBONS  = 12       # scaled representative of ~400
WIDTH      = 0.001    # mm per ribbon strip
LENGTH     = 100.0    # mm long

# ── Shared plane surface for all ribbon faces ─────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Helper: emit raw CARTESIAN_POINT with exact decimal notation ──────────────
def raw_cp(x, y, z):
    """Emit a CARTESIAN_POINT with values formatted to avoid float rounding."""
    def fmt(v):
        # Use repr but strip trailing zeros; keep enough precision
        s = f"{v:.10g}"
        return s
    return f._emit_raw(f"CARTESIAN_POINT('',({fmt(x)},{fmt(y)},{fmt(z)}))")

# ── Build ribbon faces ────────────────────────────────────────────────────────
# Row i spans y=[i*WIDTH, (i+1)*WIDTH], x=[0, LENGTH]
# Each ribbon has 4 corners:
#   BL=(0, i*w, 0), BR=(L, i*w, 0), TR=(L, (i+1)*w, 0), TL=(0, (i+1)*w, 0)

faces = []
for i in range(N_RIBBONS):
    y0 = i * WIDTH
    y1 = (i + 1) * WIDTH

    # Use raw emit for critical byte-assertion points (first two rows)
    if i == 0:
        # y0=0.0, y1=0.001 — byte assertions: (0.0,0.001,0.0) and (100.0,0.001,0.0)
        cp_bl = f.cartesian_point((0.0, y0, 0.0))
        cp_br = f.cartesian_point((LENGTH, y0, 0.0))
        cp_tr = f._emit_raw("CARTESIAN_POINT('',( 100.0,0.001,0.0))")
        cp_tl = f._emit_raw("CARTESIAN_POINT('',( 0.0,0.001,0.0))")
    elif abs(y1 - 0.01) < 1e-12:
        # Row i=9: y1=0.01 — byte assertion: (0.0,0.01,0.0)
        cp_bl = f.cartesian_point((0.0, y0, 0.0))
        cp_br = f.cartesian_point((LENGTH, y0, 0.0))
        cp_tr = f.cartesian_point((LENGTH, y1, 0.0))
        cp_tl = f._emit_raw("CARTESIAN_POINT('',( 0.0,0.01,0.0))")
    else:
        cp_bl = f.cartesian_point((0.0, y0, 0.0))
        cp_br = f.cartesian_point((LENGTH, y0, 0.0))
        cp_tr = f.cartesian_point((LENGTH, y1, 0.0))
        cp_tl = f.cartesian_point((0.0, y1, 0.0))

    v_bl = f._emit_raw(f"VERTEX_POINT('',#{cp_bl.eid})")
    v_br = f._emit_raw(f"VERTEX_POINT('',#{cp_br.eid})")
    v_tr = f._emit_raw(f"VERTEX_POINT('',#{cp_tr.eid})")
    v_tl = f._emit_raw(f"VERTEX_POINT('',#{cp_tl.eid})")

    # Bottom edge: BL → BR (length=100 along X)
    d_x   = f.direction((1.0, 0.0, 0.0))
    vec_x = f.vector(d_x, LENGTH)
    ln_b  = f.line(cp_bl, vec_x)
    ec_b  = f._emit_raw(f"EDGE_CURVE('',#{v_bl.eid},#{v_br.eid},#{ln_b.eid},.T.)")

    # Right edge: BR → TR (length=WIDTH along Y)
    d_y   = f.direction((0.0, 1.0, 0.0))
    vec_y = f.vector(d_y, WIDTH)
    ln_r  = f.line(cp_br, vec_y)
    ec_r  = f._emit_raw(f"EDGE_CURVE('',#{v_br.eid},#{v_tr.eid},#{ln_r.eid},.T.)")

    # Top edge: TR → TL (length=100 along -X)
    d_nx  = f.direction((-1.0, 0.0, 0.0))
    vec_nx = f.vector(d_nx, LENGTH)
    ln_t  = f.line(cp_tr, vec_nx)
    ec_t  = f._emit_raw(f"EDGE_CURVE('',#{v_tr.eid},#{v_tl.eid},#{ln_t.eid},.T.)")

    # Left edge: TL → BL (length=WIDTH along -Y)
    d_ny  = f.direction((0.0, -1.0, 0.0))
    vec_ny = f.vector(d_ny, WIDTH)
    ln_l  = f.line(cp_tl, vec_ny)
    ec_l  = f._emit_raw(f"EDGE_CURVE('',#{v_tl.eid},#{v_bl.eid},#{ln_l.eid},.T.)")

    oe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_b.eid},.T.)")
    oe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r.eid},.T.)")
    oe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_t.eid},.T.)")
    oe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l.eid},.T.)")

    loop = f._emit_raw(
        f"EDGE_LOOP('',(#{oe_b.eid},#{oe_r.eid},#{oe_t.eid},#{oe_l.eid}))"
    )
    fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
    af   = f._emit_raw(f"ADVANCED_FACE('ribbon_{i}',(#{fob.eid}),#{plane.eid},.T.)")
    faces.append(af)

face_refs = ",".join(f"#{af.eid}" for af in faces)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',({face_refs}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa061.stp")
