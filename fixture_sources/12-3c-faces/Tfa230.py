"""Tfa230 — ShapeFix_Face.FixLoopWire.wire-topology

Closed-wire reorder via FixReorder vs. open-wire append;
topology-driven dispatch path.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a SPHERICAL_SURFACE. The
face has a triangular EDGE_LOOP (3 line edges) forming a closed wire. The
ShapeFix_Face::FixLoopWire() wire-topology path dispatches based on wire
closure: a closed wire triggers FixReorder to reorder edges, while an open
wire would use the append path. The fixture exercises the closed-wire branch
of the topology-driven dispatch via a valid triangular boundary on a sphere.

Byte assertions:
  - contains(b'SPHERICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Tfa230",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on SPHERICAL_SURFACE; "
        "radius=2.0; triangular EDGE_LOOP: 3 line edges forming closed triangle; "
        "ShapeFix_Face::FixLoopWire() wire-topology dispatch: "
        "closed wire → FixReorder reorders edges; "
        "open wire → append path (not taken here); "
        "fixture exercises closed-wire branch of topology dispatch; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 2.0

# ── SPHERICAL_SURFACE ─────────────────────────────────────────────────────────
sph_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
sphere = f.spherical_surface(sph_plc, R)

# ── Triangular EDGE_LOOP in XY plane ──────────────────────────────────────────
# Equilateral triangle inscribed in r=1.5 circle on the XY plane
r = 1.5
p0 = f.cartesian_point((r, 0.0, 0.0))
p1 = f.cartesian_point((r * _math.cos(2 * _math.pi / 3), r * _math.sin(2 * _math.pi / 3), 0.0))
p2 = f.cartesian_point((r * _math.cos(4 * _math.pi / 3), r * _math.sin(4 * _math.pi / 3), 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)

def make_edge(va, pa, vb, pb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    return f.edge_curve(
        va, vb,
        f.line(pa, f.vector(f.direction((dx/length, dy/length, dz/length)), length))
    )

e01 = make_edge(v0, p0, v1, p1)
e12 = make_edge(v1, p1, v2, p2)
e20 = make_edge(v2, p2, v0, p0)

face_loop = f.edge_loop([
    f.oriented_edge(e01, True),
    f.oriented_edge(e12, True),
    f.oriented_edge(e20, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], sphere)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa230.stp")
