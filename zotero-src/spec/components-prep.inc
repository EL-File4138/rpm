# typescript-source-js
mkdir -p "$component_tools/typescript-source-js"
cp %{SOURCE41} "$component_tools/typescript-source-js/build.py"
cp %{SOURCE42} "$component_tools/typescript-source-js/check.cjs"
(
    mkdir -p "$component_sources/typescript-source-js"
    cd "$component_sources/typescript-source-js"
tar -xf %{SOURCE40} --strip-components=1
)

# react-js
mkdir -p "$component_tools/react-js"
cp %{SOURCE45} "$component_tools/react-js/build.py"
cp %{SOURCE46} "$component_tools/react-js/esbuild-plugin.cjs"
cp %{SOURCE47} "$component_tools/react-js/check.cjs"
cp %{SOURCE48} "$component_tools/react-js/package.json"
cp %{SOURCE49} "$component_tools/react-js/package-lock.json"
cp %{SOURCE50} "$component_tools/react-js/install-npm-offline.py"
(
    mkdir -p "$component_sources/react-js"
    cd "$component_sources/react-js"
tar -xf %{SOURCE43} --strip-components=1
tar -xf %{SOURCE44}
mkdir rpm-dependencies
cp "$component_tools/react-js/package.json" rpm-dependencies/package.json
cp "$component_tools/react-js/package-lock.json" rpm-dependencies/package-lock.json
)

# prop-types-js
mkdir -p "$component_tools/prop-types-js"
cp %{SOURCE53} "$component_tools/prop-types-js/build.py"
cp %{SOURCE54} "$component_tools/prop-types-js/check.cjs"
(
    mkdir -p "$component_sources/prop-types-js"
    cd "$component_sources/prop-types-js"
tar -xf %{SOURCE51} --strip-components=1
mkdir rpm-object-assign
tar -xf %{SOURCE52} -C rpm-object-assign --strip-components=1
)

# react-autosuggest-js
mkdir -p "$component_tools/react-autosuggest-js"
cp %{SOURCE61} "$component_tools/react-autosuggest-js/react-themeable-LICENSE"
cp %{SOURCE62} "$component_tools/react-autosuggest-js/build.py"
cp %{SOURCE63} "$component_tools/react-autosuggest-js/check.cjs"
(
    mkdir -p "$component_sources/react-autosuggest-js"
    cd "$component_sources/react-autosuggest-js"
tar -xf %{SOURCE55} --strip-components=1
mkdir -p rpm-dependencies/{react-themeable,section-iterator,shallow-equal,prop-types,object-assign}
tar -xf %{SOURCE56} --strip-components=1 -C rpm-dependencies/react-themeable
tar -xf %{SOURCE57} --strip-components=1 -C rpm-dependencies/section-iterator
tar -xf %{SOURCE58} --strip-components=1 -C rpm-dependencies/shallow-equal
tar -xf %{SOURCE59} --strip-components=1 -C rpm-dependencies/prop-types
tar -xf %{SOURCE60} --strip-components=1 -C rpm-dependencies/object-assign
)

# react-virtualized-js
mkdir -p "$component_tools/react-virtualized-js"
cp %{SOURCE70} "$component_tools/react-virtualized-js/build.py"
cp %{SOURCE71} "$component_tools/react-virtualized-js/strip-flow.cjs"
cp %{SOURCE72} "$component_tools/react-virtualized-js/check.cjs"
cp %{SOURCE73} "$component_tools/react-virtualized-js/package.json"
cp %{SOURCE74} "$component_tools/react-virtualized-js/package-lock.json"
cp %{SOURCE75} "$component_tools/react-virtualized-js/install-npm-offline.py"
(
    mkdir -p "$component_sources/react-virtualized-js"
    cd "$component_sources/react-virtualized-js"
tar -xf %{SOURCE64} --strip-components=1
tar -xf %{SOURCE69}
mkdir -p rpm-dependencies/{clsx,dom-helpers,react-lifecycles-compat,prop-types}
tar -xf %{SOURCE65} --strip-components=1 -C rpm-dependencies/clsx
tar -xf %{SOURCE66} --strip-components=1 -C rpm-dependencies/dom-helpers
tar -xf %{SOURCE67} --strip-components=1 -C rpm-dependencies/react-lifecycles-compat
tar -xf %{SOURCE59} --strip-components=1 -C rpm-dependencies/prop-types
mkdir rpm-build-dependencies
cp "$component_tools/react-virtualized-js/package.json" rpm-build-dependencies/package.json
cp "$component_tools/react-virtualized-js/package-lock.json" rpm-build-dependencies/package-lock.json
)

