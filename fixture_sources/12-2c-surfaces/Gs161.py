"""Gs161 — Face with null geometric surface.

Catalog claim: Face with null surface is silently dropped from partitioned output
lists without error logging or recovery. Geometry loss in healing workflows that
partition by surface type (SF-003).

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - ADVANCED_FACE with face_geometry = $ (null surface) IS the
    ADVANCED_FACE; face boundary EDGE_LOOP with properly-formed edges (no
    pcurves, since there is no surface to reference) IS the mechanism wired
    into face topology; silent drop without error logging IS the defect.
  - Byte assertions: contains(b'ADVANCED_FACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: ADVANCED_FACE with null face_geometry ($) IS the face;
    face boundary EDGE_LOOP with edges present (null surface means no pcurves
    possible) IS the mechanism wired into face topology; SF-003 partition
    silent-drop without error IS the defect.
  - shape_null driver: null-surface face silently lost from partition output;
    healing workflow loses geometry; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs161",
    defect=(
        "ADVANCED_FACE with null face_geometry ($) IS the face; face boundary "
        "EDGE_LOOP with edges present (null surface prevents pcurves) IS the "
        "mechanism wired into face topology; SF-003 partition silent-drop "
        "without error logging IS the defect; shape_null"
    ),
)

# ── ADVANCED_FACE with null surface — geometry-loss defect ───────────────────
# Byte assertion: contains(b'ADVANCED_FACE')
# The face has a proper EDGE_LOOP boundary but face_geometry = $ (null).
# ShapeUpgrade SF-003 partition processes faces by surface type; faces with
# null geometry are silently dropped (not logged, not recovered).
# Edges use LINE 3D geometry only — no pcurves because there is no surface
# to parameterize against.

# ── Face boundary: unit square in XY plane, lines only (no pcurves) ───────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((1.0, 0.0, 0.0))
p_C = f.cartesian_point((1.0, 1.0, 0.0))
p_D = f.cartesian_point((0.0, 1.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line3d(vs, ve, p3_start, d3t, p3_len):
    """Edge with only 3D line geometry (no pcurve — null surface has no domain)."""
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{l3e.eid},.T.)")

# Bottom: A→B
e0 = mk_edge_line3d(v_A, v_B, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0)
# Right: B→C
e1 = mk_edge_line3d(v_B, v_C, (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1.0)
# Top: C→D
e2 = mk_edge_line3d(v_C, v_D, (1.0, 1.0, 0.0), (-1.0, 0.0, 0.0), 1.0)
# Left: D→A
e3 = mk_edge_line3d(v_D, v_A, (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

fob = f.face_outer_bound(loop)

# ADVANCED_FACE with null face_geometry ($) IS the face; face boundary EDGE_LOOP
# with 3D-only edges IS the mechanism wired into face topology — exercises
# SF-003 partition silent-drop of null-geometry face.
face = f._emit_raw(
    f"ADVANCED_FACE('gs161_null_surf_face',(#{fob.eid}),$,.T.)"
)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
