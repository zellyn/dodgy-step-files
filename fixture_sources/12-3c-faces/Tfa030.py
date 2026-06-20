"""Tfa030 — ADVANCED_FACE PLANE AXIS2_PLACEMENT_3D ignored relative to
raw-global CARTESIAN_POINT bounds (subshape replacement helper drops local
placement).

Catalog claim: A face's local placement transform is lost or ignored relative
to its bounding vertices. An ADVANCED_FACE references a PLANE whose
AXIS2_PLACEMENT_3D origin is shifted (e.g. to (3,4,5)) and x-axis rotated
(e.g. 30°), but the EDGE_LOOP's CARTESIAN_POINTs are written in raw global
coordinates as if the placement were identity.

Mechanism: OPEN_SHELL with TWO ADVANCED_FACEs:
  face[0]: PLANE with a non-identity AXIS2_PLACEMENT_3D — origin (3,4,5),
    z-axis (0,0,1), x-axis rotated 30° in xy-plane
    (cos30=0.866, sin30=0.5). But the EDGE_LOOP vertices are given in raw
    global coordinates (10×10 square at z=0 in global frame, no placement
    applied). The discrepancy between the PLANE's local placement and the
    EDGE_LOOP's raw-global vertex coords IS the defect.
  face[1]: A valid reference face on a standard plane at z=1 to ensure
    shape(1) loads.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa030",
    defect=(
        "OPEN_SHELL: face[0] PLANE with non-identity AXIS2_PLACEMENT_3D "
        "(origin=(3,4,5), z-axis=(0,0,1), x-axis=(cos30°,sin30°,0)=(0.866,0.5,0)) "
        "but EDGE_LOOP vertices are raw-global (10×10 square at z=0 in global frame); "
        "subshape-replacement helper drops local placement — vertices in global frame "
        "disagree with PLANE's shifted+rotated local frame; "
        "face[1] is a valid 10×10 plane at z=1 so OCC loads shape(1); "
        "defect IS on live OPEN_SHELL traversal path: both faces wired into shell"
    ),
)

cos30 = math.cos(math.radians(30.0))
sin30 = math.sin(math.radians(30.0))

# ── face[0]: PLANE with non-identity placement — the defect ──────────────────
# PLANE origin shifted to (3,4,5), x-axis rotated 30° in xy-plane.
# But EDGE_LOOP vertices live in raw global coordinates (z=0, 10×10 box).
# A correct reader applies the inverse placement to evaluate the plane at
# the given bounding vertex coordinates; a buggy reader (or subshape-
# replacement helper) drops the placement, treating it as identity.

defect_orig = f.cartesian_point((3.0, 4.0, 5.0))          # shifted origin
defect_zdir = f.direction((0.0, 0.0, 1.0))                # normal (z)
defect_xdir = f.direction((cos30, sin30, 0.0))            # x-axis rotated 30°
defect_plc  = f.axis2_placement_3d(defect_orig, defect_zdir, defect_xdir)
defect_plane = f.plane(defect_plc)

# Vertices in raw global coordinates (z=0, 10×10 square) — placement NOT applied
p0 = f.cartesian_point(( 0.0,  0.0, 0.0))
p1 = f.cartesian_point((10.0,  0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point(( 0.0, 10.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

ec0 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec1 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec2 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec3 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop0 = f.edge_loop([
    f.oriented_edge(ec0, True),
    f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True),
    f.oriented_edge(ec3, True),
])
face0 = f.advanced_face([f.face_outer_bound(loop0)], defect_plane)

# ── face[1]: valid reference plane at z=1 to anchor shape(1) ─────────────────
p4 = f.cartesian_point(( 0.0,  0.0, 1.0))
p5 = f.cartesian_point((10.0,  0.0, 1.0))
p6 = f.cartesian_point((10.0, 10.0, 1.0))
p7 = f.cartesian_point(( 0.0, 10.0, 1.0))

v4 = f.vertex_point(p4)
v5 = f.vertex_point(p5)
v6 = f.vertex_point(p6)
v7 = f.vertex_point(p7)

ec4 = f.edge_curve(v4, v5, f.line(p4, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec5 = f.edge_curve(v5, v6, f.line(p5, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec6 = f.edge_curve(v6, v7, f.line(p6, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec7 = f.edge_curve(v7, v4, f.line(p7, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

loop1 = f.edge_loop([
    f.oriented_edge(ec4, True),
    f.oriented_edge(ec5, True),
    f.oriented_edge(ec6, True),
    f.oriented_edge(ec7, True),
])
ref_orig  = f.cartesian_point((0.0, 0.0, 1.0))
ref_zdir  = f.direction((0.0, 0.0, 1.0))
ref_xdir  = f.direction((1.0, 0.0, 0.0))
ref_plc   = f.axis2_placement_3d(ref_orig, ref_zdir, ref_xdir)
ref_plane = f.plane(ref_plc)
face1 = f.advanced_face([f.face_outer_bound(loop1)], ref_plane)

# ── OPEN_SHELL → SBSM → product chain ────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa030.stp")
