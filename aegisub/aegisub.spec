%global         gituser         TypesettingTools
%global         altname         aegisub

Name:           Aegisub
Version:        3.4.1
Release:        1%{?dist}
Summary:        Tool for creating and modifying subtitles
License:        BSD and MIT and MPLv1.1
URL:            https://github.com/%{gituser}/%{name}

Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.xz
Source1:        https://github.com/EL-File4138/rpm/raw/refs/heads/master/aegisub/wrapper.sh

ExcludeArch:    %{power64} %{ix86} %{arm}

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
BuildRequires:  libGL-devel
BuildRequires:  libX11-devel
BuildRequires:  uchardet-devel
BuildRequires:  openal-soft-devel
BuildRequires:  libcurl-devel
BuildRequires:  jansson-devel
BuildRequires:  gtest-devel
BuildRequires:  gmock-devel

%description
Aegisub is an advanced subtitle editor which assists in the creation of subtitles,
timing, and editing of subtitle files. It supports a wide range of formats and
provides powerful visual typesetting tools.

%prep
%autosetup

cp %{SOURCE1} wrapper.sh

%build
%meson
%meson_build

%install
%meson_install

mkdir -p %{buildroot}%{_prefix}/local/bin
install -m 755 wrapper.sh %{buildroot}%{_prefix}/local/bin/%{altname}

desktop-file-validate %{buildroot}%{_datadir}/applications/org.%{altname}.%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/org.%{altname}.%{name}.metainfo.xml

%files
# Application Desktop Entry
%{_datadir}/applications/org.%{altname}.%{name}.desktop
# metainfo
%{_metainfodir}/org.%{altname}.%{name}.metainfo.xml
# Translations
%{_datadir}/locale/*/LC_MESSAGES/%{altname}.mo
# Executable
%{_bindir}/%{altname}*
%{_prefix}/local/bin/%{altname}
# Automation Autoload Scripts
%{_datadir}/%{altname}/automation/*
# Application Icons
%{_datadir}/icons/hicolor/*/apps/org.%{altname}.%{name}.*

%changelog
%autochangelog