{pkgs}: {
  deps = [
    pkgs.gcc
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
    pkgs.opencl-headers
    pkgs.ocl-icd
    pkgs.glibcLocales
    pkgs.re2
    pkgs.oneDNN
    pkgs.gtest
    pkgs.abseil-cpp
    pkgs.postgresql
    pkgs.openssl
  ];
}
