%global gecko_version 140.17.0
%global source_commit 35429ad62024032e0888b6cc1b6b51f96f8a8f1d
%global __provides_exclude_from ^%{_libdir}/zotero/.*$
%global __requires_exclude ^(libclearkey|liblgpllibs|libmozavcodec|libmozavutil|libmozgtk|libmozsandbox|libmozsqlite3|libmozwayland|libxul|libgkcodecs)\.so.*$

Name:           zotero-src
Version:        10.0.7
Release:        2%{?dist}
Summary:        Zotero desktop application

License:        AGPL-3.0-only AND GPL-3.0-only AND MPL-2.0 AND LGPL-2.1-only AND MIT AND Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND ISC AND BSL-1.0 AND Zlib AND W3C AND Unicode-3.0 AND Unicode-DFS-2016 AND CC-BY-4.0 AND CC-BY-SA-3.0 AND CC0-1.0 AND OFL-1.1 AND Knuth-CTAN AND LicenseRef-Rsfs AND LicenseRef-Liberation AND (Apache-2.0 WITH LLVM-exception)
URL:            https://www.zotero.org
# Exported at source_commit with sources/prepare-zotero-source.py;
# source-commits.txt records the recursively pinned submodules.
Source0:        zotero-%{version}-source.tar.xz
Source1:        https://archive.mozilla.org/pub/firefox/releases/%{gecko_version}esr/source/firefox-%{gecko_version}esr.source.tar.xz
# Prepared from the exported lockfiles with sources/prepare-npm-sources.py.
Source2:        zotero-%{version}-npm-sources.tar.xz
Source3:        scripts/prepare-source.py
Source4:        scripts/install-npm-offline.py
Source5:        scripts/prepare-gecko.py
Source6:        config/gecko.mozconfig
Source7:        scripts/prepare-application.py
Source8:        config/zotero.desktop
Source9:        scripts/check-citeproc-preview.cjs
Source10:       scripts/editor-source-inputs.py
Source11:       https://github.com/ProseMirror/prosemirror-tables/archive/a99f70855f2b3e2433bc77451fedd884305fda5b/prosemirror-tables-a99f70855f2b3e2433bc77451fedd884305fda5b.tar.gz
# The registry gitHead is unreachable; all four implementation files match its
# published source-map sourcesContent byte-for-byte at this upstream commit.
Source12:       https://github.com/atlassian/prosemirror-utils/archive/d34dac47b291da9a8a74aeca25ef57b0450fd133/prosemirror-utils-d34dac47b291da9a8a74aeca25ef57b0450fd133.tar.gz
Source13:       scripts/check-editor-dependencies.cjs
Source14:       https://github.com/liberationfonts/liberation-1.7-fonts/archive/dbeb786b4ede1eaec2ec5cb8d3b75d21641e2a35/liberation-1.7-fonts-dbeb786b4ede1eaec2ec5cb8d3b75d21641e2a35.tar.gz
# Retain original Liberation 1.07.4 TTFs. FontsPolicy source generation is a
# conditional SHOULD, not the program-binary MUST. Current FontForge changes
# glyph count/order used by PDF.js scaling and annotation embedding; avoid a
# renamed font fork. Source14 supplies corresponding editable sources/notices.
# Policy: packaging/guidelines commit 721795c3754e16b157d14de00d89789708498f87,
# FontsPolicy.adoc (Building), what-can-be-packaged.adoc (content binaries).
# Original TypeScript inputs omitted from the npm distributions in Source2.
# Keep the tested readable generated modules; supplying generator inputs does
# not require another compiler pipeline (what-can-be-packaged.adoc).
Source15:       https://github.com/projectfluent/fluent.js/archive/88582193c29a689241a4f7b2ca7086c802840264/fluent.js-88582193c29a689241a4f7b2ca7086c802840264.tar.gz
Source16:       https://github.com/projectfluent/fluent.js/archive/f07305556f92bf19acfccc9621adf99dd8f434d8/fluent.js-f07305556f92bf19acfccc9621adf99dd8f434d8.tar.gz
Source17:       https://github.com/darkreader/darkreader/archive/52e1169ce25da2a08fce86a05fc6d70b923f9dfd/darkreader-52e1169ce25da2a08fce86a05fc6d70b923f9dfd.tar.gz
Source18:       https://github.com/AbeJellinek/sentencex-ts/archive/b70514b1bafc81215f6defc37265df9a7b0c8520/sentencex-ts-b70514b1bafc81215f6defc37265df9a7b0c8520.tar.gz
Source19:       https://github.com/101arrowz/fflate/archive/d3243651cb142e3e04f3e4bc037b9e985878f444/fflate-d3243651cb142e3e04f3e4bc037b9e985878f444.tar.gz
Source20:       https://github.com/ka-weihe/fastest-levenshtein/archive/03d621ba324d0f665b3b7f557429ca622560d9a3/fastest-levenshtein-03d621ba324d0f665b3b7f557429ca622560d9a3.tar.gz
# Registry gitHead identifies this snapshot. Its manifest still says 1.8.0;
# both tracked JS implementations match npm 1.8.1 except CRLF line endings.
Source21:       https://github.com/qwertie/btree-typescript/archive/e54ffd3c042fd066be55262751691b271413794c/btree-typescript-e54ffd3c042fd066be55262751691b271413794c.tar.gz
Source22:       https://github.com/tinymce/tinymce/archive/54c877e17a350900c795ba939f7b2bf24411cb90/tinymce-54c877e17a350900c795ba939f7b2bf24411cb90.tar.gz
# Zotero intentionally retains the 4.6.7 paste plugin (upstream c7d05ad2f9ec).
# Readable release files replace minified desktop code, not compiler inputs.
Source23:       https://registry.npmjs.org/tinymce/-/tinymce-4.9.4.tgz
Source24:       https://registry.npmjs.org/tinymce/-/tinymce-4.6.7.tgz
Source25:       https://github.com/tinymce/tinymce/archive/6b1c354e63ef0c01314b44a7c7115c433a1b8fb3/tinymce-6b1c354e63ef0c01314b44a7c7115c433a1b8fb3.tar.gz
Source26:       scripts/prepare-tinymce.py
# Upstream blocks automated downloads. Verbatim retained template; provenance and
# checksum are recorded in sources/OFL-PROVENANCE.md.
Source27:       sources/OFL.txt
Source28:       scripts/collect-mathjax-notices.py
Source29:       https://raw.githubusercontent.com/JedWatson/react-select/1d9f5c8335eff27ec8be71de588528f552f422f9/LICENSE#/react-select-LICENSE
Source30:       https://raw.githubusercontent.com/nodejs/node/v7.0.0/LICENSE#/node-v7-LICENSE
Source31:       scripts/deduplicate-licenses.py
Source32:       spec/components-sources.inc
Source33:       spec/components-metadata.inc
Source34:       spec/components-prep.inc
Source35:       spec/components-build.inc
Source36:       spec/components-check.inc
# GPL version 3 is selected for GPL-2.0-or-later/GPL-3.0-or-later translators.
Source37:       https://raw.githubusercontent.com/spdx/license-list-data/v3.27.0/text/GPL-3.0-only.txt
# Mozilla Remote Settings OneCRL snapshot (timestamp 1793208925525).
# https://firefox.settings.services.mozilla.com/v1/buckets/security-state/collections/onecrl/changeset?_expected=0
Source38:       sources/onecrl-changeset.json
%include %{SOURCE32}
%include %{SOURCE33}

