# Staged catalog entries — §12.15 import-format (Ip017–Ip025)

Source mining doc: `audit/mining_trimesh_open3d_2026-07.md` (trimesh + Open3D,
both MIT, pattern-mined only). These 9 entries cover candidates #1–#8 and #10
from that doc (all OBJ/PLY/OFF/STL). Candidate #9 (PLY zero-count face
element) is a duplicate of the existing `Ip015` and was skipped. Candidate #11
(glTF no-indices/strip-mode) and #12 (concave n-gon fan-triangulation, §12.14
`Me*`) are out of scope for this batch — see the mining doc's own novelty
notes. The integrator should append these `### IpNNN` blocks into
`STEP_PROBLEM_CATALOG.md` in numeric order at the end of the existing Ip016
block (before the following `### Twi...` entry).

---

### Ip017 — OBJ face record with fewer than three vertex references
- **Category**: §12.15 import-format parser robustness (sub-class: under-specified-face-record)
- **Sources**: Pattern-mined from mikedh/trimesh, `models/notenoughindices.obj` (`tests/test_obj.py`) (MIT — pattern only, no bytes copied).
- **Description**: A Wavefront OBJ face statement supplies fewer than three vertex references (`f 1 2`), so the record cannot form a triangle or any valid polygon. Distinct from Ip001/Ip006 (index out of range/underflow) — here every index is individually valid, the record is simply too short to be geometry.
- **Reproducer recipe**: four `v` lines followed by a valid `f 1 2 3` and a second, malformed `f 1 2` carrying only two indices.
- **Expected kernel behavior**: reject or skip-with-diagnostic the under-specified face record; never emit a degenerate 2-vertex "triangle" or silently fabricate a third index.
- **Byte assertion**: contains(b'f 1 2\n')
- **Fixture path**: import-examples/12-15-import-formats/Ip017.obj
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 silently discards the malformed `f 1 2` record with no exception and no warning — `trimesh.load()` returns a single well-formed triangle (`vertices.shape==(3,3)`, `faces.shape==(1,3)`, `faces==[[0,1,2]]`), and the truncated second face simply vanishes from the loaded mesh — verified 2026-07-17. Synonyms: "OBJ face too few indices", "under-specified face record", "f-line fewer than 3 refs", "degenerate face silently dropped". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A face record that fails validation is dropped with zero diagnostic signal; a producer that emitted N faces has no way to learn that face N was silently discarded, and any downstream count/adjacency logic assuming 1:1 correspondence between file records and loaded faces silently desyncs.

