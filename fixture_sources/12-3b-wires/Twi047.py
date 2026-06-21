"""Twi047 — EDGE_CURVE has only a pcurve, no 3D space curve.

Catalog claim: An EDGE_CURVE on a face references a SURFACE_CURVE whose
representations list contains only a 2D pcurve and lacks the 3D space curve.
Without a 3D curve the edge cannot participate in cross-face topology checks,
length, sampling, sewing, or Boolean operations.

Mechanism: SURFACE_CURVE with one associated_geometry entry (a PCURVE) and
no 3D curve. The edge uses the SURFACE_CURVE as its curve, so the EDGE_CURVE
has no 3D space curve — only the 2D parametric trace. OCC loads the shape
but conservative kernels must reject.

Byte assertions: none defined beyond structure.
Tier-3: n_edges_total >= 4, face[0].surface_type == "plane", n_vertices_total >= 8
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi047",
    defect=(
        "EDGE_CURVE whose curve is a SURFACE_CURVE with only a pcurve "
        "in associated_geometry and no 3D space curve; "
        "edge has no Geom_Curve representation; "
        "kernel must synthesize 3D curve from pcurve+surface or reject; "
        "four such edges bound a square ADVANCED_FACE on a PLANE"
    ),
)

# Host plane: z=0, normal +z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# Corner vertices for a 10x10 square in z=0
p00 = f.cartesian_point(( 0.0,  0.0, 0.0))
p10 = f.cartesian_point((10.0,  0.0, 0.0))
p11 = f.cartesian_point((10.0, 10.0, 0.0))
p01 = f.cartesian_point(( 0.0, 10.0, 0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# Second set of corner vertices for the defect SURFACE_CURVEs
# (The SURFACE_CURVE needs vertex references but no 3D curve)
p00b = f.cartesian_point(( 0.0,  0.0, 0.0))
p10b = f.cartesian_point((10.0,  0.0, 0.0))
p11b = f.cartesian_point((10.0, 10.0, 0.0))
p01b = f.cartesian_point(( 0.0, 10.0, 0.0))

# 2D parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)

def make_pcurve_edge(v_start, v_end, uv0, uv1, name):
    """Build an EDGE_CURVE whose 3D 'curve' is a SURFACE_CURVE with pcurve only."""
    # 2D line in UV space (on the plane UV = xy since plane is z=0)
    dx = uv1[0] - uv0[0]
    dy = uv1[1] - uv0[1]
    mag = (dx**2 + dy**2) ** 0.5
    uv_start_pt = f.cartesian_point(uv0)
    uv_dir = f.direction((dx / mag, dy / mag))
    uv_vec = f.vector(uv_dir, mag)
    line2d = f.line(uv_start_pt, uv_vec)
    defrep = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',( #{line2d.eid}),#{prc.eid})"
    )
    pcurve = f._emit_raw(f"PCURVE('',#{surf.eid},#{defrep.eid})")
    # SURFACE_CURVE with no 3D curve — only the pcurve in associated_geometry
    # DEFECT: normal SURFACE_CURVE would have a 3D curve as first arg; here we
    # use the pcurve entity itself also as the "curve" (pcurve-only edge).
    # We represent this by making a degenerate SURFACE_CURVE whose curve field
    # is the pcurve entity and associated_geometry contains only that pcurve.
    surface_curve = f._emit_raw(
        f"SURFACE_CURVE('{name}',#{pcurve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
    )
    edge = f._emit_raw(
        f"EDGE_CURVE('{name}',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
    )
    return edge

# Four edges: bottom, right, top (reversed), left (reversed)
e_bot = make_pcurve_edge(v00, v10, (0.0, 0.0), (10.0,  0.0), "e_bot")
e_rgt = make_pcurve_edge(v10, v11, (10.0, 0.0), (10.0, 10.0), "e_rgt")
e_top = make_pcurve_edge(v01, v11, (0.0, 10.0), (10.0, 10.0), "e_top")
e_lft = make_pcurve_edge(v00, v01, (0.0, 0.0), (0.0,  10.0), "e_lft")

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_lft, False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