ExclusiveArch: x86_64

# Build tools. RPM stages consume only the declared sources and buildroot.
BuildRequires:  python3
BuildRequires:  python3-fonttools
BuildRequires:  python3.11-devel
BuildRequires:  gcc-c++
%if 0%{?fedora} > 44
BuildRequires:  clang22
BuildRequires:  clang22-libs
BuildRequires:  llvm22
BuildRequires:  lld22
%else
BuildRequires:  clang >= 22
BuildRequires:  clang < 23
BuildRequires:  clang-libs
BuildRequires:  llvm
BuildRequires:  lld
%endif
BuildRequires:  rust
BuildRequires:  cargo
BuildRequires:  cbindgen
BuildRequires:  autoconf213
BuildRequires:  make
BuildRequires:  nasm
BuildRequires:  m4
BuildRequires:  perl
BuildRequires:  pkgconf-pkg-config
BuildRequires:  nodejs >= 22
BuildRequires:  npm >= 10
BuildRequires:  golang-github-evanw-esbuild
BuildRequires:  zip
BuildRequires:  unzip
BuildRequires:  xz
BuildRequires:  rsync
BuildRequires:  openssl
BuildRequires:  findutils
BuildRequires:  desktop-file-utils
BuildRequires:  wasi-cxx-runtime = 22.1.8
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(dbus-glib-1)
BuildRequires:  pkgconfig(xt)
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(ice)
BuildRequires:  pkgconfig(sm)
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(nss)
BuildRequires:  pkgconfig(nspr)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(vpx)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libevent)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libpipewire-0.3)

# Native shared-library requirements are generated from ELF dependencies.
Conflicts:      zotero
Provides:       zotero = %{version}-%{release}
Requires:       hicolor-icon-theme
Requires:       %{name}-libreoffice-integration = %{version}-%{release}