### Ip018 — OBJ backslash line-continuation across a face record
- **Category**: §12.15 import-format parser robustness (sub-class: lexical-line-continuation)
- **Sources**: Pattern-mined from mikedh/trimesh, `models/wallhole.obj` (`tests/test_obj.py`, asserts `m.faces.shape==(66,3)`) (MIT — pattern only, no bytes copied).
- **Description**: A `f` statement is split across two physical lines using a trailing backslash continuation (`f 1 2 \` newline `3`). A line-oriented parser that tokenizes each physical line independently — without first joining `\`-terminated lines — either mis-tokenizes the truncated first half (a face with a trailing stray backslash token) or fails to recognize the continuation line's lone `3` as face data at all, corrupting or losing the record.
- **Reproducer recipe**: an OBJ with four `v` lines, one face record whose vertex list is split by a trailing `\` across two physical lines, and a second, ordinary single-line face.
- **Expected kernel behavior**: join `\`-terminated physical lines into one logical record before tokenizing; a naive line-by-line splitter must not drop or mangle the continued record.
- **Byte assertion**: contains(b'f 1 2 \\\n3')
- **Fixture path**: import-examples/12-15-import-formats/Ip018.obj
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 correctly joins the continuation via an explicit preprocessing step in `exchange/obj.py` (`text = text.replace("\\\n", "")`, comment: "remove backslash continuation characters and merge them into the same [line]") before tokenizing — `trimesh.load()` returns `vertices.shape==(4,3)`, `faces==[[0,1,2],[1,3,2]]`, both records intact — verified 2026-07-17. Positive/reference result: it proves the join is a deliberate, necessary preprocessing pass (not automatic), so a parser lacking it would corrupt exactly this construct. Synonyms: "OBJ line continuation", "backslash-EOL join", "split face record across lines", "lexical continuation defect". Provenance tier: bytes-only. First line-continuation/lexical-join class in the corpus.
- **Severity**: P3
- **Model impact**: A parser that skips the explicit continuation-join step either fabricates a corrupt short face from the first physical line or drops the record outright, silently losing a face the producer intended to emit as a single logical statement.

### Ip019 — OBJ face-like substring inside a group name confuses a naive `f `-scanner
- **Category**: §12.15 import-format parser robustness (sub-class: token-vs-substring-lexical-confusion)
- **Sources**: Pattern-mined from mikedh/trimesh, `models/face_in_group_name.obj` + `obj_with_no_face_in_chunk.obj` (`tests/test_obj.py`) (MIT — pattern only, no bytes copied).
- **Description**: A `g` (group) statement's name contains text that resembles face syntax (`g f 1 2 3`). A parser that detects face records by scanning each line for the substring `"f "` anywhere — rather than dispatching on the leading whitespace-delimited keyword token — misreads the group name as a phantom face statement, inventing geometry the file never declared.
- **Reproducer recipe**: three `v` lines, a `g f 1 2 3` group-name statement whose name is itself syntactically face-like, followed by the real `f 1 2 3` face record.
- **Expected kernel behavior**: dispatch on the first whitespace-delimited token of each line only; a substring match inside a group/object/material name or comment must never be read as face data.
- **Byte assertion**: contains(b'g f 1 2 3')
- **Fixture path**: import-examples/12-15-import-formats/Ip019.obj
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 correctly tokenizes by leading keyword and is immune to the trap — `trimesh.load()` returns exactly `vertices.shape==(3,3)`, `faces.shape==(1,3)`, `faces==[[0,1,2]]` (the group-name line contributes zero phantom faces) — verified 2026-07-17. Positive/reference result proving deliberate token-vs-substring discipline is required; a naive `"f " in line` scanner would corrupt this file. Synonyms: "OBJ face-like group name", "token vs substring confusion", "phantom face from group name", "naive f-scanner trap". Provenance tier: bytes-only.
- **Severity**: P3
- **Model impact**: A scanner using substring matching instead of leading-token dispatch fabricates an extra face from the group name's text, corrupting the vertex/face count and potentially indexing vertices that don't exist for the phantom record's arguments.

### Ip020 — OBJ vertex-normal index out of range silently discards the entire normal channel
- **Category**: §12.15 import-format parser robustness (sub-class: attribute-channel-underrun)
- **Sources**: Pattern-mined from mikedh/trimesh, `models/singlevn.obj` (`tests/test_obj.py`) (MIT — pattern only, no bytes copied).
- **Description**: A face record's `vn` slot references a normal index beyond the declared `vn` count (`f 1//1 2//2 3//1` with only one `vn` in the file). Rather than raising or clamping just the offending reference, a loader that bounds-checks the referenced-normal array as a whole may respond to any one invalid index by discarding per-vertex normals for the entire mesh and silently substituting a recomputed geometric (flat, per-face) normal — even for the two vertex refs (`1` and `3`) whose `vn` index was perfectly valid.
- **Reproducer recipe**: three `v` lines forming a triangle whose winding order gives a computed geometric normal of `(0,0,-1)`, one `vn 0.0 0.0 1.0` (the opposite direction, so declared-vs-computed are unambiguously distinguishable), and a face `f 1//1 2//2 3//1` where index `2` for `vn` is out of range (only one `vn` exists).
- **Expected kernel behavior**: bounds-check every `vn`/`vt` reference against the declared count of that channel individually; an out-of-range reference on one vertex should not silently discard valid per-vertex data supplied for the other vertices of the same face.
- **Byte assertion**: contains(b'f 1//1 2//2 3//1')
- **Fixture path**: import-examples/12-15-import-formats/Ip020.obj
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 raises no exception and silently drops the file's declared normal data entirely, returning `vertex_normals==[[0,0,-1],[0,0,-1],[0,0,-1]]` for every vertex — matching the recomputed geometric `face_normals` (`[0,0,-1]`), not the file's declared `vn 0.0 0.0 1.0` — verified 2026-07-17 (confirmed against an all-valid-index control file, which correctly returns the declared `[0,0,1]` normal). Synonyms: "OBJ vn index out of range", "normal channel underrun", "silent normal-channel drop", "geometric-normal fallback masks bad index". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: One malformed per-vertex-normal reference anywhere in a face silently erases shading data for the whole mesh with zero diagnostic; a producer that carefully authored smooth per-vertex normals gets flat/faceted geometric normals back instead, with no signal that anything went wrong.

### Ip021 — Non-finite (NaN) value in a vertex COLOR channel is silently clamped to zero
- **Category**: §12.15 import-format parser robustness (sub-class: non-finite-attribute-channel)
- **Sources**: Pattern-mined from mikedh/trimesh, `models/nancolor.obj` (`tests/test_obj.py`) (MIT — pattern only, no bytes copied).
- **Description**: An OBJ extended vertex line (`v x y z r g b`) carries a finite position but a `NaN` in the trailing color triple. The geometry itself is fine; the attribute is poison. Distinct from the corpus's existing `Me*` `non_finite_coordinate` class, which covers only the position channel — a non-finite value in a non-position (color) attribute is unrepresented.
- **Reproducer recipe**: three extended `v x y z r g b` lines, the third of which carries `nan` in its red-channel slot, followed by a triangular face referencing all three.
- **Expected kernel behavior**: detect and reject or clamp non-finite attribute values with a diagnostic identifying the offending vertex/channel; a silent float→int cast of NaN is undefined/implementation-specific behavior and must not be relied upon.
- **Byte assertion**: contains(b'nan 0.0 1.0')
- **Fixture path**: import-examples/12-15-import-formats/Ip021.obj
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 loads without error and silently clamps the NaN channel to 0 via an explicit step in `visual/color.py::to_rgba` (`colors[~np.isfinite(colors)] = 0.0`) before scaling to `uint8` — the third vertex's color decodes to `[0, 0, 255, 255]` (NaN silently became 0, not a diagnostic) — verified 2026-07-17. No exception, no warning; the deliberate clamp proves the class is real and must be handled explicitly, since a naive `float64.astype(uint8)` cast of NaN is undefined behavior in general. Synonyms: "OBJ non-finite vertex color", "NaN in color channel", "poisoned attribute silently clamped", "non-finite attribute vs non-finite position". Provenance tier: bytes-only.
- **Severity**: P3
- **Model impact**: A poisoned color/attribute channel is silently zeroed with no diagnostic; downstream shading, averaging, or export code sees a plausible-looking (if wrong) color value instead of an error, masking the fact the source data was corrupt.

### Ip022 — ASCII STL with multiple solid…endsolid bodies in one file
- **Category**: §12.15 import-format parser robustness (sub-class: multi-body-container)
- **Sources**: Pattern-mined from mikedh/trimesh, `models/multibody.stl` (`tests/test_stl.py`, asserts `len(s.geometry)==2`, keys `{bodyA,bodyB}`) (MIT — pattern only, no bytes copied).
- **Description**: One ASCII STL file concatenates two independent `solid NAME … endsolid NAME` blocks back to back. STL is an informal, never-formally-standardized format usually read as single-solid; a strict reader that stops parsing after the first `endsolid` silently truncates the file to one body, discarding the second solid entirely with no diagnostic. First multi-body container class for a flat mesh format in this section, and the first STL-format fixture in the corpus.
- **Reproducer recipe**: a single `.stl` file containing two complete, well-formed `solid NAME … endsolid NAME` blocks, each with one triangle, back to back with no separator beyond the second `solid` keyword.
- **Expected kernel behavior**: treat the file as a scene of N named solids and load all of them; never silently stop after the first `endsolid` and discard the remainder of the file.
- **Byte assertion**: contains(b'endsolid bodyA')
- **Fixture path**: import-examples/12-15-import-formats/Ip022.stl
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 correctly treats the file as a multi-body container — `trimesh.load()` returns a `Scene` with `geometry.keys()==['bodyA','bodyB']`, each a well-formed one-triangle mesh — verified 2026-07-17. Positive/reference result: trimesh's ASCII STL loader (`exchange/stl.py::load_stl_ascii`) explicitly scans for repeated `solid`/`endsolid` chunk pairs rather than stopping at the first `endsolid`, proving the multi-body case is a deliberate design decision a naive single-pass reader would get wrong. Synonyms: "STL multi-solid file", "multiple solid blocks in one STL", "STL container truncated to first body", "ASCII STL scene of N solids". Provenance tier: bytes-only. First STL-format fixture in the corpus.
- **Severity**: P2
- **Model impact**: A reader that stops at the first `endsolid` silently drops every subsequent body in the file with no error signal; a multi-part assembly exported as one STL loses all but its first part.

### Ip023 — Binary STL whose 80-byte header begins with the ASCII text "solid"
- **Category**: §12.15 import-format parser robustness (sub-class: ascii-vs-binary-detection-trap)
- **Sources**: Pattern-mined from mikedh/trimesh, `models/two_objects_mixed_case_names.stl` (`tests/test_stl.py`) + STL binary/ASCII-detection folklore (MIT — pattern only, no bytes copied).
- **Description**: A binary STL's free-text 80-byte header happens to begin with the literal word "solid" (many CAD/CAM exporters write a human-readable string like `solid NAME exported by TOOL` into the otherwise-arbitrary binary header). A content-sniffer that decides ASCII-vs-binary by checking whether the file's first bytes spell "solid" mis-routes this file to the ASCII parser, which then fails to make sense of the binary triangle payload (or aborts outright). Second STL-format fixture in the corpus; the first exercising the binary variant and its detection heuristic.
- **Reproducer recipe**: a well-formed binary STL (80-byte header + `uint32` triangle count + 50-byte triangle records) whose header text is deliberately set to `"solid exported by dodgy-step-files binary STL generator tool v1"` — a legal binary STL that happens to start with the ASCII bytes "solid".
- **Expected kernel behavior**: detect binary-vs-ASCII by structure (does `84 + 50*count` equal the file length?) rather than by sniffing a leading "solid" token; a leading "solid" byte sequence must never be sufficient evidence that a file is the ASCII variant.
- **Byte assertion**: contains(b'solid exported by dodgy-step-files')
- **Fixture path**: import-examples/12-15-import-formats/Ip023.stl
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 loads the file correctly as a single-triangle mesh (`vertices.shape==(3,3)`, `faces.shape==(1,3)`) despite the "solid"-prefixed header — verified 2026-07-17. Positive/reference result: `exchange/stl.py::load_stl` tries `load_stl_binary` first and only falls back to `load_stl_ascii` on a `HeaderError` (structural header-vs-filesize mismatch), so it is immune to the naive "leading solid token" heuristic that trips up simpler sniffers. Synonyms: "binary STL solid header trap", "ASCII vs binary STL misdetection", "leading solid token false positive", "STL format-sniffing by structure not prefix". Provenance tier: bytes-only. First binary-STL fixture in the corpus.
- **Severity**: P2
- **Model impact**: A loader that keys format detection off a leading "solid" token mis-routes this legal binary file to the ASCII parser, producing a parse abort or garbage geometry from what is actually valid triangle data.

### Ip024 — OFF inline comment on the vertex/face count line desynchronizes every subsequent row
- **Category**: §12.15 import-format parser robustness (sub-class: lexical-tokenization-desync)
- **Sources**: Pattern-mined from mikedh/trimesh, `models/comments.off` + `whitespace.off` (`tests/test_off.py`) (MIT — pattern only, no bytes copied).
- **Description**: An OFF file's `V F E` count line carries a trailing `# comment` on the same physical line (`3 1 0 # off count line comment`). trimesh's own comment-stripping helper (`util.comment_strip`) has a self-inflicted bug on this exact construct: its chunk-rejoin logic double-emits the line preceding an inline comment, duplicating the count line in the stripped output. Every subsequent row extraction (`splits[1:vertex_count+1]` for vertices, `splits[vertex_count+1:...]` for faces) is computed from positional offsets keyed to `vertex_count`/`face_count`, so the phantom duplicate line shifts every following row by one position — a vertex row absorbs the duplicate header text as fake coordinates, and the face-row slice lands on a real vertex-coordinate row instead.
- **Reproducer recipe**: an OFF file with `OFF` on its own line, then a count line `3 1 0 # off count line comment` (an inline `#` comment trailing the counts on the same physical line), followed by 3 vertex rows and 1 face row.
- **Expected kernel behavior**: strip inline comments without altering line count/order; validate the declared V/F/E against rows actually present rather than trusting positional offsets blindly, and never let a comment's presence silently shift which physical line answers to which logical row.
- **Byte assertion**: contains(b'3 1 0 # off count line comment')
- **Fixture path**: import-examples/12-15-import-formats/Ip024.off
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 raises `ValueError: invalid literal for int() with base 10: '0.0'` from `exchange/off.py:52` (`faces = [line[1 : int(line[0]) + 1] for line in faces]`) — traced to `util.comment_strip`'s chunk-rejoin duplicating the "3 1 0" count line in its output, which shifts the vertex/face row slices by one position until a real vertex-coordinate row ("0.0 1.0 0.0") is misread as a face row and `int("0.0")` fails — verified 2026-07-17 (confirmed by inspecting `comment_strip`'s intermediate output directly). Distinct from Ip003 (header count > body rows, an honest mismatch) — here the declared counts are correct and the desync is purely a side effect of comment placement. Synonyms: "OFF comment on count line", "inline comment desyncs row offsets", "comment_strip duplication bug", "OFF lexical tokenization ambiguity". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A syntactically legal comment placement corrupts positional row bookkeeping throughout the rest of the file, producing either a hard parse failure (as observed) or, on files with different row counts, silently misassigned vertex/face data with no correspondence to the source geometry.

