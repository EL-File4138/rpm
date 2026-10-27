#!/usr/bin/python3
"""Build React 18's browser and CommonJS distributions from release sources."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def build(root, dependencies, plugin, esbuild):
    if '18.3.1' not in (root / 'packages/shared/ReactVersion.js').read_text():
        raise ValueError('Expected React 18.3.1 sources')
    manifest_path = root / 'package.json'
    manifest = json.loads(manifest_path.read_text())
    # This release predates npm's structured devEngines schema.
    manifest.pop('devEngines', None)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    versions = json.loads(subprocess.check_output([
        'node', '-p', 'JSON.stringify(require("./ReactVersions").stablePackages)',
    ], cwd=root, text=True))
    for name, version in versions.items():
        path = root / 'packages' / name / 'package.json'
        package = json.loads(path.read_text())
        package['version'] = version
        for section in ('dependencies', 'peerDependencies'):
            for dependency in package.get(section, {}):
                if dependency in versions:
                    package[section][dependency] = '^' + versions[dependency]
        path.write_text(json.dumps(package, indent=2) + '\n')
    modules = root / 'node_modules'
    modules.mkdir(exist_ok=True)
    for package in dependencies.iterdir():
        destination = modules / package.name
        if not destination.exists():
            destination.symlink_to(package, target_is_directory=True)
    for package in (root / 'packages').iterdir():
        if (package / 'package.json').exists():
            destination = modules / package.name
            if destination.is_symlink():
                destination.unlink()
            destination.symlink_to(package, target_is_directory=True)
    shutil.copyfile(plugin, root / 'scripts/rollup/plugins/closure-plugin.js')
    environment = os.environ | {
        'RELEASE_CHANNEL': 'stable', 'RPM_ESBUILD': esbuild,
        'GOMAXPROCS': '1', 'UV_THREADPOOL_SIZE': '1',
        'NODE_OPTIONS': '--max-old-space-size=1400',
        'npm_config_offline': 'true', 'npm_config_ignore_scripts': 'true',
        'npm_config_audit': 'false', 'npm_config_fund': 'false',
        'npm_config_cache': str(root / 'rpm-npm-cache'),
    }
    subprocess.run([
        'node', 'scripts/rollup/build.js',
        'react/index,react/jsx,react.shared-subset,react-dom/index,react-dom/test-utils,'
        'react-dom-server,react-is/index,scheduler/',
        '--type=UMD_DEV,UMD_PROD,NODE_DEV,NODE_PROD,NODE_PROFILING',
    ], cwd=root, env=environment, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('dependencies', type=Path)
    parser.add_argument('plugin', type=Path)
    parser.add_argument('--esbuild', default='esbuild')
    args = parser.parse_args()
    build(args.root.resolve(), args.dependencies.resolve(), args.plugin.resolve(), args.esbuild)
