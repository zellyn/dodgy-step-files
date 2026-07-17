# Tier-1 C staging entries — §12.15 Draco `.drc` compressed-codec robustness

First-ever coverage of a compressed mesh/point-cloud container in the corpus.
Each fixture carries ONE documented single-field malformation and was regenerated
from scratch with DracoPy 2.0.0 (`DracoPy.encode` of a trivial base mesh /
point cloud, then one field altered) — no bytes were copied from any upstream
issue PoC. The base mesh is a 4-vertex tetrahedron; the base point cloud is 4
deterministic points (`numpy.random.RandomState(1).rand(4,3)`). Observed results
are the ACTUAL DracoPy 2.0.0 behavior, quoted verbatim.

---

### Ip046 — Draco connectivity `num_faces` count-driven decompression bomb
- **Category**: §12.15 import-format parser robustness (sub-class: draco-codec)
- **Sources**: Pattern-mined from google/draco#1169 (Apache-2.0 — pattern only; bytes regenerated via DracoPy, not copied).
- **Description**: The Edgebreaker connectivity header carries a `num_faces` varint that the decoder historically fed to `vector::reserve()` with no bound against the remaining buffer. A tiny (~80-byte) file can therefore claim billions of faces while supplying almost no symbol payload. A robust decoder must bound the declared count against the bytes actually remaining before it allocates.
- **Reproducer recipe**: Encode the tetra base mesh; replace the single-byte `num_faces` varint at file offset 12 (value 4) with the 5-byte varint `FF FF FF FF 0F` (~4.29 billion). Body is otherwise untouched.
- **Expected kernel behavior**: Validate `num_faces` against the remaining buffer size before any reserve/allocation; reject with a clear diagnostic. Never size an allocation from an unvalidated stream count.
- **Byte assertion**: contains(b'DRACO')
- **Fixture path**: import-examples/12-15-import-formats/Ip046.drc
- **Fixture kind**: raw import-format file (parser-robustness; graded against Draco/DracoPy, not Part-21)
- **Notes**: DracoPy 2.0.0 result observed: `FileTypeException: Input mesh is not draco encoded`. The decode returns immediately — no OOM, no hang — so this DracoPy/Draco build already bounds the count (the safe behavior, verified). Synonyms: "count-driven allocation bomb", "codec-internal reserve() bomb", "unbounded num_faces". Provenance tier: bytes-only.
- **Severity**: P1
- **Model impact**: A non-validating reader calls `reserve(num_faces)` on an attacker-chosen billions-count and either aborts on `bad_alloc`, thrashes, or (with a checked-multiply bug) under-allocates and overruns.

### Ip047 — Draco truncated bitstream over-read
- **Category**: §12.15 import-format parser robustness (sub-class: draco-codec)
- **Sources**: Pattern-mined from google/draco#1103 (Apache-2.0 — pattern only; bytes regenerated via DracoPy, not copied).
- **Description**: The binary entropy-coded body is cut short after a valid header, so section/length fields still claim payload that is not present. A `DecoderBuffer::Peek`/`Decode` that does not check `remaining_size()` reads past the buffer tail. Unlike an ASCII EOF over-read there is no line/token structure to anchor recovery on.
- **Reproducer recipe**: Encode the tetra base mesh (79 bytes) and keep only the first 40 bytes (header + partial connectivity body); the trailing symbol/attribute payload is dropped.
- **Expected kernel behavior**: Every `Peek`/`Decode` must bounds-check against the remaining buffer; a truncated stream must be rejected with a diagnostic, never read past its tail.
- **Byte assertion**: contains(b'DRACO')
- **Fixture path**: import-examples/12-15-import-formats/Ip047.drc
- **Fixture kind**: raw import-format file (parser-robustness; graded against Draco/DracoPy, not Part-21)
- **Notes**: DracoPy 2.0.0 result observed: `FileTypeException: Input mesh is not draco encoded`. Truncation at every length tried (11/20/40/55/78 of 79 bytes) rejected the same way — no crash. Synonyms: "truncated codec bitstream", "buffer over-read at EOF", "short read past remaining_size". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A reader that trusts declared section lengths reads uninitialized/adjacent memory past the buffer, yielding garbage geometry or a segfault.

