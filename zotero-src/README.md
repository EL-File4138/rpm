# Source-built Zotero RPM packaging

All maintained Zotero packaging inputs are below this directory. Downloaded
upstream archives remain RPM sources, not files to commit to this repository.

## Layout

- `f44/zotero-src.spec` and `rawhide/zotero-src.spec`: target-specific entry
  points that include the shared `zotero.spec` application recipe.
- `zotero.spec`: the shared recipe, with normal `%prep`, `%build`,
  `%install` and `%check` stages. Its build is explicitly divided into Gecko,
  application modules and distribution assembly. Release staging inlines its
  fragments into the single spec submitted to RPM/Copr.
- `spec/components-*.inc`: declared source lists, metadata and private component
  preparation, compilation and checks, included by the main spec. Intermediate
  artifacts stay under `.rpm-components`; no intermediate library RPM is needed.
- `packages/<name>/`: component-local sources, patches and checks. Only external
  toolchains have separate package specs; application components build directly
  through the shared recipe.
- `sources/`: maintainer tools for producing pinned source exports and offline
  npm/Cargo source archives before an SRPM is made. They are not build drivers.
- `scripts/`: declared source preparation, dependency input validation, offline
  installation and build-check tools.
  Gecko, editor esbuild commands, npm builds and final assembly are invoked
  directly by `zotero.spec`.
- `config/`: Gecko build configuration and the desktop entry.
- `docs/`: licensing guidance.
- `tests/` and package-local checks: packaging regression tests, separate from
  the application sources. The spec's `%check` remains the RPM build checks.

## Standard RPM workflow

Stage a release from the checksum-pinned source inputs, then build it in Mock:

```sh
python3 zotero-src/sources/stage-release.py --target f44 --output "$PWD/srpms"
mock -r fedora-44-x86_64 --rebuild srpms/zotero-src-*.src.rpm
```

The Mock/Copr repositories must contain the three external toolchain RPMs:
`emscripten-core`, `wasm-bindgen-cli` and `wasi-cxx-runtime`. Other component
build tools come from Fedora. Rawhide additionally uses the coinstallable
`binaryen125` package and Fedora's `clang22`, `clang22-libs`, `llvm22` and `lld22`
compatibility packages rather than relaxing Emscripten's supported versions.
The same SRPM produces `zotero-src` and its
`zotero-src-libreoffice-integration` subpackage. The application recipe does not
fetch dependencies from the network during compilation.

Local sources with a `#/filename` suffix must be staged under that filename;
this keeps component helper and manifest basenames distinct in the SRPM. Stage
the five `components-*.inc` files before parsing the main recipe as well.

The source CI workflow submits only to `el-file4138/zotero-src`. The separate
`../zotero/zotero.spec` is the binary-repack recipe. The source package declares
a conflict with the binary package because both own the same application paths.

`sources/stage-release.py` verifies the checksum-pinned source RPM recorded in
`sources/release-inputs.json`, overlays current local packaging inputs and builds
the selected target's SRPM. Use `--target rawhide` for Rawhide. CI does not submit
toolchains automatically.
Changing package versions also requires
updating the pinned source export and lockfile archives; changing `Version` alone
does not create a new source release.

## Licensing and review

These Copr packages are not Fedora-approved packages. Model-license coverage and
its limitations are described in [MODEL-LICENSING.md](docs/MODEL-LICENSING.md).
