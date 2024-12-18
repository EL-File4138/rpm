%global         gituser         arch1t3cht
%global         gitname         Aegisub
%global         commit          7db477c3ed31389e678844dde54f032fd1603fea
%global         shortcommit     %(c=%{commit}; echo ${c:0:8})
%global         gitdate         20241110

Name:           aegisub
Version:        3.3.4.12.%{gitdate}
Release:        1%{?dist}
Summary:        Tool for creating and modifying subtitles
License:        BSD and MIT and MPLv1.1
URL:            https://github.com/%{gituser}/%{gitname}

Source0:        %{url}/archive/%{commit}/%{gitname}-%{shortcommit}.tar.gz
Source1:        https://github.com/EL-File4138/rpm/raw/refs/heads/master/aegisub/wrapper.sh

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
BuildRequires:  uchardet-devel
BuildRequires:  jansson-devel

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

cp %{SOURCE1} wrapper.sh

%build
cd %{gitname}
mkdir -p build
meson setup build --buildtype=release --prefix=/usr
ninja -C build

%install
cd %{gitname}
DESTDIR=%{buildroot} meson install -C build

mkdir -p %{buildroot}%{_prefix}/local/bin
install -m 755 wrapper.sh %{buildroot}%{_prefix}/local/bin/aegisub

%files
# Application Desktop Entry
%{_datadir}/applications/aegisub.desktop
# AppData
%{_datadir}/metainfo/aegisub.appdata.xml
# Translations
%{_datadir}/locale/*/LC_MESSAGES/aegisub.mo
# Executable
%{_bindir}/aegisub
%{_prefix}/local/bin/aegisub
# Automation Autoload Scripts
%{_datadir}/aegisub/automation/*
# Application Icons
%{_datadir}/icons/hicolor/*/apps/aegisub.*

%changelog
* Tue Dec 17 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.12.20241217
- Follow upstream.
* Sun Nov 10 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.12.20241110
- Update to upstream Feature Release 12 Build.
* Thu Oct 10 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.11.20241010
- Initial Build
