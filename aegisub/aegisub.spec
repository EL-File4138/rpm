%global         gituser         arch1t3cht
%global         gitname         Aegisub
%global         commit          9c9a0a8dfbb1e31da50c0791cdaf1f2ae590a586
%global         shortcommit     %(c=%{commit}; echo ${c:0:8})
%global         gitdate         20251218

Name:           aegisub
Version:        3.4.9.%{gitdate}
Release:        1%{?dist}
Summary:        Tool for creating and modifying subtitles
License:        BSD and MIT and MPLv1.1
URL:            https://github.com/%{gituser}/%{gitname}

# Placebo: Requires standard dist tarball, generate via `meson dist --include-subprojects -C build` upstream.
Source0:        %{url}/archive/%{commit}/%{gitname}-%{shortcommit}.tar.gz

ExcludeArch:    %{power64} %{ix86} %{arm}

BuildRequires:  boost-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  libappstream-glib
BuildRequires:  libglvnd-devel
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  wxGTK-devel
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(ffms2)
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(gmock)
BuildRequires:  pkgconfig(gtest)
BuildRequires:  pkgconfig(hunspell)
BuildRequires:  pkgconfig(icu-i18n)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(libass)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(luajit)
BuildRequires:  pkgconfig(openal)
BuildRequires:  pkgconfig(portaudio-2.0)
BuildRequires:  pkgconfig(uchardet)

Requires: hicolor-icon-theme

# Heavily modified upon the original project
Provides: bundled(cajun-jsonapi) = 2.0.1
# Major ABI change making patching out impossible
Provides: bundled(lua-lpeg) = 0.1.0
# Discontinued project, not included in Fedora Package registry
Provides: bundled(lua-luabins) = 0.3

%description
Aegisub is an advanced subtitle editor which assists in the creation of subtitles,
timing, and editing of subtitle files. It supports a wide range of formats and
provides powerful visual typesetting tools.
This is arch1t3cht's fork, and is actively following for the most recent development
that has a CI success.

%prep
# Requires standard dist tarball, generate via `meson dist --include-subprojects -C build` upstream.
%autosetup -n %{gitname}-%{shortcommit} -p1

%build
%meson -Denable_update_checker=false
%meson_build

%install
%meson_install

%check
%meson_test

%find_lang %{name}

desktop-file-validate %{buildroot}%{_datadir}/applications/org.%{name}.%{gitname}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/org.%{name}.%{gitname}.metainfo.xml

%files -f %{name}.lang
%{_datadir}/applications/org.%{name}.%{gitname}.desktop
%{_metainfodir}/org.%{name}.%{gitname}.metainfo.xml
%{_bindir}/%{name}*
%{_datadir}/%{name}/
%{_datadir}/icons/hicolor/*/apps/org.%{name}.%{gitname}.*
%license LICENCE

%changelog
* Thu Dec 18 2025 Matrew File <elfile4138@elfile4138.moe> - 3.4.9.20251218-1
- Update to upstream Migration Release 01 Build.
* Wed Apr 16 2025 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.12.20241217-2
- Enable BestSource.
* Tue Dec 17 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.12.20241217-1
- Follow upstream.
* Sun Nov 10 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.12.20241110-1
- Update to upstream Feature Release 12 Build.
* Thu Oct 10 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.11.20241010-1
- Initial Build
