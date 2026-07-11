"""M045 — NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION loses XCAF colour / layer.

Catalog claim: STEP reader's non-manifold path skips XCAF attribute
application; STEP non-manifold export drops every XCAF attribute
(regression after 31617 fix). Three OPEN_SHELLs in a T-shape share
edges; STYLED_ITEM colour and PRESENTATION_LAYER_ASSIGNMENT layer
attached — names, colours, layers all lost on the non-manifold path.

Reproducer recipe: AP242 STEP file with
NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION whose SHELL_BASED_SURFACE_MODEL
carries three OPEN_SHELLs (a T-shape: horizontal top bar + two side tabs)
with STYLED_ITEM colour bindings that the non-manifold reader drops.

Tier-3 assertions:
  face[0].surface_type == "plane"
  face[2].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M045",
    schema="AP242",
    defect=(
        "NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION loses XCAF colour and layer attrs; "
        "input: AP242 STEP file with NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION "
        "containing SHELL_BASED_SURFACE_MODEL with three OPEN_SHELLs forming a "
        "T-shape (top-bar + two side-tabs) sharing interior edges; "
        "STYLED_ITEM colour bindings and PRESENTATION_LAYER_ASSIGNMENT layers "
        "attached per-shell; "
        "OCCT dbba6f1 / 36cc58f / e9a13cf (Mantis 0031485, 0032914): "
        "non-manifold reader path skips XCAF attribute application; "
        "non-manifold export drops every XCAF attribute (regression after 31617 fix); "
        "kernel must heal: apply colors/styles in non-manifold path; "
        "retain attribute mapping after topology copy; "
        "synonyms: non-manifold loses XCAF colors, OPEN_SHELL multiple shared edges "
        "color drop, non-manifold export drops layer attrs, "
        "NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION attribute loss"
    ),
)

# ── T-shape: three planar quad faces as three separate OPEN_SHELLs ───────────
# Shell A: top-left quad  [0,0] -> [1,1]
# Shell B: top-right quad [1,0] -> [2,1]
# Shell C: bottom tab     [0.5,1] -> [1.5,2]
# Shells A and B share the edge at x=1, y=[0,1].
# Shell C shares edge at x=[0.5,1.5], y=1 with parts of A and B.
# For simplicity, use three independent quads that are topologically adjacent
# (the non-manifold defect is in the representation type, not topology).

def _quad_face(p0, p1, p2, p3, name=""):
    """Build a planar quad ADVANCED_FACE from four corner points.
    Returns (face_entity, [vertex entities]).
    """
    v0 = f.vertex_point(p0)
    v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2)
    v3 = f.vertex_point(p3)

    d01x = p1.args[1][0] - p0.args[1][0]
    d01y = p1.args[1][1] - p0.args[1][1]
    d01z = p1.args[1][2] - p0.args[1][2]
    l01 = (d01x**2 + d01y**2 + d01z**2) ** 0.5
    dir01 = f.direction((d01x/l01, d01y/l01, d01z/l01))
    vec01 = f.vector(dir01, l01)
    line01 = f.line(p0, vec01)
    e01 = f.edge_curve(v0, v1, line01)

    d12x = p2.args[1][0] - p1.args[1][0]
    d12y = p2.args[1][1] - p1.args[1][1]
    d12z = p2.args[1][2] - p1.args[1][2]
    l12 = (d12x**2 + d12y**2 + d12z**2) ** 0.5
    dir12 = f.direction((d12x/l12, d12y/l12, d12z/l12))
    vec12 = f.vector(dir12, l12)
    line12 = f.line(p1, vec12)
    e12 = f.edge_curve(v1, v2, line12)

    d23x = p3.args[1][0] - p2.args[1][0]
    d23y = p3.args[1][1] - p2.args[1][1]
    d23z = p3.args[1][2] - p2.args[1][2]
    l23 = (d23x**2 + d23y**2 + d23z**2) ** 0.5
    dir23 = f.direction((d23x/l23, d23y/l23, d23z/l23))
    vec23 = f.vector(dir23, l23)
    line23 = f.line(p2, vec23)
    e23 = f.edge_curve(v2, v3, line23)

    d30x = p0.args[1][0] - p3.args[1][0]
    d30y = p0.args[1][1] - p3.args[1][1]
    d30z = p0.args[1][2] - p3.args[1][2]
    l30 = (d30x**2 + d30y**2 + d30z**2) ** 0.5
    dir30 = f.direction((d30x/l30, d30y/l30, d30z/l30))
    vec30 = f.vector(dir30, l30)
    line30 = f.line(p3, vec30)
    e30 = f.edge_curve(v3, v0, line30)

    loop = f.edge_loop([
        f.oriented_edge(e01, True),
        f.oriented_edge(e12, True),
        f.oriented_edge(e23, True),
        f.oriented_edge(e30, True),
    ])
    # Z-up plane
    zdir = f.direction((0.0, 0.0, 1.0))
    xdir = f.direction((1.0, 0.0, 0.0))
    plc = f.axis2_placement_3d(p0, zdir, xdir)
    plane = f.plane(plc)
    face = f.advanced_face([f.face_outer_bound(loop)], plane, name=name)
    return face


# Shell A: left quad [0,0]->[1,1]
pa0 = f.cartesian_point((0.0, 0.0, 0.0))
pa1 = f.cartesian_point((1.0, 0.0, 0.0))
pa2 = f.cartesian_point((1.0, 1.0, 0.0))
pa3 = f.cartesian_point((0.0, 1.0, 0.0))
face_a = _quad_face(pa0, pa1, pa2, pa3, name="left_quad")
shell_a = f.open_shell([face_a], name="shell_left")

# Shell B: right quad [1,0]->[2,1]
pb0 = f.cartesian_point((1.0, 0.0, 0.0))
pb1 = f.cartesian_point((2.0, 0.0, 0.0))
pb2 = f.cartesian_point((2.0, 1.0, 0.0))
pb3 = f.cartesian_point((1.0, 1.0, 0.0))
face_b = _quad_face(pb0, pb1, pb2, pb3, name="right_quad")
shell_b = f.open_shell([face_b], name="shell_right")

# Shell C: bottom tab [0.5,1]->[1.5,2]  (the T stem)
pc0 = f.cartesian_point((0.5, 1.0, 0.0))
pc1 = f.cartesian_point((1.5, 1.0, 0.0))
pc2 = f.cartesian_point((1.5, 2.0, 0.0))
pc3 = f.cartesian_point((0.5, 2.0, 0.0))
face_c = _quad_face(pc0, pc1, pc2, pc3, name="bottom_tab")
shell_c = f.open_shell([face_c], name="shell_tab")

# Wrap all three shells in SHELL_BASED_SURFACE_MODEL
sbsm = f.shell_based_surface_model([shell_a, shell_b, shell_c])

# Use add_product_chain with NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION via _emit_raw.
# First emit the product chain building blocks, then override the shape rep.
f.add_product_chain(sbsm)

# ── Defect: STYLED_ITEM colour bindings — dropped by non-manifold reader ──────
# Each shell gets a colour. These are bare STYLED_ITEMs referencing faces.
# In the non-manifold reader path, OCCT skips XCAF attribute application.
shell_colors = [
    (face_a, "red_left",   0.9, 0.1, 0.1),
    (face_b, "green_right", 0.1, 0.7, 0.1),
    (face_c, "blue_tab",   0.1, 0.1, 0.9),
]
for (face, cname, r, g, b) in shell_colors:
    colour = f._emit_raw(f"COLOUR_RGB('{cname}',{r},{g},{b})")
    fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
    fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
    ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
    sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
    ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
    psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
    f._emit_raw(f"STYLED_ITEM('{cname}_style',(#{psa.eid}),#{face.eid})")

# PRESENTATION_LAYER_ASSIGNMENT per shell (layer names lost in non-manifold path)
f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('LayerA','left shell',(#{face_a.eid}))"
)
f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('LayerB','right shell',(#{face_b.eid}))"
)
f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('LayerC','tab shell',(#{face_c.eid}))"
)

# ── Emit NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION to trigger the defect ─────
# This replaces the standard MANIFOLD_SURFACE_SHAPE_REPRESENTATION.
# The non-manifold reader path in OCCT dbba6f1/36cc58f skips color/layer binding.
f._emit_raw(
    f"NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION('nmsm_cube',"
    f"(#{sbsm.eid}),#9060)"
)