# react-intl-js
mkdir -p "$component_tools/react-intl-js"
cp %{SOURCE84} "$component_tools/react-intl-js/build.py"
cp %{SOURCE85} "$component_tools/react-intl-js/generate-parser.cjs"
cp %{SOURCE86} "$component_tools/react-intl-js/check.cjs"
cp %{SOURCE87} "$component_tools/react-intl-js/package.json"
cp %{SOURCE88} "$component_tools/react-intl-js/package-lock.json"
cp %{SOURCE89} "$component_tools/react-intl-js/install-npm-offline.py"
(
    mkdir -p "$component_sources/react-intl-js"
    cd "$component_sources/react-intl-js"
tar -xf %{SOURCE76} --strip-components=1
tar -xf %{SOURCE83}
mkdir -p rpm-dependencies/{intl-messageformat,intl-messageformat-parser,intl-format-cache,intl-utils,hoist-non-react-statics,shallow-equal}
tar -xf %{SOURCE77} --strip-components=1 -C rpm-dependencies/intl-messageformat
tar -xf %{SOURCE78} --strip-components=1 -C rpm-dependencies/intl-messageformat-parser
tar -xf %{SOURCE79} --strip-components=3 -C rpm-dependencies/intl-format-cache formatjs-3b26952abcbb1fa625ac8b465ef6ed6136ca19d3/packages/intl-format-cache
tar -xf %{SOURCE80} --strip-components=3 -C rpm-dependencies/intl-utils formatjs-5b218606c3ec03e332f472706fffd04153c20dae/packages/intl-utils
tar -xf %{SOURCE81} --strip-components=1 -C rpm-dependencies/hoist-non-react-statics
tar -xf %{SOURCE58} --strip-components=1 -C rpm-dependencies/shallow-equal
mkdir rpm-build-dependencies
cp "$component_tools/react-intl-js/package.json" rpm-build-dependencies/package.json
cp "$component_tools/react-intl-js/package-lock.json" rpm-build-dependencies/package-lock.json
)

# ace-js
mkdir -p "$component_tools/ace-js"
cp %{SOURCE92} "$component_tools/ace-js/build.py"
cp %{SOURCE93} "$component_tools/ace-js/check.cjs"
cp %{SOURCE94} "$component_tools/ace-js/package.json"
cp %{SOURCE95} "$component_tools/ace-js/package-lock.json"
cp %{SOURCE96} "$component_tools/ace-js/install-npm-offline.py"
(
    mkdir -p "$component_sources/ace-js"
    cd "$component_sources/ace-js"
tar -xf %{SOURCE90} --strip-components=1
tar -xf %{SOURCE91}
mkdir rpm-dependencies
cp "$component_tools/ace-js/package.json" rpm-dependencies/package.json
cp "$component_tools/ace-js/package-lock.json" rpm-dependencies/package-lock.json
)

# pako-js
mkdir -p "$component_tools/pako-js"
cp %{SOURCE99} "$component_tools/pako-js/build.py"
cp %{SOURCE100} "$component_tools/pako-js/check.cjs"
(
    mkdir -p "$component_sources/pako-js"
    cd "$component_sources/pako-js"
tar -xf %{SOURCE98} --strip-components=1
)

