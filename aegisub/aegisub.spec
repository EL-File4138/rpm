%global         gituser         arch1t3cht
%global         gitname         Aegisub
%global         commit          bf20c62e6b3d88a3e425fc05d26fd2b40e652775
%global         shortcommit     %(c=%{commit}; echo ${c:0:8})
%global         gitdate         20241010

Name:           aegisub
Version:        3.3.4
Release:        11.%{gitdate}%{?dist}
Summary:        Tool for creating and modifying subtitles
License:        BSD and MIT and MPLv1.1
URL:            https://github.com/%{gituser}/%{gitname}

ExcludeArch:    %{power64} %{ix86} %{arm}

BuildRequires:  git
BuildRequires:  desktop-file-utils
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

%description
Aegisub is an advanced subtitle editor which assists in the creation of subtitles,
timing, and editing of subtitle files. It supports a wide range of formats and
provides powerful visual typesetting tools.
This is arch1t3cht's fork, and is actively following for the most recent development
that has a CI success.

%prep
git clone https://github.com/%{gituser}/%{gitname}.git
cd %{gitname}
git checkout %{commit}

%build
cd %{gitname}
mkdir -p build
meson setup build --buildtype=release --prefix=/usr
ninja -C build

%install
cd %{gitname}
DESTDIR=%{buildroot} meson install -C build

%files
# Application Desktop Entry
%{_datadir}/applications/aegisub.desktop
# AppData
%{_datadir}/metainfo/aegisub.appdata.xml
# Translations
%{_datadir}/locale/*/LC_MESSAGES/aegisub.mo
# Executable
%{_bindir}/aegisub
# Automation Autoload Scripts
%{_datadir}/aegisub/automation/*
# Application Icons
%{_datadir}/icons/hicolor/*/apps/aegisub.*

%changelog
* Thu Oct 10 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4-11.20241010
- Initial Build