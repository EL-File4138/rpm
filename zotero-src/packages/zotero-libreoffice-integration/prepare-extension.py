#!/usr/bin/python3
"""Prepare and validate the OXT; javac and jar are invoked by the spec."""

import argparse
import io
import os
from pathlib import Path
import shutil
import time
import xml.etree.ElementTree as ET
import zipfile


LIBRARIES = ('jackson-core', 'jackson-databind', 'jackson-annotations', 'jna')
ARCHIVE = Path('install/Zotero_LibreOffice_Integration.oxt')


def check():
    with zipfile.ZipFile(ARCHIVE) as archive:
        jars = [name for name in archive.namelist() if name.endswith('.jar')]
        if jars != ['Zotero.jar']:
            raise ValueError(f'Unexpected bundled jars: {jars}')
        with zipfile.ZipFile(io.BytesIO(archive.read('Zotero.jar'))) as jar:
            if 'org/zotero/integration/ooo/comp/RegistrationHandler.class' not in jar.namelist():
                raise ValueError('Missing UNO registration class')
            manifest = jar.read('META-INF/MANIFEST.MF').decode().replace('\r\n ', '')
            for name in LIBRARIES:
                if f'file:/usr/share/java/{name}.jar' not in manifest:
                    raise ValueError(f'Missing system dependency: {name}')
        description = ET.fromstring(archive.read('description.xml'))
        if description.find('{http://openoffice.org/extensions/description/2006}update-information') is not None:
            raise ValueError('Extension must be updated by RPM')


def prepare():
    source = Path('build/source')
    classes = Path('build/bin')
    classes.mkdir(parents=True, exist_ok=True)
    sources = sorted(source.rglob('*.java'))
    if not sources:
        raise ValueError('No Java source files')
    Path('build/java-sources.list').write_text(''.join(f'{path}\n' for path in sources))
    for item in sorted(source.rglob('*')):
        if item.is_file() and item.suffix != '.java':
            destination = classes / item.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item, destination)
    Path('build/system-manifest.mf').write_text(
        'Manifest-Version: 1.0\n'
        'RegistrationClassName: org.zotero.integration.ooo.comp.RegistrationHandler\n'
        'Class-Path: ' + '\n  '.join(f'file:/usr/share/java/{name}.jar' for name in LIBRARIES) + '\n\n',
        encoding='utf-8',
    )


def archive():
    oxt = Path('build/oxt')
    description = oxt / 'description.xml'
    namespace = 'http://openoffice.org/extensions/description/2006'
    ET.register_namespace('', namespace)
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    tree = ET.parse(description)
    root = tree.getroot()
    for update in root.findall(f'{{{namespace}}}update-information'):
        root.remove(update)
    tree.write(description, encoding='UTF-8', xml_declaration=True)
    shutil.rmtree(oxt / 'external_jars', ignore_errors=True)
    epoch = max(315532802, int(os.environ.get('SOURCE_DATE_EPOCH', '315532802')))
    ARCHIVE.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED) as output:
        for item in sorted(oxt.rglob('*')):
            if item.is_file():
                info = zipfile.ZipInfo(item.relative_to(oxt).as_posix(), time.gmtime(epoch)[:6])
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                output.writestr(info, item.read_bytes())
    check()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'archive', 'check'))
    globals()[parser.parse_args().action]()
