"""Canonical cube-block generator for STEP fixtures.

Generates a closed-shell cube with consistent topology winding: every
EDGE_CURVE is used exactly once .T. and once .F. across its two
incident faces. Verified by /tmp/cube_block.py self-test.

Usage:
    from cube_block import cube
    body, shell_id = cube(base=100, origin=(0,0,0), size=10.0,
                          label_prefix="outer", outward=True)

ID layout (relative to `base`):
  base+0..7    : 8 CARTESIAN_POINT (vertices)
  base+10..17  : 8 VERTEX_POINT
  base+20..37  : per-face CARTESIAN_POINT + AXIS2_PLACEMENT_3D + PLANE (3*6 = 18)
  base+50..73  : 12 LINE + 12 EDGE_CURVE (paired)
  base+80..103 : 24 ORIENTED_EDGE (4*6 faces)
  base+110..115: 6 EDGE_LOOP
  base+120..125: 6 FACE_OUTER_BOUND
  base+130..135: 6 ADVANCED_FACE
  base+140     : CLOSED_SHELL (return this id)
  base+200..211: 12 DIRECTION (z-axis + ref-dir per face)
  base+220..231: 12 DIRECTION (one per edge)
  base+240..251: 12 VECTOR (one per edge)

So a cube needs ~260 ids of headroom from `base`. Use base = 100, 400,
700 for 3 nested cubes.

The face/edge winding convention (verified, all edges T-once-F-once):

  Edges (V_a -> V_b is the .T. direction):
    E0=V0->V1  E1=V1->V2  E2=V2->V3  E3=V3->V0   (bottom CCW from +z)
    E4=V4->V5  E5=V5->V6  E6=V6->V7  E7=V7->V4   (top CCW from +z)
    E8=V0->V4  E9=V1->V5  E10=V2->V6 E11=V3->V7  (verticals upward)

  Faces (outward=True; for outward=False, each loop reverses and senses flip):
    bot   normal -z: E3.F E2.F E1.F E0.F
    top   normal +z: E4.T E5.T E6.T E7.T
    front normal -y: E0.T E9.T E4.F E8.F
    back  normal +y: E11.T E6.F E10.F E2.T
    left  normal -x: E8.T E7.F E11.F E3.T
    right normal +x: E1.T E10.T E5.F E9.F

For void shells inside BREP_WITH_VOIDS the convention is that void shell
normals point INTO the void (i.e., toward the void's interior). Pass
outward=False for a void shell.
"""
import math


