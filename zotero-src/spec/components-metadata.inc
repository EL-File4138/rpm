# Build requirements for the private source stages. Runtime bundled Provides
# remain scoped to the shipped inventory in zotero.spec, not whole vendor trees.
%if 0%{?fedora} > 44
BuildRequires: binaryen125
%else
BuildRequires: binaryen >= 125
%endif
BuildRequires: bzip2
BuildRequires: cargo >= 1.88
BuildRequires: cmake
BuildRequires: emscripten-core = 4.0.22
BuildRequires: fontforge
BuildRequires: fonttools
BuildRequires: gcc
BuildRequires: java-devel >= 17
BuildRequires: javapackages-filesystem
BuildRequires: libreoffice-ure-common >= 26.2
BuildRequires: mftrace
BuildRequires: mvn(com.fasterxml.jackson.core:jackson-annotations)
BuildRequires: mvn(com.fasterxml.jackson.core:jackson-core)
BuildRequires: mvn(com.fasterxml.jackson.core:jackson-databind)
BuildRequires: mvn(net.java.dev.jna:jna)
BuildRequires: patch
BuildRequires: perl(JSON)
BuildRequires: potrace
BuildRequires: python3-brotli
BuildRequires: python3-zopfli
BuildRequires: rust >= 1.88
BuildRequires: rust-std-static-wasm32-unknown-unknown
BuildRequires: t1utils
BuildRequires: tar
BuildRequires: texlive-amsfonts
BuildRequires: texlive-cm
BuildRequires: texlive-dvips
BuildRequires: texlive-metafont
BuildRequires: texlive-rsfs
BuildRequires: texlive-texlive-scripts
BuildRequires: ttfautohint
BuildRequires: wasm-bindgen-cli = 0.2.129
BuildRequires: which
