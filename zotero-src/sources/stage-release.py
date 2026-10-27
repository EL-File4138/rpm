#!/usr/bin/python3
"""Stage reviewed release inputs, overlay local packaging, and produce an SRPM."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request


def standalone_spec(root, target):
    """Inline packaging fragments without expanding RPM or shell macros."""
    sources = {}

    def inline(text):
        result = []
        for line in text.splitlines(keepends=True):
            declaration = re.match(r'^Source(\d+):\s+(\S+)', line)
            if declaration:
                original = declaration[2].partition('#/')[0]
                sources[declaration[1]] = root / ('zotero.spec' if original == '../zotero.spec' else original)
            include = re.fullmatch(r'%include %\{SOURCE(\d+)\}\s*', line)
            if include:
                result.append(inline(sources[include[1]].read_text()))
            elif line.startswith('%include'):
                raise ValueError(f'Unsupported spec include: {line.strip()}')
            else:
                result.append(line)
        return ''.join(result)

    return inline((root / target / 'zotero-src.spec').read_text())


def stage(root, target, output):
    manifest = json.loads((root / 'sources/release-inputs.json').read_text())
    recipe = (root / 'zotero.spec').read_text()
    version = re.search(r'^Version:\s+(\S+)', recipe, re.M)[1]
    if version != manifest['version']:
        raise ValueError('Release inputs do not match the requested version')
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        seed = work / 'inputs.src.rpm'
        with urllib.request.urlopen(manifest['url'], timeout=180) as response, seed.open('wb') as stream:
            shutil.copyfileobj(response, stream)
        with seed.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != manifest['sha256']:
                raise ValueError('Release input SRPM checksum mismatch')
        sources = work / 'SOURCES'
        sources.mkdir()
        archive = work / 'inputs.cpio'
        with archive.open('wb') as stream:
            subprocess.run(['rpm2cpio', str(seed)], stdout=stream, check=True)
        with archive.open('rb') as stream:
            subprocess.run(['cpio', '-idm', '--no-absolute-filenames'], stdin=stream, cwd=sources, check=True)
        shutil.copyfile(root / 'zotero.spec', sources / 'zotero-common.inc')
        for fragment in (root / 'spec').glob('*.inc'):
            shutil.copyfile(fragment, sources / fragment.name)
        fedora = '44' if target == 'f44' else '46'
        spec = root / target / 'zotero-src.spec'
        defines = ['--define', f'_sourcedir {sources}', '--define', f'fedora {fedora}',
                   '--define', f'dist .fc{fedora}']
        expanded = subprocess.check_output(['rpmspec', '--parse', *defines, str(spec)], text=True)
        for value in re.findall(r'^Source\d+:\s+(\S+)', expanded, re.M):
            original, _, alias = value.partition('#/')
            name = alias or original.rsplit('/', 1)[-1]
            local = root / original
            if original == '../zotero.spec':
                local = root / 'zotero.spec'
            if local.is_file():
                shutil.copyfile(local, sources / name)
            elif not (sources / name).is_file():
                raise FileNotFoundError(f'Unreviewed release input: {value}')
        spec = work / 'zotero-src.spec'
        spec.write_text(standalone_spec(root, target))
        subprocess.run(['rpmbuild', '-bs', *defines, '--define', f'_topdir {work}',
                         '--define', f'_srcrpmdir {output.resolve()}', str(spec)], check=True)
        release = re.search(r'^Release:\s+(\d+)', recipe, re.M)[1]
        artifact = output / f'zotero-src-{version}-{release}.fc{fedora}.src.rpm'
        members = subprocess.check_output(['rpm', '-qpl', str(artifact)], text=True).splitlines()
        if [name for name in members if name.endswith('.spec')] != ['zotero-src.spec']:
            raise ValueError('Source RPM must contain exactly one target spec file')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('f44', 'rawhide'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    stage(Path(__file__).resolve().parents[1], args.target, args.output)
