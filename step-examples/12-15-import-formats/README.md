# 12-15-import-formats

## Fixtures

| ID | Title |
|---|---|
| [Ip001](Ip001.stp) | OBJ face index exceeds vertex count (out-of-range reference) |
| [Ip002](Ip002.stp) | PLY header vertex count exceeds body rows (declared > actual) |
| [Ip003](Ip003.stp) | OFF header V/F/E counts exceed actual body rows (declared > actual) |
| [Ip004](Ip004.stp) | glTF accessor over-runs its bufferView (count×stride > byteLength) |
| [Ip005](Ip005.stp) | COLLADA `<p>` primitive index references vertex beyond `<source>` |
| [Ip006](Ip006.stp) | OBJ negative relative face index below −(vertex count) |
| [Ip007](Ip007.stp) | glTF accessor `componentType` is an invalid enum value |
| [Ip008](Ip008.stp) | glTF node `children[]` references a node index out of range |
| [Ip009](Ip009.stp) | PLY vertex row supplies more scalar fields than declared properties |
| [Ip010](Ip010.stp) | OFF face names a vertex index ≥ declared vertex count |
| [Ip011](Ip011.stp) | glTF node `matrix` has fewer than 16 backing floats |
| [Ip012](Ip012.stp) | glTF accessor `componentType` disagrees with the buffer's actual data layout |
| [Ip013](Ip013.stp) | PLY face list references a vertex index ≥ declared vertex count (unvalidated on load) |
| [Ip014](Ip014.stp) | COLLADA document with no `library_geometries` (empty scene) |
| [Ip015](Ip015.stp) | PLY zero-count face element alongside a populated vertex element (silent type change) |
| [Ip016](Ip016.stp) | OFF face names a negative vertex index (unvalidated, wraps to the last vertex) |
