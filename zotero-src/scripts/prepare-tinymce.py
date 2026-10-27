#!/usr/bin/python3
"""Use readable release files while preserving Zotero's exact TinyMCE changes."""

import argparse
from pathlib import Path
import tarfile


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one TinyMCE link replacement: {old!r}")
    return text.replace(old, new)


def prepare(root, release, paste_release, check=False):
    directory = root / 'resource/tinymce'
    replacements = []
    with tarfile.open(release) as current, tarfile.open(paste_release) as paste:
        for target in sorted(directory.rglob('*.min.js')):
            relative = target.relative_to(directory).as_posix()
            archive = paste if relative == 'plugins/paste/plugin.min.js' else current
            expected = archive.extractfile('package/' + relative).read()
            readable = archive.extractfile('package/' + relative.replace('.min.js', '.js')).read()
            if relative == 'plugins/link/plugin.min.js':
                # These are the only changes from the 4.9.4 release minified file.
                # Compare the complete result before applying equivalent changes
                # to its readable counterpart; never silently drop Zotero patches.
                expected = once(expected.decode(), '!/^\\w+:/i.test(r)',
                                '!/^\\w+:|^#/i.test(r)')
                expected = once(expected, 'else s(e.href)',
                                'else t.execCommand("ZoteroLinkClick", false, e.href)')
                expected = expected.encode()
                readable = once(readable.decode(), '!/^\\w+:/i.test(href)',
                                '!/^\\w+:|^#/i.test(href)')
                readable = once(readable, 'OpenUrl.open(a.href);',
                                'editor.execCommand("ZoteroLinkClick", false, a.href);').encode()
            if target.read_bytes() != (readable if check else expected):
                raise ValueError(f"Unrecognized TinyMCE customization: {relative}")
            replacements.append((target, readable))
    expected_paths = {'tinymce.min.js', 'themes/modern/theme.min.js'} | {
        f'plugins/{name}/plugin.min.js' for name in
        ('autolink', 'code', 'contextmenu', 'directionality', 'link', 'lists',
         'nonbreaking', 'paste', 'searchreplace', 'textcolor')}
    if {path.relative_to(directory).as_posix() for path, _ in replacements} != expected_paths:
        raise ValueError('Unexpected TinyMCE runtime file inventory')
    # Keep filenames: the upstream loader explicitly requests *.min.js.
    # Validate every input before writing any replacement.
    if not check:
        for target, readable in replacements:
            target.write_bytes(readable)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('release', type=Path)
    parser.add_argument('paste_release', type=Path)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    prepare(arguments.root, arguments.release, arguments.paste_release, check=arguments.check)
