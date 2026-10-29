%define debug_package %{nil}
%define __requires_exclude ^(libfreeblpriv3|liblgpllibs|libmozavcodec|libmozavutil|libmozgtk|libmozsandbox|libmozsqlite3|libmozwayland|libnspr4|libnss3|libnssutil3|libplc4|libplds4|libsmime3|libsoftokn3|libssl3|libxul|libgkcodecs)\.so(\(.*\))?$
%global __provides_exclude_from ^%{_libdir}/%{name}/.*$

Name:		zotero
Version:	10.0.7
Release:	1%{?dist}
Summary:	Zotero desktop application

License:	AGPLv3
URL:		https://www.zotero.org
Source0:	https://download.zotero.org/client/release/%{version}/Zotero-%{version}_linux-x86_64.tar.xz
Source1:        https://raw.githubusercontent.com/zotero/zotero/%{version}/COPYING
Source2:        policies.json
Patch0:	    desktop.patch

ExclusiveArch: x86_64
BuildRequires: desktop-file-utils
BuildRequires: python3
Requires: hicolor-icon-theme

%description
Zotero is a free, easy-to-use tool to help you collect, organize, cite,
and share research.

%prep
%autosetup -n Zotero_linux-x86_64
# Preserve upstream notices without modifying the bundled runtime archives.
mkdir rpm-licenses
cp %{SOURCE1} rpm-licenses/COPYING
%{__python3} - <<'PY'
from pathlib import Path
from zipfile import ZipFile
for filename in ('omni.ja', 'app/omni.ja'):
    with ZipFile(filename) as archive:
        for name in archive.namelist():
            path = Path(name)
            if path.name.startswith(('LICENSE', 'COPYING')) or path.name in ('license.txt', 'license.html', 'OpenH264-license.txt'):
                if path.is_absolute() or '..' in path.parts:
                    raise ValueError(f'Unsafe notice path: {name}')
                destination = Path('rpm-licenses') / filename.replace('/', '-') / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(name))
PY

%build

%install
mkdir -p %{buildroot}{%{_bindir},%{_libdir}/%{name}}
cp -a . %{buildroot}%{_libdir}/%{name}/
rm -rf %{buildroot}%{_libdir}/%{name}/rpm-licenses
ln -s ../%{_lib}/%{name}/%{name} %{buildroot}%{_bindir}/%{name}
install -Dm644 %{SOURCE2} %{buildroot}%{_libdir}/%{name}/distribution/policies.json
install -Dm644 %{buildroot}%{_libdir}/%{name}/%{name}.desktop %{buildroot}/%{_datadir}/applications/%{name}.desktop
install -Dm644 %{buildroot}%{_libdir}/%{name}/icons/icon32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -Dm644 %{buildroot}%{_libdir}/%{name}/icons/icon64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
install -Dm644 %{buildroot}%{_libdir}/%{name}/icons/icon128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
install -Dm644 icons/symbolic.svg %{buildroot}%{_datadir}/icons/hicolor/symbolic/apps/%{name}-symbolic.svg
rm -f %{buildroot}%{_libdir}/%{name}/{zotero.desktop,set_launcher_icon}

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
test "$(readlink %{buildroot}%{_bindir}/%{name})" = "../%{_lib}/%{name}/%{name}"
%{__python3} - <<'PY'
import json
from pathlib import Path
root = Path('%{buildroot}%{_libdir}/%{name}')
assert json.loads((root / 'distribution/policies.json').read_text())['policies']['DisableAppUpdate'] is True
assert (root / 'app/omni.ja').is_file()
assert not (root / 'set_launcher_icon').exists()
assert Path('rpm-licenses/COPYING').is_file()
PY

%files
%license rpm-licenses/*
%{_bindir}/%{name}
%{_libdir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/zotero.png
%{_datadir}/icons/hicolor/symbolic/apps/zotero-symbolic.svg

%changelog
* Thu Oct 29 2026 github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com> - 10.0.7-1
- Update to version 10.0.7.

* Mon Oct 26 2026 Matrew File <elfile4138@elfile4138.moe> - 10.0.3-2
- Disable application self-updates using the supported enterprise policy.
- Preserve upstream notices and correct private dependency filtering.
- Use a relative launcher link and validate desktop integration.

* Sat Jan 24 2026 Matrew File <elfile4138@elfile4138.moe> - 8.0
- Upstream update to Zotero 8.
* Sun Oct 13 2024 Matrew File <elfile4138@elfile4138.moe> - 7.0.7
- Upstream update to Zotero 7.
- Fix Spec error.
* Mon Nov 13 2023 Matrew File <elfile4138@outlook.com> - 6.0.30
- Upstream update.
* Wed Mar 22 2023 Matrew File <elfile4138@outlook.com> - 6.0.23
- Initial package.