def cube(base: int, origin=(0.0, 0.0, 0.0), size=10.0,
         label_prefix="cube", outward=True):
    ox, oy, oz = origin
    s = size

    coords = [
        (ox,     oy,     oz    ),
        (ox+s,   oy,     oz    ),
        (ox+s,   oy+s,   oz    ),
        (ox,     oy+s,   oz    ),
        (ox,     oy,     oz+s  ),
        (ox+s,   oy,     oz+s  ),
        (ox+s,   oy+s,   oz+s  ),
        (ox,     oy+s,   oz+s  ),
    ]

    P  = lambda i: base + i
    VP = lambda i: base + 10 + i
    F_P  = lambda f: base + 20 + 3*f
    F_AP = lambda f: base + 20 + 3*f + 1
    F_PL = lambda f: base + 20 + 3*f + 2
    LINE = lambda e: base + 50 + 2*e
    EC   = lambda e: base + 50 + 2*e + 1
    OE   = lambda f, k: base + 80 + 4*f + k
    LOOP = lambda f: base + 110 + f
    BND  = lambda f: base + 120 + f
    FACE = lambda f: base + 130 + f
    SHELL = base + 140
    D    = lambda f, k: base + 200 + 2*f + k
    EDIR = lambda e: base + 220 + e
    VEC  = lambda e: base + 240 + e

    half = s/2.0
    face_geom = {
        0: ("bot",   (ox+half, oy+half, oz),       (0,0,-1), (1,0,0)),
        1: ("top",   (ox+half, oy+half, oz+s),     (0,0,+1), (1,0,0)),
        2: ("front", (ox+half, oy,      oz+half),  (0,-1,0), (1,0,0)),
        3: ("back",  (ox+half, oy+s,    oz+half),  (0,+1,0), (1,0,0)),
        4: ("left",  (ox,      oy+half, oz+half),  (-1,0,0), (0,0,1)),
        5: ("right", (ox+s,    oy+half, oz+half),  (+1,0,0), (0,0,1)),
    }
    if not outward:
        face_geom = {f: (n, c, (-z[0],-z[1],-z[2]), r)
                     for f,(n,c,z,r) in face_geom.items()}

    edge_specs = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7),
    ]

    face_loops_outward = [
        [(3,False),(2,False),(1,False),(0,False)],
        [(4,True ),(5,True ),(6,True ),(7,True )],
        [(0,True ),(9,True ),(4,False),(8,False)],
        [(11,True),(6,False),(10,False),(2,True )],
        [(8,True ),(7,False),(11,False),(3,True )],
        [(1,True ),(10,True),(5,False),(9,False)],
    ]
    if outward:
        face_loops = face_loops_outward
    else:
        face_loops = []
        for fl in face_loops_outward:
            face_loops.append([(e, not d) for (e,d) in reversed(fl)])

    out = []
    for i,(x,y,z) in enumerate(coords):
        out.append(f"#{P(i)}=CARTESIAN_POINT('',({x},{y},{z}));")
    for i in range(8):
        out.append(f"#{VP(i)}=VERTEX_POINT('',#{P(i)});")
    for f,(name,centre,z,r) in face_geom.items():
        out.append(f"#{F_P(f)}=CARTESIAN_POINT('{label_prefix}_{name}_c',({centre[0]},{centre[1]},{centre[2]}));")
        out.append(f"#{D(f,0)}=DIRECTION('',({z[0]},{z[1]},{z[2]}));")
        out.append(f"#{D(f,1)}=DIRECTION('',({r[0]},{r[1]},{r[2]}));")
        out.append(f"#{F_AP(f)}=AXIS2_PLACEMENT_3D('',#{F_P(f)},#{D(f,0)},#{D(f,1)});")
        out.append(f"#{F_PL(f)}=PLANE('',#{F_AP(f)});")
    for e_idx,(a,b) in enumerate(edge_specs):
        ax,ay,az = coords[a]; bx,by,bz = coords[b]
        dx,dy,dz = bx-ax, by-ay, bz-az
        mag = math.sqrt(dx*dx+dy*dy+dz*dz)
        ndx,ndy,ndz = dx/mag, dy/mag, dz/mag
        out.append(f"#{EDIR(e_idx)}=DIRECTION('',({ndx},{ndy},{ndz}));")
        out.append(f"#{VEC(e_idx)}=VECTOR('',#{EDIR(e_idx)},{mag});")
        out.append(f"#{LINE(e_idx)}=LINE('',#{P(a)},#{VEC(e_idx)});")
        out.append(f"#{EC(e_idx)}=EDGE_CURVE('',#{VP(a)},#{VP(b)},#{LINE(e_idx)},.T.);")
    for f_idx,loop in enumerate(face_loops):
        for k,(e_idx,fwd) in enumerate(loop):
            sense = '.T.' if fwd else '.F.'
            out.append(f"#{OE(f_idx,k)}=ORIENTED_EDGE('',*,*,#{EC(e_idx)},{sense});")
        refs = ",".join(f"#{OE(f_idx,k)}" for k in range(4))
        out.append(f"#{LOOP(f_idx)}=EDGE_LOOP('',({refs}));")
        out.append(f"#{BND(f_idx)}=FACE_OUTER_BOUND('',#{LOOP(f_idx)},.T.);")
        name = face_geom[f_idx][0]
        out.append(f"#{FACE(f_idx)}=ADVANCED_FACE('{label_prefix}_{name}',(#{BND(f_idx)}),#{F_PL(f_idx)},.T.);")
    face_refs = ",".join(f"#{FACE(f)}" for f in range(6))
    out.append(f"#{SHELL}=CLOSED_SHELL('{label_prefix}_shell',({face_refs}));")
    return "\n".join(out), SHELL


if __name__ == '__main__':
    body, shell_id = cube(base=100, origin=(0,0,0), size=10.0, label_prefix="outer")
    import re
    oe_pat = re.compile(r"=ORIENTED_EDGE\('',\*,\*,#(\d+),\.([TF])\.")
    uses = {}
    for m in oe_pat.finditer(body):
        uses.setdefault(int(m.group(1)), []).append(m.group(2))
    bad = [(e, s) for e, s in uses.items() if sorted(s) != ['F', 'T']]
    print(f"{len(uses)} edges, {len(bad)} inconsistent")
    print(f"shell id: #{shell_id}")
    print(f"{len(body.splitlines())} lines")