Provides:       bundled(gecko) = %{gecko_version}
Provides:       bundled(source-map-mappings) = 0.5.0
Provides:       bundled(crate(rand)) = 0.4.6
Provides:       bundled(crate(vlq)) = 0.5.1
Provides:       bundled(onnxruntime) = 1.27.0
# Static link inputs of the copied ONNX Runtime WASM, not its build tools.
Provides:       bundled(onnx) = 1.21.0
Provides:       bundled(protobuf) = 3.21.12
Provides:       bundled(re2) = 20240702
Provides:       bundled(abseil-cpp) = 20250814.0
# These implementations are copied into Zotero's WASM payloads; the build
# prerequisite RPMs' Provides do not describe the resulting application RPM.
Provides:       bundled(expat) = 2.7.1
Provides:       bundled(rnv) = 1.7.11
Provides:       bundled(csl-schema) = 0^e3ce254a72c4470a5ed3b9d23b428017d25674e9
Provides:       bundled(openjpeg) = 0^6c4a29b00211eb0430fa0e5e890f1ce5c80f409f
Provides:       bundled(pdfium) = 0^bb1f9f71e7b15afdd5937adf8cfe5807522b882f
Provides:       bundled(quickjs) = 0^3d5e064e9dd67c70f7962836505a7fa067bf0a4e
Provides:       bundled(crate(qcms)) = 0.3.0
Provides:       bundled(monacopilot) = 1.1.15
Provides:       bundled(monacopilot-core) = 1.1.15
Provides:       bundled(react) = 18.3.1
Provides:       bundled(react-dom) = 18.3.1
Provides:       bundled(scheduler) = 0.23.2
Provides:       bundled(ace) = 1.4.12
Provides:       bundled(jshint) = 2.13.6
Provides:       bundled(lodash) = 4.17.23
Provides:       bundled(events) = 3.3.0
Provides:       bundled(react-autosuggest) = 10.1.0
Provides:       bundled(react-themeable) = 1.1.0
Provides:       bundled(section-iterator) = 2.0.0
Provides:       bundled(shallow-equal) = 1.2.1
Provides:       bundled(prop-types) = 15.8.1
Provides:       bundled(@benrbray/prosemirror-math) = 1.0.0
Provides:       bundled(object-assign) = 3.0.0
Provides:       bundled(object-assign) = 4.1.1
Provides:       bundled(pako) = 2.1.0
Provides:       bundled(katex) = 0.16.22
Provides:       bundled(mathjax) = 3.2.2
Provides:       bundled(liberation-fonts) = 1.07.4
Provides:       bundled(mhchemparser) = 4.2.1
Provides:       bundled(classnames) = 2.2.6
Provides:       bundled(jspath) = 0.4.0
Provides:       bundled(react-virtualized) = 9.22.4
Provides:       bundled(clsx) = 1.1.1
Provides:       bundled(dom-helpers) = 5.2.0
Provides:       bundled(react-lifecycles-compat) = 3.0.4
Provides:       bundled(react-intl) = 3.12.1
Provides:       bundled(intl-messageformat) = 7.8.4
Provides:       bundled(intl-messageformat-parser) = 3.6.4
Provides:       bundled(intl-format-cache) = 4.3.1
Provides:       bundled(@formatjs/intl-utils) = 2.3.0
Provides:       bundled(hoist-non-react-statics) = 3.3.2
Provides:       bundled(react-is) = 18.3.1
Provides:       bundled(monaco-editor) = 0.47.0
Provides:       bundled(monaco-editor-core) = 0.47.0
Provides:       bundled(typescript) = 5.0.2
Provides:       bundled(vscode-css-languageservice) = 5.4.1
Provides:       bundled(vscode-html-languageservice) = 4.2.4
Provides:       bundled(vscode-json-languageservice) = 4.2.1
Provides:       bundled(vscode-languageserver-textdocument) = 1.0.4
Provides:       bundled(vscode-languageserver-types) = 3.16.0
Provides:       bundled(vscode-uri) = 3.0.3
Provides:       bundled(jsonc-parser) = 3.0.0
Provides:       bundled(vscode-loader) = 1.0.0
Provides:       bundled(vscode-codicons) = 0.0.35
Provides:       bundled(prosemirror-commands) = 1.7.1
Provides:       bundled(prosemirror-dropcursor) = 1.8.2
Provides:       bundled(prosemirror-gapcursor) = 1.3.2
Provides:       bundled(prosemirror-history) = 1.4.1
Provides:       bundled(prosemirror-inputrules) = 1.5.0
Provides:       bundled(prosemirror-keymap) = 1.2.3
Provides:       bundled(prosemirror-markdown) = 1.13.2
Provides:       bundled(prosemirror-model) = 1.25.2
Provides:       bundled(prosemirror-schema-basic) = 1.2.4
Provides:       bundled(prosemirror-schema-list) = 1.5.1
Provides:       bundled(prosemirror-state) = 1.4.3
Provides:       bundled(prosemirror-tables) = 1.7.1
Provides:       bundled(prosemirror-transform) = 1.10.4
Provides:       bundled(prosemirror-utils) = 1.2.2
Provides:       bundled(prosemirror-view) = 1.40.1
Provides:       bundled(tinymce) = 4.9.4
Provides:       bundled(tinymce) = 4.6.7
Provides:       bundled(react-select) = 3.1.0
Provides:       bundled(@fluent/bundle) = 0.19.1
Provides:       bundled(@fluent/react) = 0.15.2
Provides:       bundled(darkreader) = 4.9.83
Provides:       bundled(fflate) = 0.8.2
Provides:       bundled(fastest-levenshtein) = 1.0.16
Provides:       bundled(sentencex-ts) = 0.1.13~ts
Provides:       bundled(sorted-btree) = 1.8.1
# Additional runtime module sections in the reader, editor and worker bundles.
# Build-only webpack loaders and entire development lockfiles are not included.
Provides:       bundled(@babel/runtime) = 7.23.8
Provides:       bundled(@babel/runtime) = 7.24.8
Provides:       bundled(@fluent/sequence) = 0.8.0
Provides:       bundled(cached-iterable) = 0.3.0
Provides:       bundled(classnames) = 2.3.2
Provides:       bundled(classnames) = 2.5.1
Provides:       bundled(eld) = 2.0.2
Provides:       bundled(event-emitter) = 0.3.5
Provides:       bundled(jszip) = 3.10.1
Provides:       bundled(luaparse) = 0.3.1
Provides:       bundled(pako) = 1.0.11
Provides:       bundled(path-webpack) = 0.0.3
Provides:       bundled(postcss-selector-parser) = 6.0.13
Provides:       bundled(queue) = 6.0.2
Provides:       bundled(inherits) = 2.0.4
Provides:       bundled(d) = 1.0.1
Provides:       bundled(es5-ext) = 0.10.62
Provides:       bundled(util-deprecate) = 1.0.2
Provides:       bundled(cssesc) = 3.0.0
Provides:       bundled(entities) = 4.5.0
Provides:       bundled(linkify-it) = 5.0.0
Provides:       bundled(markdown-it) = 14.1.0
Provides:       bundled(mdurl) = 2.0.0
Provides:       bundled(orderedmap) = 2.1.1
Provides:       bundled(punycode.js) = 2.3.1
Provides:       bundled(rope-sequence) = 1.3.4
Provides:       bundled(uc.micro) = 2.1.0
Provides:       bundled(w3c-keyname) = 2.2.8
Provides:       bundled(dom-serializer) = 2.0.0
Provides:       bundled(domelementtype) = 2.3.0
Provides:       bundled(domhandler) = 5.0.3
Provides:       bundled(domutils) = 3.2.2
Provides:       bundled(htmlparser2) = 9.1.0
Provides:       bundled(@babel/runtime) = 7.12.1
Provides:       bundled(@emotion/cache) = 10.0.29
Provides:       bundled(@emotion/core) = 10.0.35
Provides:       bundled(@emotion/css) = 10.0.27
Provides:       bundled(@emotion/hash) = 0.8.0
Provides:       bundled(@emotion/memoize) = 0.7.4
Provides:       bundled(@emotion/serialize) = 0.11.16
Provides:       bundled(@emotion/sheet) = 0.9.4
Provides:       bundled(@emotion/stylis) = 0.8.5
Provides:       bundled(@emotion/unitless) = 0.7.5
Provides:       bundled(@emotion/utils) = 0.11.3
Provides:       bundled(@emotion/weak-memoize) = 0.2.5
Provides:       bundled(memoize-one) = 5.1.1
Provides:       bundled(react-input-autosize) = 2.2.2
Provides:       bundled(react-is) = 16.13.1
Provides:       bundled(process) = 0.11.10
Provides:       bundled(punycode) = 1.3.2
Provides:       bundled(querystring) = 0.2.0
Provides:       bundled(url) = 0.11.0

