# typescript-source-js
(
    cd "$component_sources/typescript-source-js"
node "$component_tools/typescript-source-js/check.cjs" "$component_data/typescript-source-js"
)

# react-js
(
    cd "$component_sources/react-js"
node "$component_tools/react-js/check.cjs" build/node_modules
)

# prop-types-js
(
    cd "$component_sources/prop-types-js"
node "$component_tools/prop-types-js/check.cjs" "$component_data/prop-types-js"
)

# react-autosuggest-js
(
    cd "$component_sources/react-autosuggest-js"
node "$component_tools/react-autosuggest-js/check.cjs" "$component_data/react-autosuggest-js"/autosuggest.min.js "$component_data/react-js"
)

# react-virtualized-js
(
    cd "$component_sources/react-virtualized-js"
node "$component_tools/react-virtualized-js/check.cjs" "$component_data/react-virtualized-js"/react-virtualized.js "$component_data/react-js"
)

# react-intl-js
(
    cd "$component_sources/react-intl-js"
node "$component_tools/react-intl-js/check.cjs" "$component_data/react-intl-js" "$component_data/react-js"
)

# ace-js
(
    cd "$component_sources/ace-js"
node "$component_tools/ace-js/check.cjs" "$component_data/ace-js"
)

# pako-js
(
    cd "$component_sources/pako-js"
node "$component_tools/pako-js/check.cjs" "$component_data/pako-js"
)

# katex-js
(
    cd "$component_sources/katex-js"
node "$component_tools/katex-js/check.mjs" "$component_data/katex-js"
%{__python3} "$component_tools/katex-js/check-fonts.py" "$component_data/katex-js"/fonts
)

# mathjax-chtml-js
(
    cd "$component_sources/mathjax-chtml-js"
node "$component_tools/mathjax-chtml-js/check.cjs" "$component_data/mathjax-chtml-js"
)

# monaco-editor-js
(
    cd "$component_sources/monaco-editor-js"
node "$component_tools/monaco-editor-js/check.cjs" "$component_data/monaco-editor-js"
%{__python3} "$component_tools/monaco-editor-js/check-font.py" "$component_data/monaco-editor-js"/vs/base/browser/ui/codicons/codicon/codicon.ttf
)

# monacopilot-js
(
    cd "$component_sources/monacopilot-js"
node "$component_tools/monacopilot-js/check.mjs" dist
)

# source-map-mappings-wasm
(
    cd "$component_sources/source-map-mappings-wasm"
node "$component_tools/source-map-mappings-wasm/check.mjs" "$component_data/source-map-mappings-wasm"/mappings.wasm
)

# citeproc-rs-wasm
(
    cd "$component_sources/citeproc-rs-wasm"
node "$component_tools/citeproc-rs-wasm/check-bindings.cjs" bindings
)

# csl-validator-wasm
(
    cd "$component_sources/csl-validator-wasm"
cp csl-validator.mjs worker.mjs "$component_tools/csl-validator-wasm/check-validator.mjs" dist/
node dist/check-validator.mjs
)

# pdfjs-codecs
(
    cd "$component_sources/pdfjs-codecs"
node "$component_tools/pdfjs-codecs/check-codecs.mjs" dist
)

# onnxruntime-web-wasm
(
    cd "$component_sources/onnxruntime-web-wasm"
native-protobuf/protoc --proto_path=wasm-build/_deps/onnx-src \
    --encode=onnx.ModelProto onnx/onnx.proto < "$component_tools/onnxruntime-web-wasm/identity.prototxt" > identity.onnx
node "$component_tools/onnxruntime-web-wasm/check-runtime.mjs" wasm-build identity.onnx
node "$component_tools/onnxruntime-web-wasm/check-bindings.mjs" wasm-build identity.onnx
)

# zotero-libreoffice-integration
(
    cd "$component_sources/zotero-libreoffice-integration"
%{__python3} "$component_tools/zotero-libreoffice-integration/prepare-extension.py" check
)
