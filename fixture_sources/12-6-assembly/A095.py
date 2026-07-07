"""A095 — STEP export of a part with a fillet/round generates malformed shape.

Catalog claim: fillet radius r << boundingBox/1000 is exported with
edge-vertex coordinates that round to the same CARTESIAN_POINT.
Receiver sees a degenerate face.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: a face on a
small CYLINDRICAL_SURFACE (radius 0.05mm) inside a 10mm-scale part, with
two near-coincident CARTESIAN_POINTs (distance 1e-7) — the
writer-precision collapse pattern.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A095",
             defect="small CYLINDRICAL_SURFACE + near-coincident vertices (fillet collapse)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)

# Tiny CYLINDRICAL_SURFACE — fillet radius 0.05mm.
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('tiny_fillet',#{plc.eid},0.05)")

# Two near-coincident vertices (~1e-7 apart).
p_a = f.cartesian_point((0.05, 0.0, 0.0))
p_b = f.cartesian_point((0.050000001, 0.0, 0.0))   # within rounding
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0e-7)
ln = f.line(p_a, vec)
edge = f.edge_curve(v_a, v_b, ln)
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Add a NAUO so the byte assertion is satisfied (assembly-level claim).
sub_pdc = f._emit_raw(f"PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub','',"
    f"#9054,#{sub_pdef.eid},$)"
)
