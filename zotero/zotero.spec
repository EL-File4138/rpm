%define debug_package %{nil}
%define __requires_exclude ^(libclearkey|libfreeblpriv3|liblgpllibs|libmozavcodec|libmozavutil|libmozgtk|libmozsandbox|libmozsqlite3|libmozwayland|libnspr4|libnss3|libnssckbi|libnssdbm3|libnssutil3|libplc4|libsmime3|libsoftokn3|libssl3|libxul)\.so
%global __provides_exclude_from %{_libdir}/%{name}

Name:		zotero
Version:	7.0.11
Release:	1%{?dist}
Summary:	Zotero desktop application

License:	AGPLv3
URL:		https://www.zotero.org
Source0:	https://download.zotero.org/client/release/%{version}/Zotero-%{version}_linux-x86_64.tar.bz2
Patch0:	    desktop.patch

ExclusiveArch: x86_64

%description
Zotero is a free, easy-to-use tool to help you collect, organize, cite, and share research.

%prep
%autosetup -n Zotero_linux-x86_64

%build

%install
mkdir -p %{buildroot}{%{_bindir},%{_libdir}/%{name}}
cp -rf %{_builddir}/Zotero_linux-x86_64/* %{buildroot}%{_libdir}/%{name}/
ln -sf %{_libdir}/%{name}/%{name} %{buildroot}%{_bindir}/%{name}
install -Dm644 %{buildroot}%{_libdir}/%{name}/%{name}.desktop %{buildroot}/%{_datadir}/applications/%{name}.desktop
install -Dm644 %{buildroot}%{_libdir}/%{name}/icons/icon32.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -Dm644 %{buildroot}%{_libdir}/%{name}/icons/icon64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
install -Dm644 %{buildroot}%{_libdir}/%{name}/icons/icon128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png

%files
%doc
%{_bindir}/%{name}
%{_libdir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/zotero.png

%changelog
* Sun Oct 13 2024 Matrew File <elfile4138@elfile4138.moe> - 7.0.7
- Upstream update to Zotero 7.
- Fix Spec error.
* Mon Nov 13 2023 Matrew File <elfile4138@outlook.com> - 6.0.30
- Upstream update.
* Wed Mar 22 2023 Matrew File <elfile4138@outlook.com> - 6.0.23
- Initial package.
