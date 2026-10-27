%global _smp_build_ncpus 1

Name:           wasm-bindgen-cli
Version:        0.2.129
Release:        1%{?dist}
Summary:        Generate JavaScript bindings for Rust WebAssembly modules
# Includes statically linked dependencies; see bundled-licenses.txt.
License:        MIT AND Apache-2.0 AND ISC AND BSD-3-Clause AND Unicode-3.0 AND Zlib AND CDLA-Permissive-2.0
URL:            https://github.com/wasm-bindgen/wasm-bindgen
Source0:        https://static.crates.io/crates/%{name}/%{name}-%{version}.crate
# Generated from Source0's Cargo.lock with ../packaging/prepare-rust-vendor.py.
Source1:        %{name}-%{version}-vendor.tar.xz
Source2:        bundled-licenses.txt
Source3:        bundled-provides.inc

BuildRequires:  rust >= 1.86
BuildRequires:  cargo >= 1.86
BuildRequires:  gcc

%include %{SOURCE3}

%description
Generate JavaScript interfaces for Rust WebAssembly modules. The binding
generator version must match the wasm-bindgen crate used by the module.
The generated JavaScript is loaded by the application; this command is
needed only while building bindings.

%prep
%autosetup -n %{name}-%{version}
%setup -q -T -D -a 1 -n %{name}-%{version}
mkdir -p .cargo
cp vendor-config.toml .cargo/config.toml
# Some crate archives mark Rust sources executable. Debugsource preserves these
# modes, causing RPM's shebang check to interpret Rust attributes as scripts.
find . -type f -name '*.rs' -exec chmod a-x {} +

%build
export CARGO_HOME="$PWD/cargo-home"
export CARGO_NET_OFFLINE=true
export CARGO_BUILD_JOBS=%{_smp_build_ncpus}
export RUSTFLAGS="%{build_rustflags}"
cargo build --frozen --release --bin wasm-bindgen

%install
install -Dpm 0755 target/release/wasm-bindgen %{buildroot}%{_bindir}/wasm-bindgen
install -pm 0644 %{SOURCE2} bundled-licenses.txt

%check
test "$(target/release/wasm-bindgen --version)" = "wasm-bindgen %{version}"

%files
%license LICENSE-MIT LICENSE-APACHE bundled-licenses.txt
%{_bindir}/wasm-bindgen

%changelog
* Sun Sep 27 2026 Matrew File <elfile4138@elfile4138.moe> - 0.2.129-1
- Build the binding generator from locked, offline Rust sources.
