"""Twi028 — Scrambled (out-of-cyclic-order) EDGE_LOOP edge_list on TOROIDAL_SURFACE.

Catalog claim: An EDGE_LOOP whose edge_list is out of cyclic head-to-tail order —
for example ordered (#50, #52, #51, #53) so consecutive ORIENTED_EDGEs do not
share endpoints. A face whose wire is reordered during shape-healing isn't replaced
in the resulting shape, so the fix is lost.

Mechanism IS the EDGE_LOOP whose oriented-edge entries are listed in scrambled
(non-consecutive) order on a TOROIDAL_SURFACE face: the EDGE_LOOP aggregate
references edges out of cyclic order so that oe[0].end != oe[1].start, etc.
The scrambled EDGE_LOOP IS wired into a FACE_OUTER_BOUND in an ADVANCED_FACE
in an OPEN_SHELL; never orphaned. A healing pass must reorder the loop AND
replace the face in the resulting shape.

Reproducer: ADVANCED_FACE on TOROIDAL_SURFACE with EDGE_LOOP listing four edges
as [e0, e2, e1, e3] instead of [e0, e1, e2, e3].

Byte assertions:
  - count_entity_def(b'TOROIDAL_SURFACE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - face[0].surface_type == "torus"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - brepcheck.valid == False

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi028",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a TOROIDAL_SURFACE "
        "(major_radius 2, minor_radius 0.5, axis +Z, centre at origin); "
        "FACE_OUTER_BOUND references an EDGE_LOOP whose four ORIENTED_EDGEs "
        "are listed in scrambled cyclic order [oe0, oe2, oe1, oe3] instead of "
        "[oe0, oe1, oe2, oe3]; "
        "scrambled EDGE_LOOP on TOROIDAL_SURFACE IS the mechanism; "
        "scrambled EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "healing pass must reorder the loop AND replace the face in the result shape"
    ),
)

# ── TOROIDAL_SURFACE: major 2, minor 0.5, axis +Z ────────────────────────────
MAJOR = 2.0
MINOR = 0.5

tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_plc  = f.axis2_placement_3d(tor_orig, tor_zdir, tor_xdir)
tor_surf = f._emit_raw(
    f"TOROIDAL_SURFACE('',#{tor_plc.eid},{MAJOR},{MINOR})"
)

# ── Four vertices at quarter-points of the torus (theta=0,90,180,270 @ phi=0) ─
# On the outer equator: (major+minor, 0, 0), (0, major+minor, 0), etc.
R = MAJOR + MINOR   # outer radius = 2.5
verts_coords = [
    (R, 0.0, 0.0),
    (0.0, R, 0.0),
    (-R, 0.0, 0.0),
    (0.0, -R, 0.0),
]
verts = [f.vertex_point(f.cartesian_point(c)) for c in verts_coords]

# ── Four arc edges (quarter-circles of torus equator) ─────────────────────────
# Each arc is a quarter CIRCLE of radius R centred at origin in z=0 plane.
def quarter_arc_edge(v_s, v_e, start_angle_deg):
    """Quarter circle arc from start_angle to start_angle+90 degrees."""
    plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
    plc_zdir = f.direction((0.0, 0.0, 1.0))
    plc_xdir = f.direction((1.0, 0.0, 0.0))
    plc = f.axis2_placement_3d(plc_orig, plc_zdir, plc_xdir)
    circ = f._emit_raw(f"CIRCLE('',#{plc.eid},{R})")
    return f._emit_raw(
        f"EDGE_CURVE('',#{v_s.eid},#{v_e.eid},#{circ.eid},.T.)"
    )

# Correct cyclic order: e0: v0→v1, e1: v1→v2, e2: v2→v3, e3: v3→v0
e0 = quarter_arc_edge(verts[0], verts[1], 0)
e1 = quarter_arc_edge(verts[1], verts[2], 90)
e2 = quarter_arc_edge(verts[2], verts[3], 180)
e3 = quarter_arc_edge(verts[3], verts[0], 270)

oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e3.eid},.T.)")

# ── EDGE_LOOP: scrambled order [oe0, oe2, oe1, oe3] — IS the mechanism ────────
# Correct order would be [oe0, oe1, oe2, oe3].
# Scrambled so consecutive edges don't share endpoints.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe2.eid},#{oe1.eid},#{oe3.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{tor_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
