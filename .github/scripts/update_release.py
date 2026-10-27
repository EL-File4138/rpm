"""Validate a release notification and update the supported RPM specs."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

import rpm


PACKAGES = {
    "zotero": ("master", ("zotero/zotero.spec",)),
    "xpadneo": (
        "master",
        ("xpadneo/xpadneo/xpadneo.spec", "xpadneo/xpadneo-kmod/xpadneo-kmod.spec"),
    ),
    "aegisub": ("aegisub-next", ("aegisub/aegisub.spec",)),
}
BOT = "github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>"


def normalize_version(package, version):
    if package not in PACKAGES:
        raise ValueError("Unsupported package")
    if not isinstance(version, str) or len(version) > 100:
        raise ValueError("Version must be a string of at most 100 characters")
    pattern = r"v?([0-9]+(?:\.[0-9]+)*"
    if package == "aegisub":
        pattern += r"(?:[-~](?:alpha|beta|rc)[0-9]*(?:\.[0-9]+)*)?"
    match = re.fullmatch(pattern + r")", version)
    if not match:
        raise ValueError("Unsupported version format")
    return match[1].replace("-", "~")


def resolve_event(event_name, event):
    if event_name == "repository_dispatch":
        payload = event.get("client_payload")
    elif event_name == "workflow_dispatch":
        payload = event.get("inputs")
    else:
        raise ValueError("Unsupported event")
    if not isinstance(payload, dict):
        raise ValueError("Expected package and version fields")
    package = payload.get("package")
    if not isinstance(package, str):
        raise ValueError("Package must be a string")
    version = normalize_version(package, payload.get("version"))
    return package, version, PACKAGES[package][0]


def field(text, name):
    matches = list(re.finditer(rf"^{name}:([ \t]+)(\S+)[ \t]*$", text, re.MULTILINE))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {name} field")
    return matches[0]


def update_specs(root, package, version):
    version = normalize_version(package, version)
    updates = []
    for relative in PACKAGES[package][1]:
        path = root / relative
        text = path.read_text()
        current = field(text, "Version")
        comparison = rpm.labelCompare(("0", version, "0"), ("0", current[2], "0"))
        if comparison < 0:
            return False  # A delayed notification must never downgrade either spec.
        if comparison == 0:
            continue
        text = text[:current.start(2)] + version + text[current.end(2):]
        release = field(text, "Release")
        if release[2] != "%autorelease":
            if not re.fullmatch(r"[0-9]+%\{\?dist\}", release[2]):
                raise ValueError(f"Unsupported Release field in {relative}")
            text = text[:release.start(2)] + "1%{?dist}" + text[release.end(2):]
        if not re.search(r"^%autochangelog\s*$", text, re.MULTILINE):
            if release[2] == "%autorelease":
                raise ValueError("Automatic releases require an automatic changelog")
            date = datetime.now(timezone.utc).strftime("%a %b %d %Y")
            entry = f"* {date} {BOT} - {version}-1\n- Update to version {version}.\n\n"
            text, count = re.subn(r"^%changelog\n", lambda m: m[0] + entry, text, flags=re.MULTILINE)
            if count != 1:
                raise ValueError(f"Expected one changelog in {relative}")
        updates.append((path, text))
    # Validate every spec before writing any of them.
    for path, text in updates:
        path.write_text(text)
    return bool(updates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("resolve", "update"))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    if args.command == "resolve":
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        package, version, branch = resolve_event(os.environ["GITHUB_EVENT_NAME"], event)
        outputs = {"package": package, "version": version, "branch": branch}
    else:
        changed = update_specs(args.root, os.environ["PACKAGE"], os.environ["VERSION"])
        outputs = {"changed": str(changed).lower()}
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        for key, value in outputs.items():
            print(f"{key}={value}", file=output)


if __name__ == "__main__":
    main()