%description
Zotero is a free, easy-to-use tool to help you collect, organize, cite, and
share research.

%package libreoffice-integration
Summary:        LibreOffice citation integration for Zotero
License:        AGPL-3.0-only
BuildArch:      noarch
Provides:       zotero-libreoffice-integration = %{version}-%{release}
Obsoletes:      zotero-libreoffice-integration < 10.0.3-2
Requires:       java-headless >= 17
Requires:       libreoffice-ure >= 26.2
Requires:       mvn(net.java.dev.jna:jna)
Requires:       mvn(com.fasterxml.jackson.core:jackson-core)
Requires:       mvn(com.fasterxml.jackson.core:jackson-databind)
Requires:       mvn(com.fasterxml.jackson.core:jackson-annotations)

%description libreoffice-integration
LibreOffice citation integration built from Zotero's pinned integration sources,
using Fedora's Java libraries rather than copies embedded in the extension.

%prep
%setup -q -n zotero-%{version} -b 1 -a 2
cp %{SOURCE38} .rpm-onecrl.json
mkdir -p .rpm-original-sources/{fluent-bundle,fluent-react,darkreader,sentencex-ts,fflate,fastest-levenshtein,sorted-btree,tinymce}
tar -xf %{SOURCE15} --strip-components=1 -C .rpm-original-sources/fluent-bundle
tar -xf %{SOURCE16} --strip-components=1 -C .rpm-original-sources/fluent-react
tar -xf %{SOURCE17} --strip-components=1 -C .rpm-original-sources/darkreader
tar -xf %{SOURCE18} --strip-components=1 -C .rpm-original-sources/sentencex-ts
tar -xf %{SOURCE19} --strip-components=1 -C .rpm-original-sources/fflate
tar -xf %{SOURCE20} --strip-components=1 -C .rpm-original-sources/fastest-levenshtein
tar -xf %{SOURCE21} --strip-components=1 -C .rpm-original-sources/sorted-btree
tar -xf %{SOURCE22} --strip-components=1 -C .rpm-original-sources/tinymce
mkdir -p .rpm-original-sources/tinymce-paste
tar -xf %{SOURCE25} --strip-components=1 -C .rpm-original-sources/tinymce-paste
%{__python3} %{SOURCE26} . %{SOURCE23} %{SOURCE24}
# RPM's unique debugsource collector is rooted at this build subdirectory.
# Keep Gecko beneath it so debugedit can collect its sources and generated files.
# A hidden directory is excluded from upstream's application-source rsync.
mkdir .rpm-gecko
mv ../firefox-%{gecko_version} .rpm-gecko/
# Gecko supports system libffi directly; do not retain its unused private copy.
rm -rf .rpm-gecko/firefox-%{gecko_version}/js/src/ctypes/libffi
grep -Fqx '.;%{source_commit}' source-commits.txt
mkdir -p .rpm-editor-sources/{prosemirror-tables,prosemirror-utils}
tar -xf %{SOURCE11} --strip-components=1 -C .rpm-editor-sources/prosemirror-tables
tar -xf %{SOURCE12} --strip-components=1 -C .rpm-editor-sources/prosemirror-utils
mkdir -p .rpm-font-sources/liberation
tar -xf %{SOURCE14} --strip-components=1 -C .rpm-font-sources/liberation
for style in Bold BoldItalic Italic Regular; do
    cmp reader/pdfjs/pdf.js/external/standard_fonts/LiberationSans-$style.ttf \
        document-worker/pdf.js/external/standard_fonts/LiberationSans-$style.ttf
done
for project in reader/pdfjs/pdf.js document-worker/pdf.js; do
    cp .rpm-font-sources/liberation/License.txt "$project/external/standard_fonts/LICENSE_LIBERATION"
done
%{__python3} %{SOURCE5} .rpm-gecko/firefox-%{gecko_version}
component_sources="$PWD/.rpm-components/sources"
component_tools="$PWD/.rpm-components/tools"
mkdir -p "$component_sources" "$component_tools"
%include %{SOURCE34}

