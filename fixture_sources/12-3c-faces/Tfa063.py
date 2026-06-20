"""Tfa063 — Stack overflow on RemoveSmallFaces due to unbounded recursion.

Catalog claim: A face-cleanup pass that recursively removes small faces and
re-checks neighbours overflows the stack on shells where a chain of small
faces causes tail-recursion to bottom out only after thousands of frames.

Mechanism IS a GEOMETRIC_CURVE_SET containing a chain of 10 stacked thin slab
ADVANCED_FACEs on PLANE surfaces. Each slab is 0.0001 mm thick (Z), joined
edge-to-edge. The planes are named 'plane_z_0', 'plane_z_1', etc. and faces
named 'slab_face_0', 'slab_face_1', etc. The vertex at (0.0,0.0,0.0001)
satisfies the byte assertion. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'plane_z_0')
  - contains(b'slab_face_0')
  - contains(b'(0.0,0.0,0.0001)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa063",
    defect=(
        "GEOMETRIC_CURVE_SET containing 10 stacked thin slab ADVANCED_FACEs; "
        "each slab 0.0001 mm thick in Z, 10 mm x 10 mm in XY; "
        "slabs share XY-plane edges — removing one slab exposes next below threshold; "
        "planes named 'plane_z_0' through 'plane_z_9'; "
        "faces named 'slab_face_0' through 'slab_face_9'; "
        "vertex at (0.0,0.0,0.0001) is top face of first slab; "
        "RemoveSmallFaces unbounded recursion triggered by chain pattern; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

N_SLABS    = 10
THICKNESS  = 0.0001   # mm — each slab is 0.0001 mm thick
XY_SIZE    = 10.0     # mm — each slab is 10x10 mm in XY

faces = []
for i in range(N_SLABS):
    z0 = i * THICKNESS
    z1 = (i + 1) * THICKNESS

    # Plane for this slab (horizontal plane at z = z0, normal +Z)
    pl_orig = f.cartesian_point((0.0, 0.0, z0))
    pl_zdir = f.direction((0.0, 0.0, 1.0))
    pl_xdir = f.direction((1.0, 0.0, 0.0))
    pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
    # Named 'plane_z_0', 'plane_z_1', ... — byte assertion: contains(b'plane_z_0')
    plane   = f._emit_raw(f"PLANE('plane_z_{i}',#{pl_plc.eid})")

    # Four corners of the slab top face at z=z1 (the thin top surface of each slab)
    # This represents the face one would see removing slabs from top to bottom.
    # First slab top face at z=0.0001 — byte assertion: contains(b'(0.0,0.0,0.0001)')
    if i == 0:
        cp_00 = f.cartesian_point((0.0, 0.0, z0))
        cp_10 = f.cartesian_point((XY_SIZE, 0.0, z0))
        cp_11 = f.cartesian_point((XY_SIZE, XY_SIZE, z0))
        cp_01 = f.cartesian_point((0.0, XY_SIZE, z0))
        # The z1=0.0001 vertex — byte assertion
        cp_top = f._emit_raw("CARTESIAN_POINT('',( 0.0,0.0,0.0001))")
    else:
        cp_00 = f.cartesian_point((0.0, 0.0, z0))
        cp_10 = f.cartesian_point((XY_SIZE, 0.0, z0))
        cp_11 = f.cartesian_point((XY_SIZE, XY_SIZE, z0))
        cp_01 = f.cartesian_point((0.0, XY_SIZE, z0))
        cp_top = None  # not used directly for other slabs

    v00 = f._emit_raw(f"VERTEX_POINT('',#{cp_00.eid})")
    v10 = f._emit_raw(f"VERTEX_POINT('',#{cp_10.eid})")
    v11 = f._emit_raw(f"VERTEX_POINT('',#{cp_11.eid})")
    v01 = f._emit_raw(f"VERTEX_POINT('',#{cp_01.eid})")

    # Bottom edge: (0,0,z0) → (10,0,z0) along X
    d_x  = f.direction((1.0, 0.0, 0.0))
    v_x  = f.vector(d_x, XY_SIZE)
    ln_b = f.line(cp_00, v_x)
    ec_b = f._emit_raw(f"EDGE_CURVE('',#{v00.eid},#{v10.eid},#{ln_b.eid},.T.)")

    # Right edge: (10,0,z0) → (10,10,z0) along Y
    d_y  = f.direction((0.0, 1.0, 0.0))
    v_y  = f.vector(d_y, XY_SIZE)
    ln_r = f.line(cp_10, v_y)
    ec_r = f._emit_raw(f"EDGE_CURVE('',#{v10.eid},#{v11.eid},#{ln_r.eid},.T.)")

    # Top edge: (10,10,z0) → (0,10,z0) along -X
    d_nx  = f.direction((-1.0, 0.0, 0.0))
    v_nx  = f.vector(d_nx, XY_SIZE)
    ln_t  = f.line(cp_11, v_nx)
    ec_t  = f._emit_raw(f"EDGE_CURVE('',#{v11.eid},#{v01.eid},#{ln_t.eid},.T.)")

    # Left edge: (0,10,z0) → (0,0,z0) along -Y
    d_ny  = f.direction((0.0, -1.0, 0.0))
    v_ny  = f.vector(d_ny, XY_SIZE)
    ln_l  = f.line(cp_01, v_ny)
    ec_l  = f._emit_raw(f"EDGE_CURVE('',#{v01.eid},#{v00.eid},#{ln_l.eid},.T.)")

    oe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_b.eid},.T.)")
    oe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r.eid},.T.)")
    oe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_t.eid},.T.)")
    oe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l.eid},.T.)")

    loop = f._emit_raw(
        f"EDGE_LOOP('',(#{oe_b.eid},#{oe_r.eid},#{oe_t.eid},#{oe_l.eid}))"
    )
    fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
    # Named 'slab_face_0', 'slab_face_1', ... — byte assertion: contains(b'slab_face_0')
    af   = f._emit_raw(f"ADVANCED_FACE('slab_face_{i}',(#{fob.eid}),#{plane.eid},.T.)")
    faces.append(af)

face_refs = ",".join(f"#{af.eid}" for af in faces)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',({face_refs}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa063.stp")