# katex-js
mkdir -p "$component_tools/katex-js"
cp %{SOURCE103} "$component_tools/katex-js/build.py"
cp %{SOURCE104} "$component_tools/katex-js/check.mjs"
cp %{SOURCE105} "$component_tools/katex-js/strip-flow.cjs"
cp %{SOURCE106} "$component_tools/katex-js/package.json"
cp %{SOURCE107} "$component_tools/katex-js/package-lock.json"
cp %{SOURCE108} "$component_tools/katex-js/install-npm-offline.py"
cp %{SOURCE109} "$component_tools/katex-js/build-fonts.py"
cp %{SOURCE110} "$component_tools/katex-js/check-fonts.py"
cp %{SOURCE113} "$component_tools/katex-js/collect-font-notices.py"
(
    mkdir -p "$component_sources/katex-js"
    cd "$component_sources/katex-js"
tar -xf %{SOURCE101} --strip-components=1
tar -xf %{SOURCE102}
mkdir rpm-build-dependencies
cp "$component_tools/katex-js/package.json" rpm-build-dependencies/package.json
cp "$component_tools/katex-js/package-lock.json" rpm-build-dependencies/package-lock.json
rm -rf dist fonts
%{__python3} - <<'PY'
from pathlib import Path
from zipfile import ZipFile
directory = Path('rpm-input-font-licenses')
directory.mkdir()
with ZipFile('%{SOURCE111}') as archive:
    (directory / 'AMS-OFL.txt').write_bytes(archive.read('amsfonts/doc/OFL.txt'))
with ZipFile('%{SOURCE112}') as archive:
    (directory / 'RSFS-README').write_bytes(archive.read('rsfs/README'))
PY
)

# mathjax-chtml-js
mkdir -p "$component_tools/mathjax-chtml-js"
cp %{SOURCE116} "$component_tools/mathjax-chtml-js/build.cjs"
cp %{SOURCE117} "$component_tools/mathjax-chtml-js/check.cjs"
(
    mkdir -p "$component_sources/mathjax-chtml-js"
    cd "$component_sources/mathjax-chtml-js"
tar -xf %{SOURCE114} --strip-components=1
mkdir rpm-chemistry
tar -xf %{SOURCE115} -C rpm-chemistry --strip-components=1
rm -rf js es5 rpm-chemistry/dist rpm-chemistry/esm
)

# monaco-editor-js
mkdir -p "$component_tools/monaco-editor-js"
cp %{SOURCE132} "$component_tools/monaco-editor-js/build-core.cjs"
cp %{SOURCE133} "$component_tools/monaco-editor-js/build-languages.py"
cp %{SOURCE134} "$component_tools/monaco-editor-js/build-font.py"
cp %{SOURCE135} "$component_tools/monaco-editor-js/build-font.cjs"
cp %{SOURCE136} "$component_tools/monaco-editor-js/check.cjs"
cp %{SOURCE137} "$component_tools/monaco-editor-js/check-font.py"
cp %{SOURCE138} "$component_tools/monaco-editor-js/build-typescript.py"
cp %{SOURCE139} "$component_tools/monaco-editor-js/install-npm-offline.py"
cp %{SOURCE140} "$component_tools/monaco-editor-js/font-package.json"
cp %{SOURCE141} "$component_tools/monaco-editor-js/font-package-lock.json"
(
    mkdir -p "$component_sources/monaco-editor-js"
    cd "$component_sources/monaco-editor-js"
tar -xf %{SOURCE118} --strip-components=1
mkdir -p rpm-sources/dependencies rpm-font-dependencies
for pair in 'vscode %{SOURCE119}' 'typescript %{SOURCE120}' 'loader %{SOURCE121}' 'codicons %{SOURCE122}' \
    'vscode-css-languageservice %{SOURCE123}' 'vscode-html-languageservice %{SOURCE124}' \
    'vscode-json-languageservice %{SOURCE125}' 'textdocument %{SOURCE126}' 'types %{SOURCE127}' \
    'vscode-uri %{SOURCE128}' 'jsonc-parser %{SOURCE129}'; do
    set -- $pair
    mkdir rpm-sources/$1
    tar -xf "$2" -C rpm-sources/$1 --strip-components=1
done
for package in vscode-css-languageservice vscode-html-languageservice vscode-json-languageservice vscode-uri jsonc-parser; do
    ln -s ../$package rpm-sources/dependencies/$package
done
ln -s ../textdocument/textDocument rpm-sources/dependencies/vscode-languageserver-textdocument
ln -s ../types/types rpm-sources/dependencies/vscode-languageserver-types
tar -xf %{SOURCE130}
cp "$component_tools/monaco-editor-js/font-package.json" rpm-font-dependencies/package.json
cp "$component_tools/monaco-editor-js/font-package-lock.json" rpm-font-dependencies/package-lock.json
cp "$component_tools/monaco-editor-js/build-core.cjs" build-core.cjs
cp "$component_tools/monaco-editor-js/build-languages.py" build-languages.py
cp "$component_tools/monaco-editor-js/build-font.py" build-font.py
cp "$component_tools/monaco-editor-js/build-font.cjs" build-font.cjs
cp "$component_tools/monaco-editor-js/build-typescript.py" build-typescript.py
)

