"""Os001 — Offset of a surface whose normals flip sign.

Catalog claim: A face on a CYLINDRICAL_SURFACE is supplied with
same_sense = .F., so the face normal contradicts the surface's natural
normal direction. An offset request then has no consistent direction to push.

Mechanism: ADVANCED_FACE on CYLINDRICAL_SURFACE with same_sense=.F.
injected via _emit_raw.  The shell is wrapped in a SHELL_BASED_SURFACE_MODEL
so OCC loads a shape (shape(1)/shape(1)).

Tier-3 assertions:
  face[0].surface_type == "cylinder"
  n_edges_total >= 1

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os001",
    defect=(
        "ADVANCED_FACE on CYLINDRICAL_SURFACE with same_sense=.F.; "
        "face normal contradicts surface natural normal direction; "
        "offset has no consistent push direction — BRepOffset_MakeOffset "
        "BadNormalsOnGeometry; OCC loads (heals) but conservative kernels reject; "
        "mechanism: same_sense=.F. injected via _emit_raw on ADVANCED_FACE"
    ),
)

# ── Cylindrical surface: radius=5, axis along Z ───────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, 5.0)

# ── Full circle edge (seam at (5,0,0)) ────────────────────────────────────────
circle_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
circle = f.circle(circle_plc, 5.0)

p_seam = f.cartesian_point((5.0, 0.0, 0.0))
v_seam = f.vertex_point(p_seam)

ec = f._emit_raw(
    f"EDGE_CURVE('seam',#{v_seam.eid},#{v_seam.eid},#{circle.eid},.T.)"
)
oe   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('cyl_loop',(#{oe.eid}))")
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")

# DEFECT: same_sense = .F. — normal flipped vs. surface natural direction
af = f._emit_raw(
    f"ADVANCED_FACE('flipped_cyl',(#{fob.eid}),#{cyl_surf.eid},.F.)"
)

# Wrap in OPEN_SHELL → SHELL_BASED_SURFACE_MODEL so OCC yields shape(1)
shell = f._emit_raw(f"OPEN_SHELL('os001_shell',(#{af.eid}))")
sbsm  = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('os001_sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os001.stp")