### Ip025 — OBJ face record forward-referencing vertices declared later in the file
- **Category**: §12.15 import-format parser robustness (sub-class: index-resolution-ordering)
- **Sources**: Pattern-mined from isl-org/Open3D issue #5582, "Vertex Index disorder when reading from obj file" (MIT — pattern only, no bytes copied).
- **Description**: A `f` statement appears in the file before the `v` records it references, relying on the loader resolving indices against the complete, final vertex table rather than an in-progress running list. A single-pass, streaming-style loader that resolves each face's indices against only the vertices seen so far cannot resolve a forward reference at all (index 1 doesn't exist yet when the `f` line is read) — the independent Open3D loader was observed to bind faces to the wrong vertices under this kind of ordering/disorder.
- **Reproducer recipe**: a face record `f 1 2 3` placed as the first content line, followed by the three `v` lines it references.
- **Expected kernel behavior**: resolve every OBJ index against the final, complete 1-based global vertex table after a full pass over the file; forward references are legal OBJ and must resolve correctly regardless of physical line order.
- **Byte assertion**: contains(b'f 1 2 3')
- **Fixture path**: import-examples/12-15-import-formats/Ip025.obj
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Cross-oracle: trimesh 4.12.2 resolves the forward reference correctly — `trimesh.load()` returns `vertices.shape==(3,3)`, `faces==[[0,1,2]]`, exactly the intended triangle — verified 2026-07-17. Positive/reference result: trimesh's OBJ loader extracts all `v`/`vn`/`vt`/`f` records via a two-pass, regex-based approach (`_parse_vertices` runs over the whole text before face resolution) rather than a single streaming pass, so forward references are immune to the disorder Open3D's issue tracker reports; a naive streaming single-pass reader would fail or mis-bind on this exact construct. Synonyms: "OBJ forward vertex reference", "face before vertex declaration", "vertex index disorder", "two-pass vs streaming OBJ resolution". Provenance tier: bytes-only.
- **Severity**: P3
- **Model impact**: A streaming-style loader that resolves indices against a running (not final) vertex list either fails outright on a forward reference or, worse, silently binds the face to whatever vertex currently occupies that index slot, producing wrong geometry with no error.