# monacopilot-js
mkdir -p "$component_tools/monacopilot-js"
cp %{SOURCE143} "$component_tools/monacopilot-js/build.py"
cp %{SOURCE144} "$component_tools/monacopilot-js/check.mjs"
(
    mkdir -p "$component_sources/monacopilot-js"
    cd "$component_sources/monacopilot-js"
tar -xf %{SOURCE142} --strip-components=1
)

# source-map-mappings-wasm
mkdir -p "$component_tools/source-map-mappings-wasm"
cp %{SOURCE147} "$component_tools/source-map-mappings-wasm/Cargo.lock"
cp %{SOURCE148} "$component_tools/source-map-mappings-wasm/check.mjs"
cp %{SOURCE149} "$component_tools/source-map-mappings-wasm/bundled-licenses.txt"
cp %{SOURCE150} "$component_tools/source-map-mappings-wasm/bundled-provides.inc"
cp %{SOURCE151} "$component_tools/source-map-mappings-wasm/explicit-callback-import.patch"
(
    mkdir -p "$component_sources/source-map-mappings-wasm"
    cd "$component_sources/source-map-mappings-wasm"
tar -xf %{SOURCE145} --strip-components=1
patch -p1 < "$component_tools/source-map-mappings-wasm/explicit-callback-import.patch"
tar -xf %{SOURCE146}
rm -f lib/mappings.wasm
cp "$component_tools/source-map-mappings-wasm/Cargo.lock" wasm-mappings/source-map-mappings-wasm-api/Cargo.lock
mkdir -p .cargo
cp vendor-config.toml .cargo/config.toml
find vendor -type f -name '*.rs' -exec chmod a-x {} +
)

# citeproc-rs-wasm
mkdir -p "$component_tools/citeproc-rs-wasm"
cp %{SOURCE154} "$component_tools/citeproc-rs-wasm/Cargo.lock"
cp %{SOURCE155} "$component_tools/citeproc-rs-wasm/build-bindings.py"
cp %{SOURCE156} "$component_tools/citeproc-rs-wasm/check-bindings.cjs"
cp %{SOURCE157} "$component_tools/citeproc-rs-wasm/bundled-licenses.txt"
cp %{SOURCE158} "$component_tools/citeproc-rs-wasm/bundled-provides.inc"
cp %{SOURCE160} "$component_tools/citeproc-rs-wasm/modern-rust.patch"
cp %{SOURCE161} "$component_tools/citeproc-rs-wasm/smartstring-compat.patch"
(
    mkdir -p "$component_sources/citeproc-rs-wasm"
    cd "$component_sources/citeproc-rs-wasm"
tar -xf %{SOURCE152} --strip-components=1
mkdir rpm-lazy-transform-str
tar -xf %{SOURCE159} -C rpm-lazy-transform-str --strip-components=1
patch -p1 < "$component_tools/citeproc-rs-wasm/modern-rust.patch"
patch -p1 < "$component_tools/citeproc-rs-wasm/smartstring-compat.patch"
tar -xf %{SOURCE153}
cp "$component_tools/citeproc-rs-wasm/Cargo.lock" Cargo.lock
mkdir -p .cargo
cp vendor-config.toml .cargo/config.toml
rm .cargo/config
)

# csl-validator-wasm
mkdir -p "$component_tools/csl-validator-wasm"
cp %{SOURCE165} "$component_tools/csl-validator-wasm/check-validator.mjs"
(
    mkdir -p "$component_sources/csl-validator-wasm"
    cd "$component_sources/csl-validator-wasm"
tar -xf %{SOURCE162} --strip-components=1
tar -xf %{SOURCE163}
rm -rf src/schema dist
mv schema-e3ce254a72c4470a5ed3b9d23b428017d25674e9 src/schema
tar -xjf src/libs/expat-2.7.1.tar.bz2 -C src/libs
tar -xjf src/libs/rnv-1.7.11.tar.bz2 -C src/libs
find . -type f \( -name '*.wasm' -o -name '*.o' -o -name '*.a' \) -delete
)

