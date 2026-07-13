"""Tfa255 — Sphere hole wire touches the pole via a degenerated edge: merges
into the natural whole-surface boundary.

Catalog claim (occt-coverage GAP `tkshh-face-natural-bound-missing`, missing
subvariant): a face on a doubly-periodic surface (sphere) with NO
FACE_OUTER_BOUND carries only an inner (hole) wire, and that hole wire
touches the pole via a degenerated edge. ShapeFix_Face::FixAddNaturalBound
(ShapeFix_Face.cxx ~937-983) must MERGE this pole-touching hole into the
synthesized natural (whole-surface) boundary rather than keep it as a
separate FACE_BOUND hole subtracted from the surface area -- distinct from
Tfa002 (empty bounds on a full sphere, no hole at all) and Tfa038 (a hole
wire that does NOT touch the pole, kept as a genuine subtracted hole).

Mechanism IS the wire/face topology: an ADVANCED_FACE on a SPHERICAL_SURFACE
(radius 5, centred at origin) has NO FACE_OUTER_BOUND. Its single FACE_BOUND
is a small lune-shaped wire that starts at the north pole (0,0,5), runs down
a meridian to a point at 70 deg latitude, across a short chord to a second
point at the same latitude, back up another meridian to the pole, and closes
via an explicit DEGENERATE edge at the pole itself (EDGE_CURVE between two
independent VERTEX_POINT entities both located at (0,0,5), with a
zero-length LINE as its curve -- the corpus's standard degenerate-edge
encoding, per Tfa125). The wire genuinely touches the pole through this
degenerate edge, not merely through vertex reuse.

Live oracle (this worktree's OCP/OCCT 7.8.1, default STEPControl_Reader):
occt_heal_on / occt_heal_off both: status=accept, shape_null=False, face=1,
shell=1, edge=4 (matches the 4 authored edges, 2 of which OCCT marks
Degenerated after translation). face[0].surface_type=="sphere",
face[0].area == 314.15926535897924 == 4*pi*5^2 -- the EXACT full-sphere
area: the lune-shaped hole wire contributes ZERO area loss, confirming
FixAddNaturalBound genuinely merged it into the natural whole-surface
boundary (a real subtracted hole, as in Tfa038, would reduce the area by the
lune's extent).

Byte assertions:
  - contains(b'SPHERICAL_SURFACE')
  - contains(b'FACE_BOUND(')
  - count_entity_def(b'VERTEX_POINT') >= 6
Tier-3 assertions:
  - load == "ok"
  - face[0].surface_type == "sphere"
  - face[0].area == 314.15926535897924
Expected: occt=shape(1)/shape(1) gmsh=... (see catalog entry) ifc=schema_n/a
"""
import math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa255",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on SPHERICAL_SURFACE (radius=5); "
        "NO FACE_OUTER_BOUND -- only one inner FACE_BOUND: a lune-shaped "
        "wire from the north pole (0,0,5) down a meridian to 70deg latitude, "
        "across a short chord, back up another meridian, closed by an "
        "explicit DEGENERATE edge at the pole (EDGE_CURVE between two "
        "independent VERTEX_POINT entities both at (0,0,5), zero-length "
        "LINE curve); ShapeFix_Face::FixAddNaturalBound merges the "
        "pole-touching hole into the natural whole-surface boundary -- "
        "live face area == 4*pi*R^2 exactly (no area subtracted); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

R = 5.0
sp_orig = f.cartesian_point((0.0, 0.0, 0.0))
sp_zdir = f.direction((0.0, 0.0, 1.0))
sp_xdir = f.direction((1.0, 0.0, 0.0))
sp_plc = f.axis2_placement_3d(sp_orig, sp_zdir, sp_xdir)
sphere = f.spherical_surface(sp_plc, R)

lat = math.radians(70.0)
z_lat = R * math.sin(lat)
r_lat = R * math.cos(lat)
theta = math.radians(40.0)

pole_pt = f.cartesian_point((0.0, 0.0, R))
v_pole1 = f.vertex_point(pole_pt)  # start of meridian-down edge
v_pole2 = f.vertex_point(pole_pt)  # end of meridian-up edge (distinct entity)

pt_A = f.cartesian_point((r_lat, 0.0, z_lat))
pt_B = f.cartesian_point((r_lat * math.cos(theta), r_lat * math.sin(theta), z_lat))
v_A = f.vertex_point(pt_A)
v_B = f.vertex_point(pt_B)


def line_edge(pa, va, pb, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    mag = math.sqrt(dx * dx + dy * dy + dz * dz)
    d = f.direction((dx / mag, dy / mag, dz / mag))
    vec = f.vector(d, mag)
    return f.edge_curve(va, vb, f.line(pa, vec))


e_down = line_edge(pole_pt, v_pole1, pt_A, v_A)      # pole -> A (meridian)
e_chord = line_edge(pt_A, v_A, pt_B, v_B)             # A -> B (chord)
e_up = line_edge(pt_B, v_B, pole_pt, v_pole2)         # B -> pole (meridian)

# Degenerate edge AT the pole: v_pole2 -> v_pole1, zero-length LINE curve
# (the corpus's standard degenerate-edge encoding, per Tfa125).
zero_dir = f.direction((1.0, 0.0, 0.0))
zero_vec = f.vector(zero_dir, 0.0)
zero_line = f.line(pole_pt, zero_vec)
e_degen = f.edge_curve(v_pole2, v_pole1, zero_line)

hole_loop = f.edge_loop([
    f.oriented_edge(e_down, True),
    f.oriented_edge(e_chord, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_degen, True),
])

# NO FACE_OUTER_BOUND -- only this pole-touching hole wire.
inner_bound = f.face_bound(hole_loop, orientation=False)
face_sphere = f.advanced_face([inner_bound], sphere)

shell = f.open_shell([face_sphere])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa255.stp")
