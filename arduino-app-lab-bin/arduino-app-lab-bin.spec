%global appid cc.arduino.AppLab

# Binary-only repack; no sources to generate debuginfo/debugsource from.
%global debug_package %{nil}

Name:           arduino-app-lab-bin
Version:        0.3.2
Release:        1%{?dist}
Summary:        A powerful visual environment for managing the Arduino UNO Q

Provides:       arduino-app-lab = %{version}-%{release}
URL:            https://www.arduino.cc/en/software
License:        GPL-3.0

Source0:        https://downloads.arduino.cc/AppLab/Stable/ArduinoAppLab_%{version}_Linux_x86-64.tar.gz
Source1:        https://downloads.arduino.cc/AppLab/Stable/source-app-lab-%{version}.zip
Source2:        cc.arduino.AppLab.desktop
Source3:        cc.arduino.AppLab.metainfo.xml

ExclusiveArch:  x86_64

Requires:       android-tools

BuildRequires:  appstream desktop-file-utils unzip

Suggests:       arduino-flasher-cli arduino-app-cli

%description
%summary.

%prep
%setup -q -T -c
tar -xvf %{S:0}
unzip -q %{S:1}

%build
:

%install
install -dm755 %{buildroot}%{_bindir}
install -p -m755 ArduinoAppLab_%{version}_Linux_x86-64/arduino-app-lab %{buildroot}%{_bindir}/%{name}

install -dm755 %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/
install -p -m644 source-app-lab/ui-packages/images/assets/round-arduino-logo.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg

install -dm755 %{buildroot}%{_datadir}/applications/
install -p -m644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{appid}.desktop

install -dm755 %{buildroot}%{_metainfodir}/
install -p -m644 %{SOURCE3} %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

cp source-app-lab/LICENSE -t .
cp source-app-lab/dependency_licenses -t .

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop
appstreamcli validate --no-net %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

%files
%license LICENSE
%license dependency_licenses
%{_bindir}/%{name}
%{_datadir}/icons/hicolor/scalable/apps/%{appid}.svg
%{_datadir}/applications/%{appid}.desktop
%{_metainfodir}/%{appid}.metainfo.xml

%changelog
* Wed Jan 07 2025 Matrew File <elfile4138@elfile4138.moe>
- Update to version 0.3.2
- Rewrite to adhere to normative Fedora packaging guidelines
* Thu Dec 25 2025 Owen Zimmerman <owen@fyralabs.com>
- Add %%check, update macros
* Thu Dec 4 2025 Jaiden Riordan <jade@fyralabs.com>
- Package arduino-app-lab-bin
