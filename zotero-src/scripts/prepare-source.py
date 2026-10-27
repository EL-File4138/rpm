#!/usr/bin/python3
"""Adapt the pinned Zotero tree for local, serial RPM builds."""

import argparse
from pathlib import Path
import shutil


def replace(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise ValueError(f"Expected one replacement in {path}: {old!r}")
    path.write_text(text.replace(old, new))


def prepare_citeproc_preview(root):
    replace(root / "chrome/content/zotero/xpcom/citeprocRsBridge.js",
            "previewCitationCluster(citation, citationsPre, citationsPost, outputFormat) {",
            """previewCitationCluster(citation, citationsPre, citationsPost, outputFormat) {
			if (outputFormat == 'text') outputFormat = 'plain';""")


def prepare_runtime_cache(root):
    replace(root / "app/scripts/xulrunner_hash",
            'input_string="${platform}-${arch}-${components_hash}|${GECKO_VERSION}|${xulrunner_content}"',
            '''input_string="${platform}-${arch}-${components_hash}|${GECKO_VERSION}|${xulrunner_content}"
# Source-built archives can change without a Gecko version change.
if [[ $platform = "l" ]]; then
    runtime_hash=$(openssl dgst -sha256 "$APP_ROOT_DIR/xulrunner/firefox-$GECKO_VERSION-$arch.tar.xz" | awk '{print $NF}')
    input_string+="|$runtime_hash"
fi''')


def prepare_locales(root):
    (root / "note-editor/webpack.zotero-locale-plugin.js").write_text('''const fs = require('node:fs');
const path = require('node:path');
module.exports = class ZoteroLocalePlugin {
    constructor(options) { this.options = options; }
    apply(compiler) {
        compiler.hooks.beforeRun.tap('ZoteroLocalePlugin', () => {
            const output = path.join(__dirname, 'locales');
            fs.rmSync(output, { recursive: true, force: true });
            for (const locale of this.options.locales) {
                fs.mkdirSync(path.join(output, locale), { recursive: true });
                for (const file of this.options.files) {
                    fs.copyFileSync(
                        path.join(__dirname, '..', 'chrome', 'locale', locale, 'zotero', file),
                        path.join(output, locale, file));
                }
            }
        });
    }
};
''')


def prepare_editor(root):
    configuration = root / "note-editor/webpack.config.js"
    replace(configuration, "minimize: build !== 'dev',",
            "minimize: build !== 'dev' && build !== 'zotero',")
    replace(configuration, "minimizer: build === 'dev' ? [] :",
            "minimizer: (build === 'dev' || build === 'zotero') ? [] :")


def prepare_virtualized(root):
    worker = root / "js-build/babel-worker.js"
    contents = worker.read_text()
    start = contents.index("\t\t// Patch react-virtualized\n")
    end = contents.index("\t\t// Patch single-file\n", start)
    replace(worker, contents[start:end], '''		// Gecko and React 18 fixes are applied to the original sources by the RPM.
		if (comparePaths(sourcefile, 'resource/react-virtualized.js')) {
			if (!contents.includes('/* Zotero source compatibility patches applied. */')
				|| !contents.includes('flushSync')
				|| !contents.includes('http://www.w3.org/1999/xhtml')) {
				throw new Error('Missing source-built React Virtualized compatibility patches');
			}
			transformed = contents;
		}
''')


def prepare_rpm_updates(root):
    replace(root / "app/scripts/fetch_xulrunner", '''	# Prompt if major update is available instead of installing automatically on restart
	replace_line 'if \\(!updateAuto\\) \\{' 'if (update.type == "major") {
      LOG("UpdateService:_selectAndInstallUpdate - prompting because it is a major update");
      AUSTLMY.pingCheckCode(this._pingSuffix, AUSTLMY.CHK_SHOWPROMPT_PREF);
      Services.obs.notifyObservers(update, "update-available", "show-prompt");
      return;
    }
    if (!updateAuto) {' modules/UpdateService.sys.mjs''',
            "\t# Gecko's updater is disabled; application updates are managed by RPM.")


def prepare_disabled_crashreporter(root):
    replace(root / "app/scripts/fetch_xulrunner", '''	# Silence CrashManager "Could not get children of [...]/Crash Reports/events" spam
	replace_line '\\/\\/ Missing events folders are allowed' '\\/\\/ Missing events folders are allowed (silence warning)
        if (ex) return entries;' modules/CrashManager.sys.mjs''',
            "\t# Crash reporting is disabled in the source-built Gecko runtime.")


def prepare(root, data):
    prepare_citeproc_preview(root)
    prepare_runtime_cache(root)
    prepare_locales(root)
    prepare_editor(root)
    prepare_virtualized(root)
    prepare_rpm_updates(root)
    prepare_disabled_crashreporter(root)
    replace(root / "js-build/babel-worker.js",
            "contents.replace('from\\'@monacopilot/core\\'', 'from\\'./monacopilot-core.mjs\\'')",
            '''contents.replace(/from\\s*['"]@monacopilot\\/core['"]/g, 'from "./monacopilot-core.mjs"')''')
    replace(root / "app/scripts/fetch_xulrunner", '''			if [ $arch = "arm64" ]; then
				moz_arch=aarch64
			else
				moz_arch=$arch
			fi
			curl -O "$DOWNLOAD_URL/linux-$moz_arch/en-US/firefox-$GECKO_VERSION.tar.xz"
			# Store local copy of unmodified app
			cp "firefox-$GECKO_VERSION.tar.xz" "$archived_file"''',
            '''			echo "Missing locally built Gecko archive: $archived_file" >&2
			exit 1''')
    replace(root / "app/build.sh", '''		# Use our own updater, because Mozilla's requires updates signed by Mozilla
		check_lfs_file "$CALLDIR/linux/updater.tar.xz"
		tar xf "$CALLDIR/linux/updater.tar.xz" --to-stdout updater-$arch > "$APPDIR/updater"
		chmod 755 "$APPDIR/updater"''', "\t\t# Application updates are managed by RPM.")
    replace(root / "reader/pdfjs/build", "npm ci\n", "# Dependencies were installed offline by the RPM build.\n")
    replace(root / "js-build/js.js", "os.cpus().length", "1")
    build = root / "js-build/build.js"
    replace(build, "const results = await Promise.all([", "const results = [")
    replace(build, "\t\t\t]);\n\n\t\t\tawait writeSignatures", "\t\t\t];\n\n\t\t\tawait writeSignatures")
    for name in ("getBrowserify", "getCopy", "getJS", "getReader", "getDocumentWorker", "getZoteroNoteEditor"):
        replace(build, f"\t\t\t\t{name}(", f"\t\t\t\tawait {name}(")
    for first in ("symlinks", "symlinkDirs"):
        replace(build, f"\t\t\t\tgetSymlinks({first},", f"\t\t\t\tawait getSymlinks({first},")
    replace(build, "...scssFiles.map(scf => getSass(scf, { ignore: ignoreMask }, signatures)),",
            "...(await (async () => { const results = []; for (const scf of scssFiles) "
            "results.push(await getSass(scf, { ignore: ignoreMask }, signatures)); return results; })()),")

    # The three subprojects are built before the root build. Keep upstream's
    # root task interface, but remove both Git and CI artifact dependencies.
    for name, source, target in (
        ("reader", "reader/build/zotero", "reader"),
        ("document-worker", "document-worker/build", "document-worker"),
        ("note-editor", "note-editor/build/zotero", "note-editor"),
    ):
        (root / f"js-build/{name}.js").write_text(f'''const fs = require('fs-extra');
module.exports = async function () {{
    await fs.copy('{source}', 'build/resource/{target}');
    return {{ action: '{name}', count: 1, totalCount: 1, processingTime: 0 }};
}};
''')

    for pdf in (root / "reader/pdfjs/pdf.js", root / "document-worker/pdf.js"):
        for codec in ("openjpeg", "jbig2", "qcms", "quickjs"):
            target = pdf / "external" / codec
            for path in target.glob("*.wasm"):
                path.unlink()
            shutil.copytree(data / "pdfjs-codecs" / codec, target, dirs_exist_ok=True)
    lo = root / "app/modules/zotero-libreoffice-integration"
    shutil.rmtree(lo / "build/lib")
    shutil.copyfile(data / "zotero-libreoffice-integration/Zotero_LibreOffice_Integration.oxt",
                    lo / "install/Zotero_LibreOffice_Integration.oxt")
    prefs = root / "defaults/preferences/rpm.js"
    prefs.write_text('pref("app.update.enabled", false);\npref("app.update.auto", false);\n')
    policies = root / "app/policies.json"
    policies.write_text('{"policies":{"DisableAppUpdate":true}}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--data", type=Path, default=Path("/usr/share"))
    args = parser.parse_args()
    prepare(args.root.resolve(), args.data.resolve())
