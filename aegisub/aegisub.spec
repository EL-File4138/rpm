%global         gituser         TypesettingTools
%global         gitname         Aegisub
%global         commit          b0fc741099f610ee9486bfaf0186d39f74b8d756
%global         shortcommit     %(c=%{commit}; echo ${c:0:8})
%global         gitdate         20241110

Name:           aegisub
Version:        3.4.0
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
BuildRequires:  openal-soft-devel
BuildRequires:  libcurl-devel
BuildRequires:  jansson-devel
BuildRequires:  libappstream-glib

%description
Aegisub is an advanced subtitle editor which assists in the creation of subtitles,
timing, and editing of subtitle files. It supports a wide range of formats and
provides powerful visual typesetting tools.

%prep
git clone https://github.com/%{gituser}/%{gitname}.git
cd %{gitname}
git checkout %{commit}

cp %{SOURCE1} wrapper.sh

mkdir -p build

meson subprojects download gtest

%build
cd %{gitname}
%meson
%meson_build

%install
cd %{gitname}
%meson_install

mkdir -p %{buildroot}%{_prefix}/local/bin
install -m 755 wrapper.sh %{buildroot}%{_prefix}/local/bin/%{name}

desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}/%{_metainfodir}/%{name}.appdata.xml

%files
# Application Desktop Entry
%{_datadir}/applications/%{name}.desktop
# AppData
%{_metainfodir}/%{name}.appdata.xml
# Translations
%{_datadir}/locale/*/LC_MESSAGES/%{name}.mo
# Executable
%{_bindir}/%{name}*
%{_prefix}/local/bin/%{name}
# Automation Autoload Scripts
%{_datadir}/%{name}/automation/*
# Application Icons
%{_datadir}/icons/hicolor/*/apps/%{name}.*

%changelog
* Thu Dec 19 2024 Matrew File <elfile4138@elfile4138.moe> - 3.4.0
- Rebase to new major upstream.
* Tue Dec 17 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.12.20241217
- Follow upstream.
* Sun Nov 10 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.12.20241110
- Update to upstream Feature Release 12 Build.
* Thu Oct 10 2024 Matrew File <elfile4138@elfile4138.moe> - 3.3.4.11.20241010
- Initial Build