%build
%if 0%{?fedora} > 44
export PATH="%{_libdir}/llvm22/bin:%{_libdir}/binaryen125/bin:$PATH"
export LIBCLANG_PATH="%{_libdir}/llvm22/lib64"
%endif
export CARGO_NET_OFFLINE=true CARGO_BUILD_JOBS=%{_smp_build_ncpus} RAYON_NUM_THREADS=%{_smp_build_ncpus}
export MAKEFLAGS=-j%{_smp_build_ncpus} CMAKE_BUILD_PARALLEL_LEVEL=%{_smp_build_ncpus}
export EMCC_CORES=%{_smp_build_ncpus} BINARYEN_CORES=%{_smp_build_ncpus} GOMAXPROCS=%{_smp_build_ncpus}
export TMPDIR="$PWD/rpm-tmp"
mkdir -p "$TMPDIR"
# Private dependency stages share this SRPM, not installed intermediate RPMs.
component_sources="$PWD/.rpm-components/sources"
component_tools="$PWD/.rpm-components/tools"
component_data="$PWD/.rpm-components/data"
component_licenses="$PWD/.rpm-components/licenses"
mkdir -p "$component_data" "$component_licenses"
%include %{SOURCE35}
%{__python3} %{SOURCE3} . --data "$component_data"
cp "$component_data/source-map-mappings-wasm/mappings.wasm" \
    .rpm-gecko/firefox-%{gecko_version}/devtools/client/shared/vendor/source-map/lib/mappings.wasm
for project in . reader reader/pdfjs/pdf.js document-worker document-worker/pdf.js note-editor resource/SingleFile; do
    %{__python3} %{SOURCE4} "$project" "$PWD/npm-sources"
done
# These readable modules are byte-identical to their pinned upstream source,
# not npm-generated bundles (classnames 30bd487, JSPath e845ea9).
sha256sum -c <<'EOF'
aebabda87b88551787e5ea7126013a60e6c0f08d732bb95cc79654059af03171  node_modules/classnames/index.js
6133088a5b0c7f755d20d08cc3f5bbeade16a1d14852fe5e3b4ecdef18f7013c  node_modules/jspath/lib/jspath.js
EOF
# Level 1: compile and package Gecko using its upstream build system.
(
    application="$PWD"
    cd .rpm-gecko/firefox-%{gecko_version}
    cp %{SOURCE6} rpm.mozconfig
    cat >> rpm.mozconfig <<EOF
mk_add_options MOZ_OBJDIR=$PWD/obj-rpm
mk_add_options MOZ_MAKE_FLAGS=-j%{_smp_build_ncpus}
EOF
    export MOZCONFIG="$PWD/rpm.mozconfig" MOZBUILD_STATE_PATH="$PWD/mach-state"
    mkdir -p "$MOZBUILD_STATE_PATH"
    export MACH_BUILD_PYTHON_NATIVE_PACKAGE_SOURCE=none PIP_NO_INDEX=1
    export RPM_BUILD_JOBS=%{_smp_build_ncpus} MOZ_MAKE_FLAGS=-j%{_smp_build_ncpus}
    export MOZ_PKG_BASENAME=firefox-source
    export LDFLAGS="$LDFLAGS -Wl,--threads=%{_smp_build_ncpus}"
    # Gecko supplies Rust flags; cc-rs must not re-enable LTO or exceptions.
    unset MOZ_AUTOMATION RUSTFLAGS CARGO_ENCODED_RUSTFLAGS
    export CFLAGS="$CFLAGS -fno-lto" CXXFLAGS="$CXXFLAGS -fno-lto -fno-exceptions"
    # Multiprocessing socket names need a short alias for disk-backed TMPDIR.
    alias_dir=$(mktemp -d /tmp/zgecko-XXXXXX)
    trap 'rm -f "$alias_dir/tmp"; rmdir "$alias_dir"' EXIT
    ln -s "$TMPDIR" "$alias_dir/tmp"
    export TMPDIR="$alias_dir/tmp"
    python3.11 mach build
    python3.11 mach package
    set -- obj-rpm/dist/firefox-*.tar.xz
    test "$#" -eq 1 && test -f "$1"
    mkdir -p "$application/app/xulrunner"
    cp "$1" "$application/app/xulrunner/firefox-%{gecko_version}esr-x86_64.tar.xz"
)

# Level 2: replace generated dependencies, then compile application modules.
%{__python3} %{SOURCE7} . --data "$component_data"
export npm_config_offline=true npm_config_ignore_scripts=true
export npm_config_audit=false npm_config_fund=false
export UV_THREADPOOL_SIZE=1
export NODE_OPTIONS="--max-old-space-size=1400 --require=$PWD/rpm-node-jobs.cjs"
%{__python3} %{SOURCE10} . > rpm-editor-build-plan.tsv
while IFS="$(printf '\t')" read -r source entry format output; do
    mkdir -p "$(dirname "$output")"
    (
        cd "$source"
        %{_bindir}/esbuild "src/$entry" --bundle --packages=external \
            --platform=browser --target=firefox140 \
            --tsconfig-raw='{"compilerOptions":{"useDefineForClassFields":false}}' \
            --format="$format" --outfile="$output" --metafile="$output.inputs.json"
    )
