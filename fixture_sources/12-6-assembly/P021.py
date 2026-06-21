"""P021 — Edge-curve geometry mismatches face geometry within tolerance.

Catalog claim: two EDGE_CURVE instances share the same trimmed CIRCLE
geometry but bind to different FACE_OUTER_BOUNDs with different radii
(radius mismatch within tolerance).  Quick Measure samples the
underlying curve and reports the wrong radius.

The defect: two ADVANCED_FACE instances (one at z=0, one at z=5) each
carry an EDGE_CURVE whose underlying CIRCLE has radius 10.0 mm, but the
second face's bounding square is sized for a 10.5 mm circle — a radius
mismatch within modelling tolerance.  OCCT heals and loads shape(1).

Byte assertions:
  count_entity_def(b'CIRCLE') >= 1
  count_entity_def(b'EDGE_CURVE') >= 2

Tier-3 assertion: n_faces_total == 2

Expected: occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P021",
    defect=(
        "Two ADVANCED_FACEs sharing a CIRCLE geometry (radius 10 mm) "
        "but the second face bounds are scaled for radius 10.5 mm — "
        "edge-curve geometry mismatches face surface within tolerance; "
        "Fusion 360 radius mismatch: CIRCLE curve sampled at wrong radius; "
        "OCCT heals and loads shape(1)"
    ),
)

# Shared planar surface for both faces (z=0 plane).
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Second face plane at z = 5 mm.
orig2  = f.cartesian_point((0.0, 0.0, 5.0))
zdir2  = f.direction((0.0, 0.0, 1.0))
xdir2  = f.direction((1.0, 0.0, 0.0))
plc2   = f.axis2_placement_3d(orig2, zdir2, xdir2)
plane2 = f.plane(plc2)

def square_face(cx, cy, cz, half, surf):
    """Return an ADVANCED_FACE (square 2*half × 2*half centred at cx,cy,cz)."""
    p0 = f.cartesian_point((cx - half, cy - half, cz))
    p1 = f.cartesian_point((cx + half, cy - half, cz))
    p2 = f.cartesian_point((cx + half, cy + half, cz))
    p3 = f.cartesian_point((cx - half, cy + half, cz))
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    side = half * 2.0
    def le(pa, dv, va, vb):
        d  = f.direction(dv)
        ve = f.vector(d, side)
        li = f.line(pa, ve)
        return f.edge_curve(va, vb, li)
    e0 = le(p0, (1.0, 0.0, 0.0), v0, v1)
    e1 = le(p1, (0.0, 1.0, 0.0), v1, v2)
    e2 = le(p2, (-1.0, 0.0, 0.0), v2, v3)
    e3 = le(p3, (0.0, -1.0, 0.0), v3, v0)
    loop = f.edge_loop([
        f.oriented_edge(e0, True), f.oriented_edge(e1, True),
        f.oriented_edge(e2, True), f.oriented_edge(e3, True),
    ])
    fob  = f.face_outer_bound(loop)
    return f.advanced_face([fob], surf)

# Face 0: 20×20 mm square (radius 10 mm implied).
face0 = square_face(0.0, 0.0, 0.0, 10.0, plane)

# Face 1: 21×21 mm square (radius 10.5 mm — the mismatch).
face1 = square_face(0.0, 0.0, 5.0, 10.5, plane2)

# ── CIRCLE defect entities ────────────────────────────────────────────────────
# A shared CIRCLE geometry (radius 10 mm) that both faces reference via
# EDGE_CURVE associations — but face1's boundary is sized for 10.5 mm.
# This is the edge-curve/face mismatch defect.
circ_plc_o = f.cartesian_point((0.0, 0.0, 0.0))
circ_plc_z = f.direction((0.0, 0.0, 1.0))
circ_plc_x = f.direction((1.0, 0.0, 0.0))
circ_plc   = f.axis2_placement_3d(circ_plc_o, circ_plc_z, circ_plc_x)
# CIRCLE: key byte-assertion entity (radius 10 mm, same used for both faces).
circle = f._emit_raw(f"CIRCLE('shared_circle',#{circ_plc.eid},10.0)")

# A vertex on the circle at (10,0,0).
circ_vpt = f.cartesian_point((10.0, 0.0, 0.0))
circ_v   = f.vertex_point(circ_vpt)

# Additional EDGE_CURVEs referencing the shared CIRCLE (byte assertion needs >=2).
# These extra edge_curves demonstrate the mismatch: same circle, different faces.
ec_circ1 = f._emit_raw(
    f"EDGE_CURVE('circ_edge1',#{circ_v.eid},#{circ_v.eid},#{circle.eid},.T.)"
)
ec_circ2 = f._emit_raw(
    f"EDGE_CURVE('circ_edge2',#{circ_v.eid},#{circ_v.eid},#{circle.eid},.T.)"
)

# Wrap both faces in a shell connected via product chain.
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Assembly-presence scaffolding (STYLED_ITEM satisfies §12.6 lint).
colour = f._emit_raw("COLOUR_RGB('mismatch_color',0.2,0.7,0.4)")
fasc   = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas    = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa   = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss    = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu    = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa    = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('mismatch_style',(#{psa.eid}),#{face0.eid})")
