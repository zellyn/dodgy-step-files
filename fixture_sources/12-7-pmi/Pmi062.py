"""Pmi062 — STEP-to-glTF balloon inflation on AP242 (mesh count explosion).

Catalog claim: AP242 file with PMI/hole structures yields mesh count
explosion on glTF output. Same model exported as AP203 converts correctly.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: face for a
hole feature + DIMENSIONAL_SIZE + DRAUGHTING_ANNOTATION for the hole.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pmi062",
             defect="AP242 hole + PMI annotation chain (glTF write target)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)

# CYLINDRICAL_SURFACE for the hole.
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('hole_cyl',#{plc.eid},5.0)")
v_bot = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)))
v_top = f.vertex_point(f.cartesian_point((5.0, 0.0, 10.0)))
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, 10.0)
seam_line = f.line(f.cartesian_point((5.0, 0.0, 0.0)), seam_vec)
seam_edge = f.edge_curve(v_bot, v_top, seam_line)
loop = f.edge_loop([f.oriented_edge(seam_edge, True)])
hole_face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([hole_face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# AP242 PMI hole-feature chain.
shape_aspect = f._emit_raw(f"SHAPE_ASPECT('hole_feature','',#9005,.T.)")
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{shape_aspect.eid},'diameter','10.0 mm')"
)
f._emit_raw(
    f"GEOMETRIC_TOLERANCE('position_tol','0.05 mm position',#9009,#{shape_aspect.eid})"
)