### Ip048 — Draco invalid encoder-method header byte
- **Category**: §12.15 import-format parser robustness (sub-class: draco-codec)
- **Sources**: Pattern-mined from google/draco#1169 header-validation surface (Apache-2.0 — pattern only; bytes regenerated via DracoPy, not copied).
- **Description**: The 11-byte Draco header's `encoder_method` byte (offset 8) selects the mesh connectivity codec; only 0 (sequential) and 1 (Edgebreaker) are defined. A value outside that set must be rejected before the decoder dispatches to a non-existent method.
- **Reproducer recipe**: Encode the tetra base mesh (method byte = 1, Edgebreaker); set file offset 8 to `0x02` (undefined method). All other bytes untouched.
- **Expected kernel behavior**: Validate the method byte against the known enumeration; reject an unknown method with a clear diagnostic rather than dispatching on it.
- **Byte assertion**: contains(b'DRACO')
- **Fixture path**: import-examples/12-15-import-formats/Ip048.drc
- **Fixture kind**: raw import-format file (parser-robustness; graded against Draco/DracoPy, not Part-21)
- **Notes**: DracoPy 2.0.0 result observed: `FileTypeException: Input mesh is not draco encoded`. Synonyms: "unknown codec method", "invalid encoder-method enum", "unsupported connectivity method". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A reader that indexes a method-dispatch table by the raw byte reads out of range / calls a null method pointer.

### Ip049 — Draco unsupported bitstream version
- **Category**: §12.15 import-format parser robustness (sub-class: draco-codec)
- **Sources**: Pattern-mined from google/draco#1169 header-validation surface (Apache-2.0 — pattern only; bytes regenerated via DracoPy, not copied).
- **Description**: The header's major/minor version bytes (offsets 5–6) gate which bitstream layout the decoder applies. A version the build does not support must be rejected up front; proceeding would parse later fields under the wrong layout assumptions.
- **Reproducer recipe**: Encode the tetra base mesh (version 2.2); set the major-version byte at offset 5 to `0xFF`. All other bytes untouched.
- **Expected kernel behavior**: Compare the declared version against the maximum supported version and reject anything higher with a clear diagnostic before decoding the body.
- **Byte assertion**: contains(b'DRACO')
- **Fixture path**: import-examples/12-15-import-formats/Ip049.drc
- **Fixture kind**: raw import-format file (parser-robustness; graded against Draco/DracoPy, not Part-21)
- **Notes**: DracoPy 2.0.0 result observed: `FileTypeException: Input mesh is not draco encoded`. Synonyms: "unsupported version header", "future bitstream version", "version-gate bypass". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A reader that ignores the version byte parses newer/older field layouts under the wrong assumptions, silently mis-decoding geometry.

### Ip050 — Draco encoder-method/body mismatch → silent-empty decode
- **Category**: §12.15 import-format parser robustness (sub-class: draco-codec)
- **Sources**: Pattern-mined from google/draco#1171 (empty/degenerate decode surface) (Apache-2.0 — pattern only; bytes regenerated via DracoPy, not copied).
- **Description**: The `encoder_method` byte is set to a VALID value (0, sequential) that does not match the actual Edgebreaker-encoded body. Unlike Ip048 (an out-of-range method), this passes the enum check, so the decoder applies the wrong-but-legal codec to the body. The danger class here is a silently-wrong result rather than an error: the decoder must cross-check the method against what the body actually contains.
- **Reproducer recipe**: Encode the tetra base mesh (method = 1, Edgebreaker); set file offset 8 to `0x00` (sequential — a valid method, wrong for this body). All other bytes untouched.
- **Expected kernel behavior**: Detect that the declared method cannot consistently decode the body and reject with a diagnostic; never emit a geometry-losing empty result without an error.
- **Byte assertion**: contains(b'DRACO')
- **Fixture path**: import-examples/12-15-import-formats/Ip050.drc
- **Fixture kind**: raw import-format file (parser-robustness; graded against Draco/DracoPy, not Part-21)
- **Notes**: DracoPy 2.0.0 result observed: decode SUCCEEDS with NO exception and returns a `DracoPointCloud` carrying no points (`points` is empty) and no faces — the entire mesh is silently discarded. This is the one fixture in the set whose malformation is NOT rejected: it decodes to an empty result with no diagnostic. Synonyms: "method/body mismatch", "silent-empty decode", "connectivity silently dropped". Provenance tier: bytes-only.
- **Severity**: P1
- **Model impact**: A downstream consumer receives an empty scene with a success return code and treats "no geometry" as valid input, masking data loss.

