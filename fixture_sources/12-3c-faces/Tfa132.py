"""Tfa132 — CheckTwisted spline-tangent-discontinuity.

Catalog claim: Face on B-spline surface with C0 tangent discontinuity. The
surface normal calculation in ShapeAnalysis_CheckSmallFace::CheckTwisted
returns inconsistent values across the discontinuity, causing the twisted-face
detector to misclassify topology.

Demonstration: degree-3×3 B-spline surface with interior U-knot of multiplicity
3 (= degree, producing a C0 break at u=0.5). Left half is flat at z=0; right
half tilts up. Surface normal flips orientation across the seam.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa132",
             defect="CheckTwisted on C0-discontinuous B-spline surface")

# 7 U poles × 4 V poles, degree 3 × 3.
# Left tile (U=0..0.5): flat at z=0.
# Right tile (U=0.5..1): tilted +Z.
# Interior U knot at 0.5 with multiplicity 3 = degree → C0 break.
u_rows = 7   # = degree_u + 1 + (left=3 + right=3 - 1 shared at the break)
v_rows = 4   # = degree_v + 1

control_pts = []
for vi in range(v_rows):
    y = vi * (10.0 / (v_rows - 1))
    row = []
    for ui in range(u_rows):
        if ui < 3:
            # left tile poles
            x = ui * (5.0 / 2.0)        # 0, 2.5, 5
            z = 0.0
        elif ui == 3:
            # shared corner pole at the discontinuity seam
            x = 5.0
            z = 0.0
        else:
            # right tile poles (lift in z, slight x stretch to make tangent visibly differ)
            x = 5.0 + (ui - 3) * (5.0 / 3.0)   # 6.67, 8.33, 10
            z = (ui - 3) * 1.0                  # 1, 2, 3 — slope discontinuity
        row.append(f.cartesian_point((x, y, z)))
    control_pts.append(row)

# Knot vectors.
# U: clamped degree-3 with interior multiplicity 3 → (4, 3, 4) on knot values (0, 0.5, 1).
u_knots = [0.0, 0.5, 1.0]
u_mults = [4, 3, 4]
# V: standard clamped Bezier-like (4,4) on (0, 1).
v_knots = [0.0, 1.0]
v_mults = [4, 4]

# Emit B_SPLINE_SURFACE_WITH_KNOTS via _emit_raw (nested control-points grid).
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in control_pts)
um = ",".join(str(m) for m in u_mults)
vm = ",".join(str(m) for m in v_mults)
uk = ",".join(f"{k}" for k in u_knots)
vk = ",".join(f"{k}" for k in v_knots)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('discontinuous_spline',3,3,({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,({um}),({vm}),({uk}),({vk}),.UNSPECIFIED.)"
)

# Face bounded by 10x10 rectangle in the parametric domain (mapped via the surface).
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))
v = [f.vertex_point(p) for p in (p0, p1, p2, p3)]

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

edges = [
    line_edge(p0, (1.0, 0.0, 0.0), 10.0, v[0], v[1]),
    line_edge(p1, (0.0, 1.0, 0.0), 10.0, v[1], v[2]),
    line_edge(p2, (-1.0, 0.0, 0.0), 10.0, v[2], v[3]),
    line_edge(p3, (0.0, -1.0, 0.0), 10.0, v[3], v[0]),
]
loop = f.edge_loop([f.oriented_edge(e, True) for e in edges])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
