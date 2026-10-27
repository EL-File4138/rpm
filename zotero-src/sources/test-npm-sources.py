#!/usr/bin/python3
"""Regression checks for pinned archives and offline npm relocation."""

import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPOSITORY = Path(__file__).resolve().parents[1]
prepare = load('prepare', REPOSITORY / 'sources/prepare-npm-sources.py')
installer = load('installer', REPOSITORY / 'scripts/install-npm-offline.py')


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        self.archives = self.root / 'archives'
        self.url = 'https://codeload.github.com/example/dependency/tar.gz/' + 'a' * 40
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode='w:gz') as archive:
            contents = json.dumps({'name': 'dependency', 'version': '1.0.0'}).encode()
            member = tarfile.TarInfo('package/package.json')
            member.size = len(contents)
            archive.addfile(member, io.BytesIO(contents))
        self.payload = payload.getvalue()
        self.integrity = 'sha512-' + base64.b64encode(hashlib.sha512(self.payload).digest()).decode()
        self.manifest = {'name': 'fixture', 'version': '1.0.0',
                         'dependencies': {'dependency': self.url}}
        self.lock = {'lockfileVersion': 3, 'packages': {
            '': self.manifest.copy(),
            'node_modules/dependency': {'version': '1.0.0', 'resolved': self.url,
                                        'integrity': self.integrity}}}
        self.write_project()

    def write_project(self):
        (self.project / 'package.json').write_text(json.dumps(self.manifest))
        (self.project / 'package-lock.json').write_text(json.dumps(self.lock))

    def prepare_archives(self):
        with patch.object(prepare.urllib.request, 'urlopen', return_value=io.BytesIO(self.payload)):
            prepare.prepare([self.project / 'package-lock.json'], self.archives, 1)

    def test_pinned_url_installs_offline(self):
        self.prepare_archives()
        installer.install(self.project, self.archives)
        installed = json.loads((self.project / 'node_modules/dependency/package.json').read_text())
        self.assertEqual(installed['version'], '1.0.0')
        manifest = json.loads((self.project / 'package.json').read_text())
        self.assertTrue(manifest['dependencies']['dependency'].startswith('file:'))

    def test_unpinned_or_unhashed_url_rejected_before_download(self):
        for url, integrity in ((self.url.replace('a' * 40, 'main'), self.integrity),
                               (self.url, None)):
            with self.subTest(url=url, integrity=integrity):
                package = self.lock['packages']['node_modules/dependency']
                package.update(resolved=url, integrity=integrity)
                self.write_project()
                with patch.object(prepare.urllib.request, 'urlopen') as download:
                    with self.assertRaisesRegex(ValueError, 'Unsupported package origin'):
                        prepare.prepare([self.project / 'package-lock.json'], self.archives, 1)
                    download.assert_not_called()

    def test_corrupted_archive_rejected_before_npm_or_manifest_changes(self):
        self.prepare_archives()
        next(self.archives.glob('*.tgz')).write_bytes(b'corrupted')
        before = (self.project / 'package-lock.json').read_bytes()
        with patch.object(installer.subprocess, 'run') as npm:
            with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
                installer.install(self.project, self.archives)
            npm.assert_not_called()
        self.assertEqual((self.project / 'package-lock.json').read_bytes(), before)
        self.assertEqual(json.loads((self.project / 'package.json').read_text()), self.manifest)

    def test_manifest_disagreement_rejected(self):
        self.prepare_archives()
        self.manifest['dependencies'] = {'dependency': 'unexpected'}
        (self.project / 'package.json').write_text(json.dumps(self.manifest))
        with patch.object(installer.subprocess, 'run') as npm:
            with self.assertRaisesRegex(ValueError, 'Manifest and lockfile disagree'):
                installer.install(self.project, self.archives)
            npm.assert_not_called()


if __name__ == '__main__':
    unittest.main()
