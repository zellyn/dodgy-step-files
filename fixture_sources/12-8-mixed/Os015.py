"""Os015 — Draft modification fails to recompute a deformed face.

Catalog claim: A draft (taper) angle applied to a CYLINDRICAL_SURFACE face
produces a deformed surface that cannot be re-fitted to the kernel's surface
representation: the deformed B-spline degenerates or the analytic surface
family doesn't extend to the requested angle.

Mechanism: ADVANCED_FACE on a CYLINDRICAL_SURFACE, same as the canonical
draft-fail case.  OCC loads (heals) but conservative kernels should reject.
Wrapped in OPEN_SHELL → SHELL_BASED_SURFACE_MODEL for shape(1) result.

Tier-3 assertions:
  face[0].surface_type == "cylinder"
  n_edges_total >= 1

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os015",
    defect=(
        "ADVANCED_FACE on CYLINDRICAL_SURFACE; 45-degree draft request results "
        "in a deformed surface that cannot be re-fitted to any analytic surface "
        "family — Draft_Modification Draft_FaceRecomputation; "
        "cylinder cannot become cone-like in analytic family; "
        "OCC loads (heals) but conservative kernels must reject; "
        "mechanism: cylindrical face with same_sense=.T. presented for draft"
    ),
)

# ── Cylindrical surface: radius=5, height=10, axis along Z ──────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, 5.0)

# ── Bottom seam circle at z=0 ─────────────────────────────────────────────────
bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
bot_circle = f.circle(bot_plc, 5.0)
p_seam_bot = f.cartesian_point((5.0, 0.0, 0.0))
v_seam_bot = f.vertex_point(p_seam_bot)
ec_bot = f._emit_raw(
    f"EDGE_CURVE('bot_seam',#{v_seam_bot.eid},#{v_seam_bot.eid},#{bot_circle.eid},.T.)"
)
oe_bot  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_bot.eid},.T.)")
loop    = f._emit_raw(f"EDGE_LOOP('cyl_loop',(#{oe_bot.eid}))")
fob     = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")

# same_sense = .T. (normal outward) — draft recompute fails
af = f._emit_raw(
    f"ADVANCED_FACE('draft_cyl',(#{fob.eid}),#{cyl_surf.eid},.T.)"
)

shell = f._emit_raw(f"OPEN_SHELL('os015_shell',(#{af.eid}))")
sbsm  = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('os015_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os015.stp")