# pdfjs-codecs
mkdir -p "$component_tools/pdfjs-codecs"
cp %{SOURCE174} "$component_tools/pdfjs-codecs/Cargo.lock"
cp %{SOURCE176} "$component_tools/pdfjs-codecs/bundled-licenses.txt"
cp %{SOURCE177} "$component_tools/pdfjs-codecs/bundled-provides.inc"
cp %{SOURCE178} "$component_tools/pdfjs-codecs/check-codecs.mjs"
(
    mkdir -p "$component_sources/pdfjs-codecs"
    cd "$component_sources/pdfjs-codecs"
tar -xf %{SOURCE166}
tar -xf %{SOURCE167}
tar -xf %{SOURCE168}
tar -xf %{SOURCE169}
tar -xf %{SOURCE170}
tar -xf %{SOURCE171}
tar -xf %{SOURCE172}
mv pdf.js.openjpeg-8bb19dc1aeecb104ce2ed3493d41fe131fc681e0 openjpeg-wrapper
mv openjpeg-6c4a29b00211eb0430fa0e5e890f1ce5c80f409f openjpeg
mv pdf.js.jbig2-15f6f9357c5e5e30285eb83aa08e5fe1a16ab77a jbig2-wrapper
mv pdfium-bb1f9f71e7b15afdd5937adf8cfe5807522b882f pdfium
mv pdf.js.quickjs-e2c5bfc8194b16f5973eea5e4e025b67be3c1015 quickjs-wrapper
mv quickjs-3d5e064e9dd67c70f7962836505a7fa067bf0a4e quickjs
mv pdf.js.qcms-bddcbcb3c2184c900620680751044ba42ece86ad qcms-wrapper
patch -d openjpeg -p1 < openjpeg-wrapper/0001-Add-support-for-buffer-based-stream-see-https-github.patch
patch -d quickjs -p1 < quickjs-wrapper/0001-Extra-stuff-for-use-with-PDF.js.patch
# Use the caller's writable cache and omit optional Closure minification.
sed -i 's|export EM_CACHE=.*|export EM_CACHE|' openjpeg-wrapper/compile*.sh
sed -i 's/--closure 1/--closure 0/' quickjs-wrapper/compile.sh
tar -xJf %{SOURCE173} -C qcms-wrapper
cp "$component_tools/pdfjs-codecs/Cargo.lock" qcms-wrapper/Cargo.lock
mkdir -p qcms-wrapper/.cargo
cp qcms-wrapper/vendor-config.toml qcms-wrapper/.cargo/config.toml
find . -type f \( -name '*.wasm' -o -name '*.o' -o -name '*.a' \) -delete
)

# onnxruntime-web-wasm
mkdir -p "$component_tools/onnxruntime-web-wasm"
cp %{SOURCE181} "$component_tools/onnxruntime-web-wasm/prepare-offline.py"
cp %{SOURCE183} "$component_tools/onnxruntime-web-wasm/check-runtime.mjs"
cp %{SOURCE184} "$component_tools/onnxruntime-web-wasm/identity.prototxt"
cp %{SOURCE185} "$component_tools/onnxruntime-web-wasm/prepare-bindings.py"
cp %{SOURCE186} "$component_tools/onnxruntime-web-wasm/check-bindings.mjs"
(
    mkdir -p "$component_sources/onnxruntime-web-wasm"
    cd "$component_sources/onnxruntime-web-wasm"
tar -xf %{SOURCE179} --strip-components=1
tar -xf %{SOURCE180}
%{__python3} "$component_tools/onnxruntime-web-wasm/prepare-offline.py" . onnx-sources
)

# zotero-libreoffice-integration
mkdir -p "$component_tools/zotero-libreoffice-integration"
cp %{SOURCE188} "$component_tools/zotero-libreoffice-integration/prepare-extension.py"
(
    mkdir -p "$component_sources/zotero-libreoffice-integration"
    cd "$component_sources/zotero-libreoffice-integration"
tar -xf %{SOURCE187} --strip-components=1
# Rebuild the extension and use Fedora's Java libraries.
rm -rf build/lib build/bin
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.oxt' \) -delete
)
