#!/usr/bin/python3
"""Generate Zotero's citeproc bindings from a locally compiled WASM module."""

import argparse
from pathlib import Path
import subprocess


def build(wasm, output):
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "wasm-bindgen", str(wasm), "--target", "no-modules", "--out-dir",
        str(output), "--out-name", "citeproc_rs_wasm",
    ], check=True)
    binary = output / "citeproc_rs_wasm_bg.wasm"
    subprocess.run(["wasm-opt", "-g", "-O3", str(binary), "-o", str(binary)], check=True)
    glue = output / "citeproc_rs_wasm.js"
    text = glue.read_text().replace("CITEPROC_RS_ZOTERO_GLOBAL", "Zotero.CiteprocRs")
    # Gecko's privileged module document has no currentScript property.
    guard = "typeof document !== 'undefined' && document.currentScript !== null"
    if text.count(guard) != 1:
        raise ValueError("Unexpected wasm-bindgen currentScript guard")
    text = text.replace(guard, "typeof document !== 'undefined' && document.currentScript != null")
    text += '\nmodule.exports = wasm_bindgen;\n'
    text += ('if (typeof Zotero !== "undefined" && typeof Zotero.CiteprocRs !== "undefined") '
             '{ Object.assign(Zotero.CiteprocRs, wasm_bindgen); }\n')
    glue.write_text(text)
    source = Path("crates/wasm/src/js")
    helper = (source / "include.js").read_text().replace("export class ", "class ")
    helper += "\n" + (source / "zotero.js").read_text()
    (output / "citeproc_rs_wasm_include.js").write_text(helper)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wasm", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.wasm, args.output)
