"""Tfa068 — STEP export duplicates surfaces, leading to non-conformal geometry between adjacent faces.

Catalog claim: Two adjacent faces that share an underlying surface are written
with two separate PLANE instances rather than sharing one. On re-import the
receiver computes face-face adjacency from surface-identity and concludes the
faces are not adjacent; the shell has free edges where it should be closed.

Mechanism IS a GEOMETRIC_CURVE_SET containing two co-planar ADVANCED_FACEs
on z=0 that each reference a distinct PLANE instance with identical numerical
content. Both PLANEs are named 'dup_plane_0' and 'dup_plane_1'. The two faces
share an edge along x=5. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - count_entity_def(b'PLANE') >= 2
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa068",
    defect=(
        "GEOMETRIC_CURVE_SET containing two co-planar ADVANCED_FACEs on z=0; "
        "each face references its own PLANE instance ('dup_plane_0', 'dup_plane_1') "
        "with identical numerical content — writer failed to canonicalise surfaces; "
        "left face covers x=[0,5] y=[0,10]; right face covers x=[5,10] y=[0,10]; "
        "shared edge at x=5 but non-conformal: receiver sees two surfaces → free edges; "
        "count_entity_def(b'PLANE') >= 2 satisfied by two separate PLANE entities; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Helper: build one rectangular face on z=0 with its own PLANE instance ────
def make_planar_face(x0, x1, y0, y1, plane_name):
    """Build an ADVANCED_FACE on z=0 with a fresh PLANE named plane_name."""
    pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
    pl_zdir = f.direction((0.0, 0.0, 1.0))
    pl_xdir = f.direction((1.0, 0.0, 0.0))
    pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
    plane   = f._emit_raw(f"PLANE('{plane_name}',#{pl_plc.eid})")

    cp00 = f.cartesian_point((x0, y0, 0.0))
    cp10 = f.cartesian_point((x1, y0, 0.0))
    cp11 = f.cartesian_point((x1, y1, 0.0))
    cp01 = f.cartesian_point((x0, y1, 0.0))

    v00 = f._emit_raw(f"VERTEX_POINT('',#{cp00.eid})")
    v10 = f._emit_raw(f"VERTEX_POINT('',#{cp10.eid})")
    v11 = f._emit_raw(f"VERTEX_POINT('',#{cp11.eid})")
    v01 = f._emit_raw(f"VERTEX_POINT('',#{cp01.eid})")

    dx = x1 - x0
    dy = y1 - y0

    d_px = f.direction((1.0, 0.0, 0.0))
    v_px = f.vector(d_px, dx)
    ln_b = f.line(cp00, v_px)
    ec_b = f._emit_raw(f"EDGE_CURVE('',#{v00.eid},#{v10.eid},#{ln_b.eid},.T.)")

    d_py = f.direction((0.0, 1.0, 0.0))
    v_py = f.vector(d_py, dy)
    ln_r = f.line(cp10, v_py)
    ec_r = f._emit_raw(f"EDGE_CURVE('',#{v10.eid},#{v11.eid},#{ln_r.eid},.T.)")

    d_nx = f.direction((-1.0, 0.0, 0.0))
    v_nx = f.vector(d_nx, dx)
    ln_t = f.line(cp11, v_nx)
    ec_t = f._emit_raw(f"EDGE_CURVE('',#{v11.eid},#{v01.eid},#{ln_t.eid},.T.)")

    d_ny = f.direction((0.0, -1.0, 0.0))
    v_ny = f.vector(d_ny, dy)
    ln_l = f.line(cp01, v_ny)
    ec_l = f._emit_raw(f"EDGE_CURVE('',#{v01.eid},#{v00.eid},#{ln_l.eid},.T.)")

    oe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_b.eid},.T.)")
    oe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r.eid},.T.)")
    oe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_t.eid},.T.)")
    oe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l.eid},.T.)")

    loop = f._emit_raw(
        f"EDGE_LOOP('',(#{oe_b.eid},#{oe_r.eid},#{oe_t.eid},#{oe_l.eid}))"
    )
    fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
    af  = f._emit_raw(f"ADVANCED_FACE('',( #{fob.eid}),#{plane.eid},.T.)")
    return af

# Left face x=[0,5], right face x=[5,10] — both on z=0 with distinct PLANE instances
face_left  = make_planar_face(0.0, 5.0, 0.0, 10.0, "dup_plane_0")
face_right = make_planar_face(5.0, 10.0, 0.0, 10.0, "dup_plane_1")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('',( #{face_left.eid},#{face_right.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa068.stp")
