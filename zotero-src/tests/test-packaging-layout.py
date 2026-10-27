"""Keep all repository-local build inputs within the Zotero packaging tree."""
from pathlib import Path
import hashlib
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PackagingLayoutTest(unittest.TestCase):
    def test_binaryen_private_library_lookup_and_hardening(self):
        recipe = (ROOT / 'packages/binaryen125/binaryen125.spec').read_text()
        self.assertIn('-DCMAKE_INSTALL_LIBDIR=lib', recipe)
        self.assertIn('export CXXFLAGS="%{build_cxxflags} -Wno-error=maybe-uninitialized"', recipe)
        check = recipe.split('\n%check\n', 1)[1].split('\n%files', 1)[0]
        self.assertIn('/binaryen125/lib/libbinaryen.so', check)
        self.assertIn('unset LD_LIBRARY_PATH', check)
        self.assertIn('/binaryen125/bin/wasm-opt --version', check)

    def test_repack_and_source_packages_conflict(self):
        source = (ROOT / 'zotero.spec').read_text()
        binary = (ROOT.parent / 'zotero/zotero.spec').read_text()
        self.assertRegex(source, r'(?m)^Name:\s+zotero-src$')
        self.assertRegex(source, r'(?m)^Conflicts:\s+zotero$')
        self.assertNotRegex(binary, r'(?m)^Conflicts:\s+zotero-src$')
        self.assertIn('download.zotero.org/client/release/', binary)

    def test_warning_fixes_preserve_shared_source_and_relative_links(self):
        sources = (ROOT / 'spec/components-sources.inc').read_text()
        prep = (ROOT / 'spec/components-prep.inc').read_text()
        self.assertNotIn('Source68:', sources)
        self.assertNotIn('Source82:', sources)
        self.assertNotIn('%{SOURCE68}', prep)
        self.assertNotIn('%{SOURCE82}', prep)
        source = (ROOT / 'zotero.spec').read_text()
        self.assertIn('ln -s ../%{_lib}/zotero/zotero', source)

    def test_renamed_extension_replaces_previous_source_build_subpackage(self):
        source = (ROOT / 'zotero.spec').read_text()
        extension = source.split('%package libreoffice-integration\n', 1)[1].split('%description', 1)[0]
        self.assertIn('Provides:       zotero-libreoffice-integration = %{version}-%{release}', extension)
        self.assertIn('Obsoletes:      zotero-libreoffice-integration < 10.0.3-2', extension)

    def test_shipped_translator_and_legacy_css_licenses_are_preserved(self):
        recipe = (ROOT / 'zotero.spec').read_text()
        license_line = next(line for line in recipe.splitlines() if line.startswith('License:'))
        self.assertIn('GPL-3.0-only', license_line)
        self.assertIn('LGPL-2.1-only', license_line)
        self.assertIn(' AND W3C AND ', license_line)
        self.assertIn('cp chrome/content/zotero/xpcom/translate/src/rdf/rdfparser.js rpm-licenses/tabulator-rdf/', recipe)
        self.assertIn('cp %{SOURCE37} rpm-licenses/translators/GPL-3.0.txt', recipe)
        self.assertIn('rpm-licenses/legacy-preferences/$platform', recipe)
        self.assertIn('app/assets/mac/chrome/skin/preferences/preferences.css', recipe)
        self.assertIn('app/assets/$platform/skin/preferences/preferences.css', recipe)

    def test_csl_locale_license_and_attribution_are_packaged(self):
        recipe = (ROOT / 'zotero.spec').read_text()
        license_line = next(line for line in recipe.splitlines() if line.startswith('License:'))
        self.assertIn('CC-BY-SA-3.0', license_line)
        self.assertIn('CC0-1.0', license_line)
        install = recipe.split('\n%install\n', 1)[1].split('\n%check\n', 1)[0]
        self.assertIn('cp chrome/content/zotero/locale/csl/README.md rpm-licenses/csl-locales/', install)
        self.assertIn('cp reader/pdfjs/pdf.js/external/iccs/LICENSE rpm-licenses/pdf-icc/', install)

    def test_review_dependency_and_license_source_corrections(self):
        recipe = (ROOT / 'zotero.spec').read_text()
        requirements = re.findall(r'^BuildRequires:\s*(\S+)', recipe, re.M)
        self.assertNotIn('yasm', requirements)
        self.assertIn('nasm', requirements)
        self.assertRegex(recipe, r'(?m)^Source27:\s+sources/OFL.txt$')
        self.assertEqual(hashlib.sha256((ROOT / 'sources/OFL.txt').read_bytes()).hexdigest(),
                         '1d361a8f8e8ce6e68457dcd93fb56e162e6baa3bbb7e7573a290d44399f6b57e')

    def test_local_inputs_exist_and_do_not_escape_zotero(self):
        for recipe in list(ROOT.rglob('*.spec')) + list((ROOT / 'spec').glob('*.inc')):
            for line in recipe.read_text().splitlines():
                match = re.match(r'(?:Source|Patch)\d*:\s+(\S+)', line)
                if not match:
                    continue
                value = match[1].split('#/', 1)[0]
                if '://' in value or '%{' in value:
                    continue
                # Exported source archives are supplied when preparing an SRPM.
                if value.endswith(('.tar.xz', '.tar.gz', '.tgz', '.crate', '.zip')):
                    continue
                base = ROOT if recipe.suffix == '.inc' else recipe.parent
                path = (base / value).resolve()
                self.assertTrue(path.is_relative_to(ROOT), (recipe, value))
                self.assertTrue(path.is_file(), (recipe, value))

    def test_main_build_commands_are_in_the_spec(self):
        recipe = (ROOT / 'zotero.spec').read_text()
        build = recipe.split('\n%build\n', 1)[1].split('\n%install\n', 1)[0]
        for command in ('python3.11 mach build', 'python3.11 mach package',
                        'npm run build:zotero', 'bash app/build.sh',
                        '%{_bindir}/esbuild "src/$entry"'):
            self.assertIn(command, build)
        for helper in ('prepare-gecko.py', 'prepare-application.py', 'editor-source-inputs.py'):
            self.assertNotIn('subprocess', (ROOT / 'scripts' / helper).read_text())

    def test_rawhide_libclang_matches_compatibility_rpm_layout(self):
        recipe = (ROOT / 'zotero.spec').read_text()
        self.assertIn('export LIBCLANG_PATH="%{_libdir}/llvm22/lib64"', recipe)
        self.assertIn('--with-libclang-path="${LIBCLANG_PATH:-/usr/lib64}"',
                      (ROOT / 'config/gecko.mozconfig').read_text())

    def test_private_components_are_not_build_requires(self):
        recipe = (ROOT / 'zotero.spec').read_text()
        metadata = (ROOT / 'spec/components-metadata.inc').read_text()
        requirements = re.findall(r'^BuildRequires:\s*(\S+)', recipe + metadata, re.M)
        for package in (ROOT / 'packages').iterdir():
            if package.name not in ('emscripten-core', 'wasm-bindgen-cli', 'wasi-cxx-runtime', 'binaryen125'):
                self.assertNotIn(package.name, requirements)
        self.assertIn('%files libreoffice-integration', recipe)
        self.assertNotIn('%{_datadir}/react-js', (ROOT / 'spec/components-build.inc').read_text())

    def test_component_compiler_drivers_are_in_the_spec_fragment(self):
        build = (ROOT / 'spec/components-build.inc').read_text()
        for command in ('emcmake cmake', 'cargo build --frozen',
                        'javac --release 8', 'jar --create',
                        'node build-core.cjs', 'emconfigure ./configure'):
            self.assertIn(command, build)
        for helper in ('build-wasm.py', 'build-codecs.py', 'build-validator.sh', 'build-extension.py'):
            self.assertNotIn(helper, build)
        for component, helper in (('onnxruntime-web-wasm', 'prepare-bindings.py'),
                                  ('zotero-libreoffice-integration', 'prepare-extension.py')):
            self.assertNotIn('subprocess', (ROOT / 'packages' / component / helper).read_text())


if __name__ == '__main__':
    unittest.main()