done < rpm-editor-build-plan.tsv
%{__python3} %{SOURCE10} . --collect
(
    cd note-editor/node_modules/@benrbray/prosemirror-math
    %{_bindir}/esbuild lib/main.ts --bundle --format=esm --platform=browser \
        --packages=external --outfile=dist/prosemirror-math.js
    cp public/prosemirror-math.css dist/prosemirror-math.css
)
(cd resource/SingleFile && npm run build)
(cd reader && npm run build:zotero)
(
    cd document-worker
    node node_modules/webpack/bin/webpack.js --mode production
    bash scripts/build-assets
    node scripts/build-metadata.js
    %{_bindir}/esbuild structured-document-text/src/read.js --bundle \
        --platform=browser --target=firefox140 --format=cjs \
        --outfile=build/structured-document-text.js
)
(cd note-editor && npm run build:zotero)
# Upstream copy merges directories; discard only checked generated outputs.
%{__python3} %{SOURCE7} . --clear-outputs
npm run build
%{__python3} %{SOURCE7} . --check
rm -rf build/resource/document-worker/{cmaps,standard_fonts}

# Level 3: assemble the distribution from the source-built modules and Gecko.
mkdir -p rpm-prepared
%{__python3} app/scripts/prepare_build --source-dir "$PWD/build" \
    --output-dir "$PWD/rpm-prepared" --channel release
bash app/build.sh -d "$PWD/rpm-prepared" -p l -a x64 -c release -s
mkdir -p app/staging/Zotero_linux-x86_64/distribution
cp app/policies.json app/staging/Zotero_linux-x86_64/distribution/policies.json
test ! -e app/staging/Zotero_linux-x86_64/updater

%install
# Preserve both debugsource header paths as one stored file. cpio dereferences
# Gecko's exported symlink but does not deduplicate it against the source path.
cmp .rpm-gecko/firefox-%{gecko_version}/third_party/zstd/lib/zstd.h \
    .rpm-gecko/firefox-%{gecko_version}/obj-rpm/dist/include/zstd/zstd.h
ln -f .rpm-gecko/firefox-%{gecko_version}/third_party/zstd/lib/zstd.h \
    .rpm-gecko/firefox-%{gecko_version}/obj-rpm/dist/include/zstd/zstd.h
# These prerequisites are copied into the application, so their license files
# must also travel with Zotero rather than only with the buildroot packages.
mkdir -p rpm-licenses/gecko
for project in reader note-editor document-worker; do
    mkdir -p "rpm-licenses/$project"
    cp "$project/COPYING" "rpm-licenses/$project/"
done
mkdir -p rpm-licenses/pdf-liberation-fonts
cp .rpm-font-sources/liberation/{COPYING,License.txt,AUTHORS} rpm-licenses/pdf-liberation-fonts/
mkdir -p rpm-licenses/pdf-foxit-fonts
cmp reader/pdfjs/pdf.js/external/standard_fonts/LICENSE_FOXIT \
    document-worker/pdf.js/external/standard_fonts/LICENSE_FOXIT
cp reader/pdfjs/pdf.js/external/standard_fonts/LICENSE_FOXIT rpm-licenses/pdf-foxit-fonts/
%{__python3} %{SOURCE28} reader/node_modules/mathjax-full/es5/output/chtml/fonts/woff-v2 \
    %{SOURCE27} rpm-licenses/mathjax-tex-fonts
cp -a .rpm-gecko/firefox-%{gecko_version}/LICENSE rpm-licenses/gecko/
cp -a .rpm-gecko/firefox-%{gecko_version}/toolkit/content/license.html rpm-licenses/gecko/
cp -a %{_licensedir}/wasi-cxx-runtime rpm-licenses/
cp -a .rpm-components/licenses/. rpm-licenses/
for package in classnames jspath; do
    mkdir -p rpm-licenses/$package
    cp -a node_modules/$package/LICENSE rpm-licenses/$package/
done
mkdir -p rpm-licenses/prosemirror-math
cp -a note-editor/node_modules/@benrbray/prosemirror-math/LICENSE \
    rpm-licenses/prosemirror-math/
mkdir -p rpm-licenses/tinymce
mkdir -p rpm-licenses/csl-locales
cp chrome/content/zotero/locale/csl/README.md rpm-licenses/csl-locales/
mkdir -p rpm-licenses/pdf-icc
cmp reader/pdfjs/pdf.js/external/iccs/LICENSE document-worker/pdf.js/external/iccs/LICENSE
cp reader/pdfjs/pdf.js/external/iccs/LICENSE rpm-licenses/pdf-icc/
# Keep the original CSS grants/copyrights that preprocessing may remove.
# Select LGPL version 2.1 from their MPL/GPL/LGPL alternatives; its full text
# is also retained in tinymce/license.txt below.
for platform in unix win mac; do
    directory="rpm-licenses/legacy-preferences/$platform"
    mkdir -p "$directory"
    if test "$platform" = mac; then
        cp app/assets/mac/chrome/skin/preferences/preferences.css "$directory/"
    else
        cp "app/assets/$platform/skin/preferences/preferences.css" "$directory/"
    fi
done
# Translator grants and individual attribution remain in the shipped scripts.
mkdir -p rpm-licenses/translators
cp %{SOURCE37} rpm-licenses/translators/GPL-3.0.txt
mkdir -p rpm-licenses/tabulator-rdf
cp chrome/content/zotero/xpcom/translate/src/rdf/rdfparser.js rpm-licenses/tabulator-rdf/
cp resource/tinymce/license.txt rpm-licenses/tinymce/
cp .rpm-original-sources/tinymce-paste/LICENSE.TXT rpm-licenses/tinymce/paste-LICENSE.TXT
for package in fluent-bundle fluent-react; do
    mkdir -p rpm-licenses/$package
    cp .rpm-original-sources/$package/{LICENSE,NOTICE} rpm-licenses/$package/
