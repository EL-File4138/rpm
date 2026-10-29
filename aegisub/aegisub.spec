%global         gituser         arch1t3cht
%global         gitname         Aegisub
%global         commit          aff013f45d1aeb5ac6d3f6ea9c972278d29eb777
%global         shortcommit     %(c=%{commit}; echo ${c:0:8})
%global         gitdate         20261018
%global         upstream_tag    migration06-01

Name:           aegisub
Version:        3.5.1.%{gitdate}
Release:        1%{?dist}
Summary:        Tool for creating and modifying subtitles
License:        BSD-3-Clause AND ISC AND MIT
URL:            https://github.com/%{gituser}/%{gitname}

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
BuildRequires:  pkgconfig(libportal-gtk3)

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
%autosetup -n %{gitname}-%{commit} -p1

# GitHub archives lack the cached version header normally supplied by meson dist.
# Use revision 0, as upstream does when Git history is unavailable.
cat > git_version.h <<'EOF'
#define BUILD_GIT_VERSION_NUMBER 0
#define BUILD_GIT_VERSION_STRING "%{upstream_tag}"
#define TAGGED_RELEASE 1
#define INSTALLER_VERSION "0.0.0"
#define RESOURCE_BASE_VERSION 0, 0, 0
EOF

# Keep only the required bundled luabins; all other dependencies are system libraries.
find subprojects/ -mindepth 1 -depth ! -path "subprojects/luabins*" -exec rm -rv {} +
# Remove unused platform packaging containing GPL code and developer documentation.
rm -rv packages/{osx_bundle,osx_dmg,win_installer}
rm -rv tools/{osx-*,*.ps1}
rm -rv docs/

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
* Thu Oct 29 2026 Matrew File <elfile4138@elfile4138.moe> - 3.5.1.20261018-1
- Update to Migration Release 06, based on Aegisub 3.5.1.
- Fix archive extraction and supply version metadata for builds without Git.
- Remove unused bundled dependencies and platform packaging; update license.
* Sat Jul 11 2026 Matrew File <elfile4138@elfile4138.moe> - 3.4.9.20260711-1
- Update to upstream Migration Release 04 Build.
* Fri May 29 2026 Matrew File <elfile4138@elfile4138.moe> - 3.4.9.20260529-1
- Update to upstream Migration Release 03 Build.
* Wed Jan 07 2026 Matrew File <elfile4138@elfile4138.moe> - 3.4.9.20260106-1
- Update to upstream Migration Release 02 Build.
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