### Ip051 — Draco point-cloud `num_points` count-driven bomb
- **Category**: §12.15 import-format parser robustness (sub-class: draco-codec)
- **Sources**: Pattern-mined from google/draco#1105 (Apache-2.0 — pattern only; bytes regenerated via DracoPy, not copied).
- **Description**: In the point-cloud (kd-tree attribute) path, the header carries a `num_points` count (uint32, little-endian, at offset 11) that drives attribute-buffer sizing. A count that disagrees with the encoded attribute payload — here an implausibly large value — must be cross-checked against the attribute geometry before decode.
- **Reproducer recipe**: Encode the 4-point base point cloud; set the `num_points` uint32 at offset 11 to `0xFFFFFFFF`. All other bytes untouched.
- **Expected kernel behavior**: Cross-check the declared point count against the attribute payload size before allocating/decoding; reject an inconsistent count with a diagnostic.
- **Byte assertion**: contains(b'DRACO')
- **Fixture path**: import-examples/12-15-import-formats/Ip051.drc
- **Fixture kind**: raw import-format file (parser-robustness; graded against Draco/DracoPy, not Part-21)
- **Notes**: DracoPy 2.0.0 result observed: `FileTypeException: Input mesh is not draco encoded`. Decode returns immediately — no OOM/hang — so this build bounds the point count (verified). This is the point-cloud codec path, distinct from the mesh count-bomb Ip046. Synonyms: "point-count/level mismatch", "kd-tree attribute count bomb", "unbounded num_points". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A non-validating reader sizes attribute buffers from the attacker-chosen point count and over-allocates or under-allocates then overruns.

### Ip052 — Draco point-cloud attribute `num_components` overflow
- **Category**: §12.15 import-format parser robustness (sub-class: draco-codec)
- **Sources**: Pattern-mined from google/draco#1172 (Apache-2.0 — pattern only; bytes regenerated via DracoPy, not copied).
- **Description**: Each attribute descriptor declares a `num_components` byte that multiplies into the per-point stride and total attribute-buffer size. A value far larger than the true component count (3 for position) drives `count × component_size` size arithmetic that a robust decoder must range-check (and compute with a checked multiply) before allocating.
- **Reproducer recipe**: Encode the 4-point base point cloud (position attribute `num_components` = 3 at offset 19); set offset 19 to `0xFF`. All other bytes untouched.
- **Expected kernel behavior**: Reject implausible component counts; use checked multiplication for all attribute size arithmetic; never allocate or index from an unvalidated component count.
- **Byte assertion**: contains(b'DRACO')
- **Fixture path**: import-examples/12-15-import-formats/Ip052.drc
- **Fixture kind**: raw import-format file (parser-robustness; graded against Draco/DracoPy, not Part-21)
- **Notes**: DracoPy 2.0.0 result observed: `FileTypeException: Input mesh is not draco encoded`. Synonyms: "attribute component-count overflow", "num_components size-math overflow", "unchecked stride multiply". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A reader that computes `num_points × num_components × elem_size` without overflow/range checks under-allocates the attribute buffer and overruns it on decode.

---

## Candidates skipped (behavior not reproducible under DracoPy 2.0.0 — not asserted)

- **Empty-mesh decoder segfault (google/draco#1171, mining row 8)**: could not be
  synthesized via DracoPy. `DracoPy.encode(pts, zero-faces)` raises
  `EncodingFailedException: Invalid mesh` and `encode(zero-points, zero-faces)`
  raises `ValueError` at ENCODE time, so a valid-header/zero-geometry mesh cannot
  be produced through the DracoPy API. Skipped rather than assert an unverified
  crash. (The method/body-mismatch fixture Ip050 does exercise a related
  empty-result decode path, honestly.)
- **rANS entropy-decoder stack overflow (#1102, row 2)**, **Edgebreaker
  split-symbol OOB (#1162, row 4)**, **sequential-integer attribute OOB (#1202,
  row 7)**: these require crafting a specific interior entropy-stream / symbol
  bit-pattern. Every single-field mutation of the entropy body that was tried
  funnels into the same generic `FileTypeException: Input mesh is not draco
  encoded` (DracoPy 2.0.0 wraps all internal decode failures in that one
  exception), so there is no observable signal that distinguishes "reached the
  rANS/split/integer code path and it mishandled the input" from "generic reject".
  Not asserted — would overstate what was reproduced. The count-driven,
  truncation, header-validation, and silent-empty classes above are the fields
  where a distinct, verifiable DracoPy behavior WAS observed.
