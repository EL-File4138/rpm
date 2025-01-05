%global         gituser         TypesettingTools
%global         altname         aegisub

Name:           Aegisub
Version:        3.4.1
Release:        1%{?dist}
Summary:        Tool for creating and modifying subtitles
# Main project is under BSD-3-Clause, some historical code is under ISC, and a few MIT
License:        BSD-3-Clause AND ISC AND MIT
URL:            https://github.com/%{gituser}/%{name}

Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.xz

BuildRequires:  git
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  alsa-lib-devel
BuildRequires:  boost-devel
BuildRequires:  ffms2-devel >= 2.40
BuildRequires:  fftw-devel
BuildRequires:  hunspell-devel
BuildRequires:  intltool
BuildRequires:  libass-devel
BuildRequires:  lua-devel
BuildRequires:  luajit-devel
BuildRequires:  portaudio-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  wxGTK-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  libX11-devel
BuildRequires:  uchardet-devel
BuildRequires:  openal-soft-devel
BuildRequires:  libcurl-devel
BuildRequires:  jansson-devel
BuildRequires:  gtest-devel
BuildRequires:  gmock-devel

%description
Aegisub is an advanced subtitle editor which assists in the creation of
subtitles, timing, and editing of subtitle files. It supports a wide range
of formats and provides powerful visual typesetting tools.

%prep
%autosetup
# Strip out unused bundled library
# Remaining `luabins` is not included in Fedora Package registry, and does not provide additional shared library
find subprojects/ -mindepth 1 ! -path "subprojects/luabins*" -exec rm -rf {} +
# Strip unused packaging artifacts for other platform, which contains GPL code
rm -rf packages/{osx_bundle,osx_dmg,win_installer}
rm -rf tools/{osx-*,apply-manifest.py,*.ps1}
rm -rf osx-bundle.sed

%build
%meson
%meson_build

%install
%meson_install

%find_lang %{altname}

desktop-file-validate %{buildroot}%{_datadir}/applications/org.%{altname}.%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/org.%{altname}.%{name}.metainfo.xml

%files -f %{altname}.lang
# Application Desktop Entry
%{_datadir}/applications/org.%{altname}.%{name}.desktop
# metainfo
%{_metainfodir}/org.%{altname}.%{name}.metainfo.xml
# Executable
%{_bindir}/%{altname}*
# Plugins
%{_datadir}/%{altname}/
# Application Icons
%{_datadir}/icons/hicolor/*/apps/org.%{altname}.%{name}.*
# License
%license LICENCE

%changelog
%autochangelog