done
cp reader/node_modules/@fluent/react/vendor/LICENSE rpm-licenses/fluent-react/vendor-LICENSE
mkdir -p rpm-licenses/react-select rpm-licenses/path-webpack rpm-licenses/cached-iterable
cp %{SOURCE29} rpm-licenses/react-select/LICENSE
cp %{SOURCE30} rpm-licenses/path-webpack/LICENSE
# This package's pinned manifest is its explicit Apache-2.0 declaration.
cp reader/node_modules/cached-iterable/package.json rpm-licenses/cached-iterable/
cp .rpm-original-sources/fluent-bundle/LICENSE rpm-licenses/cached-iterable/Apache-2.0.txt
for package in @babel/runtime @emotion/cache @emotion/core @emotion/css @emotion/hash \
    @emotion/memoize @emotion/serialize @emotion/sheet @emotion/stylis @emotion/unitless \
    @emotion/utils @emotion/weak-memoize memoize-one react-input-autosize react-is process \
    punycode querystring url; do
    directory="rpm-licenses/runtime/root/$package"
    mkdir -p "$directory"
    find "node_modules/$package" -maxdepth 1 -type f -iname 'license*' \
        -exec cp -t "$directory" {} +
    test -n "$(ls -A "$directory")"
done
for package in darkreader sentencex-ts sorted-btree; do
    mkdir -p rpm-licenses/$package
    cp reader/node_modules/$package/LICENSE rpm-licenses/$package/
done
for package in fflate fastest-levenshtein; do
    mkdir -p rpm-licenses/$package
    cp document-worker/node_modules/$package/LICENSE* rpm-licenses/$package/
done
for entry in reader:@babel/runtime reader:classnames reader:eld reader:event-emitter \
    reader:jszip reader:luaparse reader:pako reader:postcss-selector-parser reader:queue \
    reader:inherits reader:d reader:es5-ext reader:util-deprecate reader:cssesc \
    note-editor:@babel/runtime note-editor:classnames note-editor:entities \
    note-editor:linkify-it note-editor:markdown-it note-editor:mdurl note-editor:orderedmap \
    note-editor:punycode.js note-editor:rope-sequence note-editor:uc.micro note-editor:w3c-keyname \
    document-worker:dom-serializer document-worker:domelementtype document-worker:domhandler \
    document-worker:domutils document-worker:entities document-worker:htmlparser2; do
    project=${entry%%:*}
    package=${entry#*:}
    directory="rpm-licenses/runtime/$project/$package"
    mkdir -p "$directory"
    cp "$project/node_modules/$package"/LICENSE* "$directory/"
done
# Preserve every component's notice path without storing identical texts twice.
%{__python3} %{SOURCE31} rpm-licenses
install -d %{buildroot}%{_bindir} %{buildroot}%{_libdir}/zotero
cp -a app/staging/Zotero_linux-x86_64/. %{buildroot}%{_libdir}/zotero/
rm -f %{buildroot}%{_libdir}/zotero/{zotero.desktop,set_launcher_icon}
ln -s ../%{_lib}/zotero/zotero %{buildroot}%{_bindir}/zotero
ln -sf ../../../../share/zotero-libreoffice-integration/Zotero_LibreOffice_Integration.oxt \
    %{buildroot}%{_libdir}/zotero/integration/libreoffice/Zotero_LibreOffice_Integration.oxt
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE8}
install -Dpm 0644 .rpm-components/data/zotero-libreoffice-integration/Zotero_LibreOffice_Integration.oxt \
    %{buildroot}%{_datadir}/zotero-libreoffice-integration/Zotero_LibreOffice_Integration.oxt
for size in 32 64 128; do
    install -Dpm 0644 app/linux/icons/icon${size}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/zotero.png
done
install -Dpm 0644 app/linux/icons/symbolic.svg \
    %{buildroot}%{_datadir}/icons/hicolor/symbolic/apps/zotero-symbolic.svg

%check
component_sources="$PWD/.rpm-components/sources"
component_tools="$PWD/.rpm-components/tools"
component_data="$PWD/.rpm-components/data"
%include %{SOURCE36}
%{__python3} %{SOURCE26} . %{SOURCE23} %{SOURCE24} --check
%{__python3} - <<'PY'
import json
from pathlib import Path
sources = Path('.rpm-original-sources')
for directory, manifest, version, implementation in (
    ('fluent-bundle', 'fluent-bundle/package.json', '0.19.1', 'fluent-bundle/src/bundle.ts'),
    ('fluent-react', 'fluent-react/package.json', '0.15.2', 'fluent-react/src/index.ts'),
    ('darkreader', 'package.json', '4.9.83', 'src/api/index.ts'),
    ('sentencex-ts', 'package.json', '0.1.13-ts', 'src/index.ts'),
    ('fflate', 'package.json', '0.8.2', 'src/index.ts'),
    ('fastest-levenshtein', 'package.json', '1.0.16', 'mod.ts'),
    ('sorted-btree', 'package.json', '1.8.0', 'b+tree.ts'),
    ('tinymce', 'package.json', '4.9.4', 'src/core/main/ts/api/Editor.ts'),
    ('tinymce-paste', 'package.json', '4.6.7', 'src/plugins/paste/src/main/js/Plugin.js'),
):
    source = sources / directory
    assert json.loads((source / manifest).read_text())['version'] == version, directory
    assert (source / implementation).is_file(), directory
for name in ('b+tree.js', 'sorted-array.js'):
    original = (sources / 'sorted-btree' / name).read_text()
    assert original == (Path('reader/node_modules/sorted-btree') / name).read_text(), name
