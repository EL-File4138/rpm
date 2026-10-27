# typescript-source-js
(
    cd "$component_sources/typescript-source-js"
python3 "$component_tools/typescript-source-js/build.py" "$PWD" --esbuild %{_bindir}/esbuild
install -Dpm0644 dist/typescript.js "$component_data/typescript-source-js"/typescript.js
install -pm0644 dist/*.d.ts "$component_data/typescript-source-js"/
mkdir -p "$component_licenses/typescript-source-js"
cp -a LICENSE.txt ThirdPartyNoticeText.txt "$component_licenses/typescript-source-js"/
)

# react-js
(
    cd "$component_sources/react-js"
%{__python3} "$component_tools/react-js/install-npm-offline.py" rpm-dependencies "$PWD/npm-sources"
%{__python3} "$component_tools/react-js/build.py" . rpm-dependencies/node_modules "$component_tools/react-js/esbuild-plugin.cjs"
mkdir -p "$component_data/react-js"
for package in react react-dom react-is scheduler; do
    cp -a build/node_modules/$package "$component_data/react-js"/
done
mkdir -p "$component_licenses/react-js"
cp -a LICENSE "$component_licenses/react-js"/
)

# prop-types-js
(
    cd "$component_sources/prop-types-js"
%{__python3} "$component_tools/prop-types-js/build.py" . rpm-object-assign --esbuild %{_bindir}/esbuild --react "$component_data/react-js"
install -Dpm 0644 rpm-dist/prop-types.js "$component_data/prop-types-js"/prop-types.js
cp -a "$component_licenses/react-js" rpm-licenses/react-is
mkdir -p "$component_licenses/prop-types-js"
cp -a LICENSE rpm-licenses "$component_licenses/prop-types-js"/
)

# react-autosuggest-js
(
    cd "$component_sources/react-autosuggest-js"
%{__python3} "$component_tools/react-autosuggest-js/build.py" . rpm-dependencies
cp "$component_tools/react-autosuggest-js/react-themeable-LICENSE" rpm-licenses/react-themeable-LICENSE
install -Dpm 0644 rpm-dist/autosuggest.min.js "$component_data/react-autosuggest-js"/autosuggest.min.js
mkdir -p "$component_licenses/react-autosuggest-js"
cp -a LICENSE rpm-licenses "$component_licenses/react-autosuggest-js"/
)

# react-virtualized-js
(
    cd "$component_sources/react-virtualized-js"
%{__python3} "$component_tools/react-virtualized-js/install-npm-offline.py" rpm-build-dependencies "$PWD/npm-sources"
%{__python3} "$component_tools/react-virtualized-js/build.py" . rpm-dependencies rpm-build-dependencies/node_modules
install -Dpm 0644 rpm-dist/react-virtualized.js "$component_data/react-virtualized-js"/react-virtualized.js
mkdir -p "$component_licenses/react-virtualized-js"
cp -a LICENSE rpm-licenses "$component_licenses/react-virtualized-js"/
)

# react-intl-js
(
    cd "$component_sources/react-intl-js"
%{__python3} "$component_tools/react-intl-js/install-npm-offline.py" rpm-build-dependencies "$PWD/npm-sources"
%{__python3} "$component_tools/react-intl-js/build.py" . rpm-dependencies rpm-build-dependencies "$component_data/react-js"
install -Dpm 0644 dist/react-intl.min.js "$component_data/react-intl-js"/react-intl.min.js
mkdir -p "$component_licenses/react-intl-js"
cp -a LICENSE.md rpm-licenses "$component_licenses/react-intl-js"/
)

# ace-js
(
    cd "$component_sources/ace-js"
%{__python3} "$component_tools/ace-js/install-npm-offline.py" rpm-dependencies "$PWD/npm-sources"
%{__python3} "$component_tools/ace-js/build.py" . rpm-dependencies/node_modules
cp %{SOURCE97} rpm-licenses/CodeMirror-LICENSE
mkdir -p "$component_data/ace-js"
for module in ace ext-searchbox keybinding-emacs keybinding-vim mode-javascript theme-chrome theme-monokai worker-javascript; do
    install -pm 0644 build/src/$module.js "$component_data/ace-js"/
done
mkdir -p "$component_licenses/ace-js"
cp -a LICENSE rpm-licenses "$component_licenses/ace-js"/
)

# pako-js
(
    cd "$component_sources/pako-js"
%{__python3} "$component_tools/pako-js/build.py" . --esbuild %{_bindir}/esbuild
install -Dpm 0644 rpm-dist/pako.min.js "$component_data/pako-js"/pako.min.js
mkdir -p "$component_licenses/pako-js"
cp -a LICENSE ZLIB-LICENSE "$component_licenses/pako-js"/
)

# katex-js
(
    cd "$component_sources/katex-js"
export GOMAXPROCS=1 UV_THREADPOOL_SIZE=1 NODE_OPTIONS=--max-old-space-size=1400
%{__python3} "$component_tools/katex-js/build-fonts.py" .
%{__python3} "$component_tools/katex-js/install-npm-offline.py" rpm-build-dependencies "$PWD/npm-sources"
%{__python3} "$component_tools/katex-js/build.py" . rpm-build-dependencies/node_modules --esbuild %{_bindir}/esbuild
mkdir -p "$component_data/katex-js"
cp rpm-dist/katex.js rpm-dist/katex.mjs "$component_data/katex-js"/
cp -a fonts "$component_data/katex-js"/
mkdir rpm-font-licenses
cp rpm-input-font-licenses/* rpm-font-licenses/
%{__python3} "$component_tools/katex-js/collect-font-notices.py" rpm-font-licenses
cp %{_licensedir}/texlive-amsfonts/ofl.txt rpm-font-licenses/
cp %{_licensedir}/texlive-cm/knuth.txt rpm-font-licenses/
cp %{_licensedir}/texlive-rsfs/other-free.txt rpm-font-licenses/
%{__python3} - <<'PY'
from pathlib import Path
from fontTools.ttLib import TTFont
notices = set()
for filename in sorted(Path('fonts').glob('*.ttf')):
    for record in TTFont(filename)['name'].names:
        if record.nameID in (0, 13, 14):
            notices.add(record.toUnicode().strip())
Path('rpm-font-licenses/font-notices.txt').write_text('\n\n'.join(sorted(notices)) + '\n')
PY
mkdir -p "$component_licenses/katex-js"
cp -a LICENSE rpm-font-licenses "$component_licenses/katex-js"/
)

# mathjax-chtml-js
(
    cd "$component_sources/mathjax-chtml-js"
export UV_THREADPOOL_SIZE=1 NODE_OPTIONS=--max-old-space-size=1400
node "$component_tools/mathjax-chtml-js/build.cjs" . rpm-chemistry "$component_data/typescript-source-js"/typescript.js
mkdir -p "$component_data/mathjax-chtml-js"
cp -a rpm-dist/. "$component_data/mathjax-chtml-js"/
mkdir -p rpm-licenses/mhchemparser
cp rpm-chemistry/LICENSE.txt rpm-licenses/mhchemparser/
mkdir -p "$component_licenses/mathjax-chtml-js"
cp -a LICENSE rpm-licenses "$component_licenses/mathjax-chtml-js"/
)

# monaco-editor-js
(
    cd "$component_sources/monaco-editor-js"
export GOMAXPROCS=1 UV_THREADPOOL_SIZE=1
export NODE_OPTIONS=--max-old-space-size=4096
%{__python3} "$component_tools/monaco-editor-js/install-npm-offline.py" rpm-font-dependencies npm-sources
mkdir -p dev
%{__python3} build-typescript.py rpm-sources/typescript --source-version 5.4.0 --esbuild %{_bindir}/esbuild
%{__python3} build-font.py rpm-sources/codicons rpm-sources/vscode \
    dev/vs/base/browser/ui/codicons/codicon/codicon.ttf rpm-font-dependencies
node build-core.cjs rpm-sources/vscode dev rpm-sources/typescript/dist/typescript.js rpm-sources/loader
%{__python3} build-languages.py . rpm-sources/dependencies \
    "$component_data/typescript-source-js" dev --esbuild %{_bindir}/esbuild --vscode rpm-sources/vscode
for pair in 'vscode LICENSE.txt' 'vscode ThirdPartyNotices.txt' \
    'typescript LICENSE.txt' 'typescript ThirdPartyNoticeText.txt' \
    'loader License.txt' 'loader ThirdPartyNotices.txt' \
    'codicons LICENSE' 'codicons LICENSE-CODE'; do
    set -- $pair
    cp "rpm-sources/$1/$2" "rpm-licenses/$1-$2"
done
mkdir -p "$component_data/monaco-editor-js"
cp -a dev/. "$component_data/monaco-editor-js"/
# Preserve the embedded compiler and library declarations' license notices.
cp -a "$component_licenses/typescript-source-js" rpm-licenses/typescript-runtime
mkdir -p "$component_licenses/monaco-editor-js"
cp -a LICENSE.txt rpm-licenses "$component_licenses/monaco-editor-js"/
)

# monacopilot-js
(
    cd "$component_sources/monacopilot-js"
%{__python3} "$component_tools/monacopilot-js/build.py" .
mkdir -p "$component_data/monacopilot-js"/{core,monacopilot}
for component in core monacopilot; do
    install -pm 0644 dist/$component/*.js dist/$component/*.mjs \
        "$component_data/monacopilot-js"/$component/
done
mkdir -p "$component_licenses/monacopilot-js"
cp -a LICENSE "$component_licenses/monacopilot-js"/
)

# source-map-mappings-wasm
(
    cd "$component_sources/source-map-mappings-wasm"
export CARGO_HOME="$PWD/cargo-home"
export CARGO_NET_OFFLINE=true
export CARGO_BUILD_JOBS=%{_smp_build_ncpus}
export CARGO_TARGET_DIR="$PWD/target"
# Native RPM link arguments are not valid for wasm32-unknown-unknown.
export RUSTFLAGS='-C opt-level=2 -C panic=abort'
cargo build --frozen --release --target wasm32-unknown-unknown \
    --manifest-path wasm-mappings/source-map-mappings-wasm-api/Cargo.toml
install -Dpm 0644 target/wasm32-unknown-unknown/release/source_map_mappings_wasm_api.wasm \
    "$component_data/source-map-mappings-wasm"/mappings.wasm
cp "$component_tools/source-map-mappings-wasm/bundled-licenses.txt" bundled-licenses.txt
mkdir -p "$component_licenses/source-map-mappings-wasm"
cp -a LICENSE bundled-licenses.txt "$component_licenses/source-map-mappings-wasm"/
)

# citeproc-rs-wasm
(
    cd "$component_sources/citeproc-rs-wasm"
# Native RPM linker flags do not apply to WASM; retain upstream's target flags.
unset RUSTFLAGS CARGO_ENCODED_RUSTFLAGS
export CARGO_HOME="$PWD/cargo-home"
export CARGO_NET_OFFLINE=true
export CARGO_BUILD_JOBS=%{_smp_build_ncpus}
export BINARYEN_CORES=1
export CARGO_TARGET_DIR="$PWD/target"
# Build in this directory to retain upstream's 8 MiB WASM stack setting.
pushd crates/wasm
cargo build --frozen --release --target wasm32-unknown-unknown --features console,zotero
popd
%{__python3} "$component_tools/citeproc-rs-wasm/build-bindings.py" target/wasm32-unknown-unknown/release/wasm.wasm bindings
install -d "$component_data/citeproc-rs-wasm"
install -pm 0644 bindings/citeproc_rs_wasm.js bindings/citeproc_rs_wasm_include.js \
    bindings/citeproc_rs_wasm_bg.wasm "$component_data/citeproc-rs-wasm"/
install -pm 0644 "$component_tools/citeproc-rs-wasm/bundled-licenses.txt" bundled-licenses.txt
mkdir -p "$component_licenses/citeproc-rs-wasm"
cp -a LICENSE.md bundled-licenses.txt rpm-lazy-transform-str/LICENSE-* "$component_licenses/citeproc-rs-wasm"/
)

# csl-validator-wasm
(
    cd "$component_sources/csl-validator-wasm"
export EM_CACHE="$PWD/emscripten-cache"
export EMCC_CORES=%{_smp_build_ncpus}
root="$PWD"
export CFLAGS=-O2 CXXFLAGS=-O2 CPPFLAGS= LDFLAGS=
(
    cd src/libs/expat-2.7.1
    emconfigure ./configure --host=wasm32-unknown-emscripten \
        --disable-shared --without-xmlwf --without-docbook --without-tests --without-examples CFLAGS=-O2
    emmake make -j%{_smp_build_ncpus}
)
(
    cd src/libs/rnv-1.7.11
    mkdir -p schema
    cp "$root"/src/schema/schemas/styles/*.rnc schema/
    emconfigure ./configure --host=wasm32-unknown-emscripten \
        --with-expat-inc=../expat-2.7.1/lib --with-expat-lib=../expat-2.7.1/lib/.libs \
        ac_cv_lib_expat_XML_SetDoctypeDeclHandler=yes
    emmake make -j%{_smp_build_ncpus} rnv AR=emar CFLAGS=-O2 \
        LDFLAGS='-L../expat-2.7.1/lib/.libs -sMODULARIZE -sEXPORT_ES6 -sEXPORT_NAME=RNV -sEXPORTED_RUNTIME_METHODS=FS -sWASM_ASYNC_COMPILATION=0 --embed-file schema/'
    mkdir -p "$root/dist"
    install -m 0644 rnv "$root/dist/rnv.mjs"
    install -m 0644 rnv.wasm "$root/dist/rnv.wasm"
)
install -d "$component_data/csl-validator-wasm"
install -pm 0644 csl-validator.mjs worker.mjs dist/rnv.mjs dist/rnv.wasm \
    "$component_data/csl-validator-wasm"/
mkdir -p "$component_licenses/csl-validator-wasm"
cp -a LICENSE.txt LICENSE_LIBS.txt "$component_licenses/csl-validator-wasm"/
)

# pdfjs-codecs
(
    cd "$component_sources/pdfjs-codecs"
root="$PWD"
export EM_CACHE="$PWD/emscripten-cache" CARGO_HOME="$PWD/cargo-home"
for component in openjpeg jbig2 quickjs qcms; do
    (
        cd "$root/$component-wrapper"
        export INPUT="$PWD/src" OUTPUT="$root/dist/$component"
        mkdir -p "$OUTPUT"
        if test "$component" = qcms; then
            unset RUSTFLAGS CARGO_ENCODED_RUSTFLAGS
            export CARGO_TARGET_DIR="$root/qcms-target"
            cargo build --frozen --release --target wasm32-unknown-unknown
            wasm-bindgen "$CARGO_TARGET_DIR/wasm32-unknown-unknown/release/qcms_pdf_js.wasm" \
                --target web --no-typescript --omit-default-module-path --out-name qcms --out-dir "$OUTPUT"
            wasm-opt -O "$OUTPUT/qcms_bg.wasm" -o "$OUTPUT/qcms_bg.wasm"
            cp js/*.js "$OUTPUT/"
        else
            export OPENJPEG="$root/openjpeg" PDFIUM="$root/pdfium" QUICKJS="$root/quickjs"
            for BUILD_TYPE in wasm js; do
                export BUILD_TYPE
                if test "$component" = quickjs && test "$BUILD_TYPE" = js; then continue; fi
                if test "$component" = openjpeg; then sh compile_lib.sh; fi
                sh compile.sh
            done
        fi
    )
done
install -d "$component_data/pdfjs-codecs"
cp -pr dist/* "$component_data/pdfjs-codecs"/
mkdir -p licenses
for component in openjpeg-wrapper openjpeg jbig2-wrapper pdfium quickjs-wrapper quickjs qcms-wrapper; do
    install -pm 0644 "$component/LICENSE" "licenses/$component-LICENSE"
done
install -pm 0644 "$component_tools/pdfjs-codecs/bundled-licenses.txt" licenses/bundled-licenses.txt
mkdir -p "$component_licenses/pdfjs-codecs"
cp -a licenses "$component_licenses/pdfjs-codecs"/
)

# onnxruntime-web-wasm
(
    cd "$component_sources/onnxruntime-web-wasm"
export EM_CACHE="$PWD/emscripten-cache"
mkdir host-sources
unzip -q onnx-sources/protobuf.zip -d host-sources
cmake -S host-sources/protobuf-21.12/cmake -B native-protobuf \
    -DCMAKE_BUILD_TYPE=Release -Dprotobuf_BUILD_TESTS=OFF -Dprotobuf_WITH_ZLIB=OFF \
    -Dprotobuf_BUILD_SHARED_LIBS=OFF -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build native-protobuf --target protoc --parallel %{_smp_build_ncpus}
unset CFLAGS CXXFLAGS CPPFLAGS LDFLAGS
emcmake cmake -S cmake -B wasm-build \
    -DCMAKE_BUILD_TYPE=Release '-DCMAKE_C_FLAGS_RELEASE=-O2 -DNDEBUG' \
    '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG -Wno-error=pass-failed' \
    -DCMAKE_COMPILE_WARNING_AS_ERROR=OFF -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DFETCHCONTENT_TRY_FIND_PACKAGE_MODE=NEVER -DFETCHCONTENT_UPDATES_DISCONNECTED=ON \
    -DONNX_CUSTOM_PROTOC_EXECUTABLE="$PWD/native-protobuf/protoc" \
    -Donnxruntime_BUILD_UNIT_TESTS=OFF -Donnxruntime_BUILD_BENCHMARKS=OFF \
    -Donnxruntime_ENABLE_CPUINFO=OFF -Donnxruntime_USE_XNNPACK=OFF \
    -Donnxruntime_USE_JSEP=OFF -Donnxruntime_USE_WEBGPU=OFF -Donnxruntime_USE_WEBNN=OFF \
    -Donnxruntime_ENABLE_TRAINING=OFF -Donnxruntime_ENABLE_LTO=OFF \
    -Donnxruntime_ENABLE_WEBASSEMBLY_SIMD=ON -Donnxruntime_ENABLE_WEBASSEMBLY_THREADS=ON \
    -Donnxruntime_ENABLE_WEBASSEMBLY_API_EXCEPTION_CATCHING=ON -Donnxruntime_BUILD_SHARED_LIB=OFF
cmake --build wasm-build --target onnxruntime_webassembly --parallel %{_smp_build_ncpus}
%{__python3} "$component_tools/onnxruntime-web-wasm/prepare-bindings.py" prepare .
%{_bindir}/esbuild js/web/lib/index.ts --bundle --format=esm --platform=browser \
    --target=es2022 --tree-shaking=true --minify-syntax \
    --alias:onnxruntime-common="$PWD/js/common/lib/index.ts" \
    --outfile=wasm-build/ort.wasm.mjs --metafile=wasm-build/bindings-inputs.json \
    '--external:node:*' --external:module --external:worker_threads \
    --define:process=undefined --define:ENVIRONMENT_IS_NODE=false --define:isNode=false \
    --define:BUILD_DEFS.DISABLE_WEBGL=true --define:BUILD_DEFS.DISABLE_JSEP=true \
    --define:BUILD_DEFS.DISABLE_WASM=false --define:BUILD_DEFS.DISABLE_WASM_PROXY=true \
    --define:BUILD_DEFS.ENABLE_JSPI=false --define:BUILD_DEFS.ENABLE_BUNDLE_WASM_JS=true \
    --define:BUILD_DEFS.DISABLE_WEBGPU=true --define:BUILD_DEFS.DISABLE_WEBNN=true \
    --define:BUILD_DEFS.IS_ESM=true --define:BUILD_DEFS.ESM_IMPORT_META_URL=import.meta.url \
    '--define:BUILD_DEFS.BUNDLE_FILENAME="ort.wasm.mjs"'
%{__python3} "$component_tools/onnxruntime-web-wasm/prepare-bindings.py" check .
install -d "$component_data/onnxruntime-web-wasm"
install -pm 0644 wasm-build/ort-wasm-simd-threaded.{mjs,wasm} \
    "$component_data/onnxruntime-web-wasm"/
install -pm 0644 wasm-build/ort.wasm.mjs "$component_data/onnxruntime-web-wasm"/
mkdir -p "$component_licenses/onnxruntime-web-wasm"
cp -a rpm-licenses "$component_licenses/onnxruntime-web-wasm"/
)

# zotero-libreoffice-integration
(
    cd "$component_sources/zotero-libreoffice-integration"
%{__python3} "$component_tools/zotero-libreoffice-integration/prepare-extension.py" prepare
classpath=
for library in jackson-core jackson-databind jackson-annotations jna libreoffice/libreoffice; do
    test -f "%{_javadir}/$library.jar"
    classpath="${classpath:+$classpath:}%{_javadir}/$library.jar"
done
javac --release 8 -encoding UTF-8 -cp "$classpath" -d build/bin @build/java-sources.list
epoch=${SOURCE_DATE_EPOCH:-315532802}
if test "$epoch" -lt 315532802; then epoch=315532802; fi
stamp=$(date -u -d "@$epoch" +%%Y-%%m-%%dT%%H:%%M:%%SZ)
jar --create --file build/oxt/Zotero.jar --manifest build/system-manifest.mf \
    --date "$stamp" -C build/bin .
%{__python3} "$component_tools/zotero-libreoffice-integration/prepare-extension.py" archive
install -Dpm 0644 install/Zotero_LibreOffice_Integration.oxt \
    "$component_data/zotero-libreoffice-integration"/Zotero_LibreOffice_Integration.oxt
mkdir -p "$component_licenses/zotero-libreoffice-integration"
cp -a COPYING "$component_licenses/zotero-libreoffice-integration"/
)
