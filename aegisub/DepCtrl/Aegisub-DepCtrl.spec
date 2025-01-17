%global         gituser         TypesettingTools

Name:           Aegisub-DepCtrl
Version:        0.6.4
Release:        1%{?dist}
Summary:        Package manager for scripts for the Aegisub subtitle editor

License:        MIT and ISC
URL:            https://github.com/%{gituser}/DependencyControl

# Supporting library versions
%global depctrl_version %{version}-alpha
%global ffi_experiments_commit b8897ead55b84ec4148e900882bff8336b38f939
%global luajson_ver 1.3.3

Source0:        https://github.com/%{gituser}/DependencyControl/archive/v%{depctrl_version}.tar.gz
Source1:        https://github.com/%{gituser}/ffi-experiments/archive/%{ffi_experiments_commit}.tar.gz
Source2:        https://github.com/harningt/luajson/archive/%{luajson_ver}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  lua-moonscript
BuildRequires:  libcurl-devel

Requires:       Aegisub

%description
Package manager for scripts for the Aegisub subtitle editor.

%prep
mkdir -p DependencyControl ffi-experiments luajson
tar -xzf %{SOURCE0} -C DependencyControl --strip-components=1
tar -xzf %{SOURCE1} -C ffi-experiments --strip-components=1
tar -xzf %{SOURCE2} -C luajson --strip-components=1

%build
# Build ffi-experiments
pushd ffi-experiments
meson build
meson compile -C build
popd

%install
%define PREFIX %{buildroot}/usr/share/aegisub/automation
mkdir -p %{PREFIX}

# Install DependencyControl
pushd DependencyControl
install -d %{PREFIX}/include/l0
cp -r modules/* %{PREFIX}/include/l0
install -D -m 644 macros/* -t %{PREFIX}/autoload
install -D -m 644 LICENSE %{buildroot}/usr/share/licenses/Aegisub/LICENSE_DependencyControl
popd

# Install ffi-experiments
pushd ffi-experiments
install -D -m 644 build/bad-mutex/BadMutex.lua                 %{PREFIX}/include/BM/BadMutex.lua
install -D -m 644 build/bad-mutex/libBadMutex.so               %{PREFIX}/include/BM/BadMutex/libBadMutex.so
install -D -m 644 build/download-manager/DownloadManager.lua   %{PREFIX}/include/DM/DownloadManager.lua
install -D -m 644 build/download-manager/libDownloadManager.so %{PREFIX}/include/DM/DownloadManager/libDownloadManager.so
install -D -m 644 build/precise-timer/PreciseTimer.lua         %{PREFIX}/include/PT/PreciseTimer.lua
install -D -m 644 build/precise-timer/libPreciseTimer.so       %{PREFIX}/include/PT/PreciseTimer/libPreciseTimer.so
install -D -m 644 build/requireffi/requireffi.lua              %{PREFIX}/include/requireffi/requireffi.lua
install -D -m 644 LICENSE %{buildroot}/usr/share/licenses/Aegisub/LICENSE_ffi-experiments
popd

# Install luajson
pushd luajson
install -m 644 lua/json.lua %{PREFIX}/include
cp -r lua/json %{PREFIX}/include
install -D -m 644 LICENSE %{buildroot}/usr/share/licenses/Aegisub/LICENSE_luajson
popd

%files
/usr/share/aegisub/automation/autoload/*
/usr/share/aegisub/automation/include/*
%license /usr/share/licenses/Aegisub/*

%changelog
%autochangelog