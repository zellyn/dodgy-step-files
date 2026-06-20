"""Tfa211 — ShapeFix_Face.FixMissingSeam.null-surface-guard

ADVANCED_FACE with null surface handle ($). Triggers FixMissingSeam null
guard path that rejects faces missing surface references before proceeding
to seam synthesis.

Mechanism: CLOSED_SHELL with TWO ADVANCED_FACEs. The defective face has a
valid quad EDGE_LOOP but face_geometry = $ (NULL surface handle). A companion
good face (1×1 square on a PLANE) ensures OCC loads shape(1). The defective
face IS on the live traversal path through the CLOSED_SHELL. The OCCT
ShapeFix_Face.FixMissingSeam code path at line 1724 checks for a null surface
handle before attempting seam synthesis and aborts gracefully, preventing a
crash on the malformed entity.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa211",
    defect=(
        "CLOSED_SHELL: ADVANCED_FACE with face_geometry = $ (null surface handle); "
        "FixMissingSeam line 1724: null-surface-guard rejects seam synthesis; "
        "defective face: quad EDGE_LOOP (1×1 square), surface slot = $ NULL; "
        "companion good face (1×1 square on PLANE at x=2) ensures shape(1) load; "
        "without null guard: FixMissingSeam dereferences null handle → crash; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── DEFECTIVE face: valid quad EDGE_LOOP, but surface = $ (NULL) ─────────────
dp_ll = f.cartesian_point((0.0, 0.0, 0.0))
dp_lr = f.cartesian_point((1.0, 0.0, 0.0))
dp_ur = f.cartesian_point((1.0, 1.0, 0.0))
dp_ul = f.cartesian_point((0.0, 1.0, 0.0))

dv_ll = f.vertex_point(dp_ll)
dv_lr = f.vertex_point(dp_lr)
dv_ur = f.vertex_point(dp_ur)
dv_ul = f.vertex_point(dp_ul)

de_bot = f.edge_curve(dv_ll, dv_lr, f.line(dp_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
de_rgt = f.edge_curve(dv_lr, dv_ur, f.line(dp_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
de_top = f.edge_curve(dv_ur, dv_ul, f.line(dp_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
de_lft = f.edge_curve(dv_ul, dv_ll, f.line(dp_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

defect_loop = f.edge_loop([
    f.oriented_edge(de_bot, True),
    f.oriented_edge(de_rgt, True),
    f.oriented_edge(de_top, True),
    f.oriented_edge(de_lft, True),
])
defect_fob = f.face_outer_bound(defect_loop)
# ADVANCED_FACE with null surface handle — triggers FixMissingSeam null guard at line 1724
defect_face = f._emit_raw(
    f"ADVANCED_FACE('null_surf',(#{defect_fob.eid}),$,.T.)"
)

# ── GOOD face: 1×1 square on PLANE at x=2 (ensures shape(1) output) ─────────
gp_ll = f.cartesian_point((2.0, 0.0, 0.0))
gp_lr = f.cartesian_point((3.0, 0.0, 0.0))
gp_ur = f.cartesian_point((3.0, 1.0, 0.0))
gp_ul = f.cartesian_point((2.0, 1.0, 0.0))

gv_ll = f.vertex_point(gp_ll)
gv_lr = f.vertex_point(gp_lr)
gv_ur = f.vertex_point(gp_ur)
gv_ul = f.vertex_point(gp_ul)

ge_bot = f.edge_curve(gv_ll, gv_lr, f.line(gp_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
ge_rgt = f.edge_curve(gv_lr, gv_ur, f.line(gp_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
ge_top = f.edge_curve(gv_ur, gv_ul, f.line(gp_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ge_lft = f.edge_curve(gv_ul, gv_ll, f.line(gp_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

good_loop = f.edge_loop([
    f.oriented_edge(ge_bot, True),
    f.oriented_edge(ge_rgt, True),
    f.oriented_edge(ge_top, True),
    f.oriented_edge(ge_lft, True),
])
good_fob = f.face_outer_bound(good_loop)
good_plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((2.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))
good_face = f.advanced_face([good_fob], good_plane)

# ── Assemble: both faces in CLOSED_SHELL ─────────────────────────────────────
closed_sh = f.closed_shell([defect_face, good_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa211.stp")
