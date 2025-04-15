{pkgs}: {
  deps = [
    pkgs.nodejs
    pkgs.geckodriver
    pkgs.firefox
    pkgs.arrow-cpp
    pkgs.py-spy
    pkgs.gtest
    pkgs.abseil-cpp
    pkgs.opencl-headers
    pkgs.ocl-icd
    pkgs.tk
    pkgs.tcl
    pkgs.qhull
    pkgs.pkg-config
    pkgs.gtk3
    pkgs.gobject-introspection
    pkgs.ghostscript
    pkgs.freetype
    pkgs.ffmpeg-full
    pkgs.cairo
    pkgs.glibcLocales
    pkgs.postgresql
    pkgs.openssl
  ];
}
