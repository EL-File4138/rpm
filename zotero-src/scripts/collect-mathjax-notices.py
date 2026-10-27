#!/usr/bin/python3
"""Preserve MathJax v3 TeX font notices alongside the complete OFL text."""
import argparse
from pathlib import Path

from fontTools.ttLib import TTFont


def collect(fonts, license_template, destination):
    text = license_template.read_text()
    heading = 'SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007'
    start = text.index(heading)
    license_text = text[start:]
    if not all(section in license_text for section in
               ('PERMISSION & CONDITIONS', 'TERMINATION', 'DISCLAIMER')):
        raise ValueError('Incomplete OFL text')
    records = []
    paths = sorted(fonts.glob('*.woff'))
    if len(paths) != 23:
        raise ValueError(f'Expected 23 MathJax TeX fonts, found {len(paths)}')
    for path in paths:
        with TTFont(path) as font:
            notices = sorted({record.toUnicode() for record in font['name'].names
                              if record.nameID in (0, 13, 14)})
        if not any('Copyright' in notice for notice in notices):
            raise ValueError(f'Missing copyright: {path.name}')
        records.append(path.name + '\n' + '\n'.join(notices))
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'FONT-NOTICES.txt').write_text('\n\n'.join(records) + '\n')
    (destination / 'OFL-1.1.txt').write_text(license_text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fonts', type=Path)
    parser.add_argument('license_template', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    collect(args.fonts, args.license_template, args.destination)
