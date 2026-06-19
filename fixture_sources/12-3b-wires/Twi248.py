"""Twi248 — BRepLib::SameParameter null 3D curve dereference.

Catalog claim: Edge with only 2D parametric curve on surface; no 3D curve
present. GetCurve3d returns null. Dereferencing null C3d in GAC.Load() would
crash.

Demonstration: place an edge on a planar surface where the EDGE_CURVE's
edge_geometry is a SURFACE_CURVE with curve_3d=$ (null reference). OCCT
parses this into a TopoDS_Edge with null Curve3D — SameParameter must guard
the null check before dereferencing.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Twi248",
             defect="EDGE_CURVE with null 3D curve (only pcurve present)")

# Carrier surface: plane at origin.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Four 3D vertices on a 1x1 square.
pts3d = [f.cartesian_point(p) for p in [(0,0,0),(1,0,0),(1,1,0),(0,1,0)]]
verts = [f.vertex_point(p) for p in pts3d]

# 2D parametric line in surface UV space + a DEFINITIONAL_REPRESENTATION wrapper
# for PCURVE.representation. We only need this structure for one edge — the
# "defective" one whose SURFACE_CURVE has null 3D geometry.
uv0 = f.cartesian_point((0.0, 0.0))   # 2D
uv1 = f.cartesian_point((1.0, 0.0))   # 2D
udir = f.direction((1.0, 0.0))        # 2D direction
uvec = f.vector(udir, 1.0)
uline = f.line(uv0, uvec)             # 2D line in UV space

# Wrap the 2D line in a DEFINITIONAL_REPRESENTATION → PARAMETRIC_REPRESENTATION_CONTEXT.
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('uv_ctx','UV'))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('uv_def',(#{uline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(
    f"PCURVE('uv_pcurve',#{plane.eid},#{defrep.eid})"
)

# SURFACE_CURVE with curve_3d=$ (null) and one PCURVE in associated_geometry.
# This is the defect-carrier: GetCurve3d() returns null on this edge.
surf_curve = f._emit_raw(
    f"SURFACE_CURVE('null_3d_curve',$,(#{pcurve.eid}),.PCURVE_S1.)"
)

# Defective edge: edge_geometry = SURFACE_CURVE with null 3D.
edge0 = f._emit_raw(
    f"EDGE_CURVE('edge_null_3d',#{verts[0].eid},#{verts[1].eid},#{surf_curve.eid},.T.)"
)

# Remaining 3 edges of the square use ordinary 3D lines (kernel-loadable).
def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e1 = line_edge(pts3d[1], (0,1,0), 1.0, verts[1], verts[2])
e2 = line_edge(pts3d[2], (-1,0,0), 1.0, verts[2], verts[3])
e3 = line_edge(pts3d[3], (0,-1,0), 1.0, verts[3], verts[0])

loop = f.edge_loop([
    f.oriented_edge(edge0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