assert Path('resource/tinymce/license.txt').read_bytes() == Path('rpm-licenses/tinymce/license.txt').read_bytes()
assert (sources / 'tinymce-paste/LICENSE.TXT').read_bytes() == Path('rpm-licenses/tinymce/paste-LICENSE.TXT').read_bytes()
PY
node %{SOURCE13} .
node - <<'JS'
const assert = require('node:assert/strict');
const configurations = require('./note-editor/webpack.config.js');
const editor = configurations.find(configuration => configuration.name === 'zotero');
assert.equal(editor.optimization.minimize, false);
assert.deepEqual(editor.optimization.minimizer, []);
JS
node %{SOURCE9} chrome/content/zotero/xpcom/citeprocRsBridge.js
cmp note-editor/node_modules/@benrbray/prosemirror-math/LICENSE \
    rpm-licenses/prosemirror-math/LICENSE
%{__python3} - <<'PY'
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
with ZipFile("%{buildroot}%{_libdir}/zotero/app/omni.ja") as archive:
    onecrl = json.loads(Path(".rpm-onecrl.json").read_text())
    assert onecrl["changes"], "OneCRL snapshot must not be empty"
    assert json.loads(archive.read("defaults/settings/security-state/onecrl.json")) == {
        "data": onecrl["changes"], "timestamp": onecrl["timestamp"]}
    packaged = archive.read("chrome/devtools/modules/devtools/client/shared/vendor/source-map/lib/mappings.wasm")
    assert packaged == Path(".rpm-components/data/source-map-mappings-wasm/mappings.wasm").read_bytes()
    fonts = {path.name: path.read_bytes() for path in Path(".rpm-components/data/katex-js/fonts").glob("*.woff2")}
    assert len(fonts) == 20
    names = [name for name in archive.namelist()
             if name.startswith("resource/note-editor/assets/fonts/KaTeX_") and name.endswith(".woff2")]
    assert len(names) == len(fonts), "Obsolete or missing note-editor fonts"
    for name in names:
        original = Path(name).name.split(".")[0] + ".woff2"
        assert archive.read(name) == fonts[original], name
    pdf_fonts = list(Path("reader/pdfjs/pdf.js/external/standard_fonts").glob("LiberationSans-*.ttf"))
    assert not any("/RPMPDFSans-" in name for name in archive.namelist())
    assert len(pdf_fonts) == 4
    original_hashes = {
        "Bold": "361c61b82d575c5c35fd9157fda8b0194bcfcd0d88ea8521a4fb5dd53d33dddc",
        "BoldItalic": "a224075ac17495ad0a3af3bc0a419ac0704a8b3fd1095456201fb9b095fc281d",
        "Italic": "832b4406dbef23628800d3aaad21048534ac84d7e3ad955be83b8172ed8ef512",
        "Regular": "f8ace1f892b2bd9dc1792ba7f097fa7588f84fed48321480e04de5390828221f",
    }
    for path in pdf_fonts:
        style = path.stem.removeprefix("LiberationSans-")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == original_hashes[style], path
        assert archive.read("resource/reader/pdf/web/standard_fonts/" + path.name) == path.read_bytes(), path
    assert archive.read("resource/reader/pdf/web/standard_fonts/LICENSE_LIBERATION") == \
        Path(".rpm-font-sources/liberation/License.txt").read_bytes()
PY
desktop-file-validate %{buildroot}%{_datadir}/applications/zotero.desktop
test ! -e %{buildroot}%{_libdir}/zotero/updater
%{__python3} -c 'import json; assert json.load(open("%{buildroot}%{_libdir}/zotero/distribution/policies.json"))["policies"]["DisableAppUpdate"]'

%files
%license COPYING rpm-licenses
%doc source-commits.txt
%doc rpm-editor-source-inputs.json
%{_bindir}/zotero
%{_libdir}/zotero
%{_datadir}/applications/zotero.desktop
%{_datadir}/icons/hicolor/*/apps/zotero.png
%{_datadir}/icons/hicolor/symbolic/apps/zotero-symbolic.svg

%files libreoffice-integration
%license .rpm-components/sources/zotero-libreoffice-integration/COPYING
%{_datadir}/zotero-libreoffice-integration/

%changelog
* Sat Oct 31 2026 Matrew File <elfile4138@elfile4138.moe> - 10.0.7-2
- Bundle the Mozilla OneCRL snapshot for offline application assembly.

* Sat Oct 31 2026 Matrew File <elfile4138@elfile4138.moe> - 10.0.7-1
- Update Zotero to 10.0.7 and Gecko to 140.17.0 ESR.
- Build the OpenJPEG decoder without Relaxed SIMD for Gecko 140 compatibility.
- Include Document inline definitions in non-unified Gecko pointer-lock builds.

* Sat Oct 24 2026 Matrew File <elfile4138@elfile4138.moe> - 10.0.3-2
- Separate source and binary-repack packages with target-specific entry points.
- Select coinstallable LLVM and Binaryen toolchains on Rawhide.
- Remove duplicate source declarations and use relative application links.

* Tue Oct 06 2026 Matrew File <elfile4138@elfile4138.moe> - 10.0.3-1
- Build Zotero and Gecko from pinned sources with offline prerequisites.
* Sat Jan 24 2026 Matrew File <elfile4138@elfile4138.moe> - 8.0
- Upstream update to Zotero 8.
* Sun Oct 13 2024 Matrew File <elfile4138@elfile4138.moe> - 7.0.7
- Upstream update to Zotero 7.
- Fix Spec error.
* Mon Nov 13 2023 Matrew File <elfile4138@outlook.com> - 6.0.30
- Upstream update.
* Wed Mar 22 2023 Matrew File <elfile4138@outlook.com> - 6.0.23
- Initial package.
