# Block-segmentation model licensing

This assessment applies to document-worker revision
`8fb70af4000873561c82b2f4eb88be190efb9979`.

The three ONNX files, `clusterer/runtime.bin`, and `classifier/stats.bin`
are model artifacts, not prebuilt program executables. Runtime code maps
`runtime.bin` as learned numeric arrays and `stats.bin` as normalization
statistics. The pinned `block-seg/manifest.json` records their hashes.

Fedora Legal treats pretrained weights as content, subject to an acceptable
license and case-specific review. This does not require retraining solely
under the prohibition on prebuilt program binaries.

The packaging applies upstream's default AGPL-3.0-only grant to these assets,
based on their inclusion in the pinned repository, their introduction in commit
`0b3ee2fa77213bf1c3589c851614cd40707588d4`, and inclusion in the application
distribution under its project license. No conflicting model-specific license,
third-party attribution or exception has been identified.

`document-worker/COPYING` describes "document-worker source code" and reserves
ungranted rights, so coverage of model content is an interpretation of the
project-wide grant rather than a model-specific declaration. The package's AGPL
identifier reflects that interpretation, not a separate model-specific grant.

ONNX metadata and adjacent JSON do not identify a trainer, external model or
separate license. No independently published original model was identified;
original training authorship and training/export inputs remain unverified.
This does not by itself establish a preferred-form violation or require
retraining content. A contrary upstream notice or an applicable Fedora requirement
would require reassessing the license coverage.

Pinned SHA256 values (paths relative to `block-seg/`):

| Asset | SHA256 |
| --- | --- |
| `clusterer/model.onnx` | `5cb6f8645a0f4c8f4396d5e8b1da70d9c8d8fff8c98f324889b8c6e271575350` |
| `clusterer/repair.onnx` | `7fd29831c26f09cefa5a4f92c797e559bda5f513f6691d339d6c323bd563a789` |
| `clusterer/runtime.bin` | `a0d71f9be6c63404393457ec31875ae799b5f4ba48dc17736112446a4f82ca26` |
| `classifier/model.onnx` | `572077354eea61583982a31a3f443c5abd8d92c04e2dbfd105299c1ca1d131f7` |
| `classifier/stats.bin` | `abc86d6fa7cfb9aa18bafc2fd8cbcbf656350a7190b08fab2239efba5c673e95` |

This interpretation does not constitute Fedora Legal approval of these models.

Primary references:

- https://www.spinics.net/linux/fedora/fedora-legal/msg04705.html
- https://raw.githubusercontent.com/zotero/document-worker/8fb70af4000873561c82b2f4eb88be190efb9979/COPYING
- https://raw.githubusercontent.com/zotero/document-worker/8fb70af4000873561c82b2f4eb88be190efb9979/src/pdf/structure/model/block-seg/manifest.json
- https://github.com/zotero/document-worker/commit/0b3ee2fa77213bf1c3589c851614cd40707588d4
