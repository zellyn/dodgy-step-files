"""Tfa121 — ShapeFix_Face.FixWiresTwoCoincEdges different-host-surfaces.

Catalog claim: A face has two wires whose edges geometrically coincide in 3D
but reside on different planes (one on PLANE at z=0, one on an offset PLANE at
z=0.001). FixWiresTwoCoincEdges checks only 3D coincidence and misses the
surface mismatch when merging coincident edges — the merged edge has undefined
surface membership.

Mechanism IS a GEOMETRIC_CURVE_SET containing two ADVANCED_FACEs on two
different (but nearly identical) PLANE instances. The shared edge in 3D
appears on face_A (PLANE at z=0) and face_B (PLANE at z=0.001, offset by 0.001
in Z). The duplicate edge between them is geometrically coincident but
host-surface inconsistent. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa121",
    defect=(
        "GEOMETRIC_CURVE_SET containing two ADVANCED_FACEs on different PLANE instances; "
        "face_A on PLANE at z=0, face_B on PLANE at z=0.001 (offset 0.001 in Z); "
        "both faces share an edge at x=5, y=[0,10] in 3D (same 3D coordinates); "
        "FixWiresTwoCoincEdges finds 3D-coincident edges and merges them; "
        "but merge ignores host-surface mismatch — edge belongs to two different surfaces; "
        "merged edge has undefined surface membership; kernel must check surface identity; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane A at z=0 ────────────────────────────────────────────────────────────
plA_orig = f.cartesian_point((0.0, 0.0, 0.0))
plA_zdir = f.direction((0.0, 0.0, 1.0))
plA_xdir = f.direction((1.0, 0.0, 0.0))
plA_plc  = f.axis2_placement_3d(plA_orig, plA_zdir, plA_xdir)
planeA   = f._emit_raw(f"PLANE('host_plane_z0',#{plA_plc.eid})")

# ── Plane B at z=0.001 (offset) ───────────────────────────────────────────────
plB_orig = f.cartesian_point((0.0, 0.0, 0.001))
plB_zdir = f.direction((0.0, 0.0, 1.0))
plB_xdir = f.direction((1.0, 0.0, 0.0))
plB_plc  = f.axis2_placement_3d(plB_orig, plB_zdir, plB_xdir)
planeB   = f._emit_raw(f"PLANE('host_plane_z0001',#{plB_plc.eid})")

# ── Helper: rectangular face wire on z=z_val ──────────────────────────────────
def make_rect_face(x0, x1, y0, y1, z_val, plane_ref, face_name):
    cp00 = f.cartesian_point((x0, y0, z_val))
    cp10 = f.cartesian_point((x1, y0, z_val))
    cp11 = f.cartesian_point((x1, y1, z_val))
    cp01 = f.cartesian_point((x0, y1, z_val))

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
    af  = f._emit_raw(f"ADVANCED_FACE('{face_name}',(#{fob.eid}),#{plane_ref.eid},.T.)")
    return af

# Face A on z=0, face B on z=0.001; shared 3D edge at x=5, y=[0,10] is
# geometrically coincident between them but host-surface differs
face_a = make_rect_face(0.0, 5.0, 0.0, 10.0, 0.0,   planeA, "face_A_z0")
face_b = make_rect_face(5.0, 10.0, 0.0, 10.0, 0.001, planeB, "face_B_z0001")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('',( #{face_a.eid},#{face_b.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa121.stp")
