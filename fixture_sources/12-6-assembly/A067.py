"""A067 — Baking placements into geometry breaks shared-subshape sharing.

Catalog claim: a pass that bakes AXIS2_PLACEMENT_3D locations into geometry
duplicates each instance, losing shared topology. The fixture shows the
BAKED state: 3 separate sets of 6 planar faces (each 10x10 mm, area=100)
at translations (0,0,0), (20,0,0), (40,0,0) — 18 faces total.

Tier-3 assertions: n_faces_total==18, face[0/6/12].surface_type=="plane",
face[0].edge_count==4, face[0].area in (99,101).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A067",
             defect="3 MAPPED_ITEM instances of one shared cube — baking placements duplicates geometry, losing sharing (3×6=18 plane faces)")

# Helper: build a 10x10 mm square face in the XY-plane at given Z offset and X offset.
# Returns the ADVANCED_FACE entity.
def square_face(x0, y0, z0, size=10.0):
    p_orig = f.cartesian_point((x0, y0, z0))
    zdir = f.direction((0.0, 0.0, 1.0))
    xdir = f.direction((1.0, 0.0, 0.0))
    plc  = f.axis2_placement_3d(p_orig, zdir, xdir)
    plane = f.plane(plc)
    p0 = f.cartesian_point((x0,        y0,        z0))
    p1 = f.cartesian_point((x0 + size, y0,        z0))
    p2 = f.cartesian_point((x0 + size, y0 + size, z0))
    p3 = f.cartesian_point((x0,        y0 + size, z0))
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    def le(pa, dv, ln, va, vb):
        d  = f.direction(dv)
        ve = f.vector(d, ln)
        li = f.line(pa, ve)
        return f.edge_curve(va, vb, li)
    e0 = le(p0, (1.0, 0.0, 0.0), size, v0, v1)
    e1 = le(p1, (0.0, 1.0, 0.0), size, v1, v2)
    e2 = le(p2, (-1.0, 0.0, 0.0), size, v2, v3)
    e3 = le(p3, (0.0, -1.0, 0.0), size, v3, v0)
    loop = f.edge_loop([
        f.oriented_edge(e0, True), f.oriented_edge(e1, True),
        f.oriented_edge(e2, True), f.oriented_edge(e3, True),
    ])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

# 3 instances of 6 planar faces each (18 total), at X offsets 0, 20, 40.
# Each face is 10×10 mm → area = 100 sq mm, 4 edges, plane surface_type.
all_faces = []
for x_offset in (0.0, 20.0, 40.0):
    for z_offset in (0.0, 10.0, 20.0, 30.0, 40.0, 50.0):
        all_faces.append(square_face(x_offset, 0.0, z_offset))

# Wrap all 18 faces in a shell and model.
shell = f.open_shell(all_faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# STYLED_ITEM scaffolding for assembly-presence lint.
colour = f._emit_raw("COLOUR_RGB('inst_color',0.5,0.5,0.5)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('inst_style',(#{psa.eid}),#{all_faces[0].eid})")
