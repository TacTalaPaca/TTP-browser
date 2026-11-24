#!/bin/sh
# Shared package build data. Sourced by package.sh and the format scripts.
set -eu

if [ -z "${ROOT:-}" ]; then
  ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
fi
VERSION="$(tr -d ' \n' < "$ROOT/VERSION")"
ESR="$(tr -d ' \n' < "$ROOT/ESR_VERSION")"
REVISION="1"
BUILD="$ROOT/build/firefox"
OUT="$ROOT/dist"
ARCH="x86_64"
DEB_ARCH="amd64"
MAINTAINER="David Danuja <contact@tactalapaca.com>"
VENDOR="TacTalaPaca"
HOMEPAGE="https://github.com/TacTalaPaca/TTP-browser"
SUMMARY="Neutral web browser based on Firefox ESR"
LICENSE_MPL="MPL-2.0"
LICENSE_GPL="GPL-3.0-or-later"
LICENSE="$LICENSE_MPL AND $LICENSE_GPL"

# System libraries used by the bundled libxul. The tarball ships its own NSS,
# NSPR, AV codecs, sqlite and onnxruntime, so those are not listed.
DEB_DEPENDS="libgtk-3-0, libdbus-glib-1-2, libasound2, libpulse0, libx11-6, libx11-xcb1, libxcb1, libxcb-shm0, libxcomposite1, libxdamage1, libxfixes3, libxrandr2, libxt6, libgbm1, libdrm2, libglib2.0-0, libstdc++6, libatomic1, libfontconfig1, libfreetype6, libharfbuzz0b, libsqlite3-0, libxkbcommon0, libpango-1.0-0, libcairo2, libgdk-pixbuf-2.0-0, libatk1.0-0, libatk-bridge2.0-0, libatspi2.0-0, libepoxy0, libseccomp2, libffi8, libexpat1, libbz2-1.0, libbrotli1, libjson-glib-1.0-0, libcloudproviders0"
RPM_DEPENDS="libgtk-3.so.0()(64bit) libdbus-glib-1.so.2()(64bit) libasound.so.2()(64bit) libpulse.so.0()(64bit) libX11.so.6()(64bit) libX11-xcb.so.1()(64bit) libxcb.so.1()(64bit) libXcomposite.so.1()(64bit) libXdamage.so.1()(64bit) libXfixes.so.3()(64bit) libXrandr.so.2()(64bit) libXt.so.6()(64bit) libgbm.so.1()(64bit) libdrm.so.2()(64bit) libglib-2.0.so.0()(64bit) libstdc++.so.6()(64bit) libatomic.so.1()(64bit) libfontconfig.so.1()(64bit) libfreetype.so.6()(64bit) libharfbuzz.so.0()(64bit) libsqlite3.so.0()(64bit) libxkbcommon.so.0()(64bit) libpango-1.0.so.0()(64bit) libcairo.so.2()(64bit) libgdk_pixbuf-2.0.so.0()(64bit) libatk-1.0.so.0()(64bit) libatk-bridge-2.0.so.0()(64bit) libatspi.so.0()(64bit) libepoxy.so.0()(64bit) libseccomp.so.2()(64bit) libffi.so.8()(64bit) libexpat.so.1()(64bit) libbz2.so.1()(64bit) libbrotlidec.so.1()(64bit) libjson-glib-1.0.so.0()(64bit) libcloudproviders.so.0()(64bit)"
ARCH_DEPENDS="gtk3 dbus-glib alsa-lib libpulse libx11 libxcb libxcomposite libxdamage libxfixes libxrandr libxt mesa libdrm glib2 gcc-libs fontconfig freetype2 harfbuzz sqlite libxkbcommon pango cairo gdk-pixbuf2 atk at-spi2-core libepoxy libseccomp libffi expat bzip2 brotli json-glib libcloudproviders"

require_build() {
  [ -x "$BUILD/firegila" ] || {
    echo "package: run customize.sh first" >&2
    exit 1
  }
}

# Release bullets for the current version, without the Markdown dash.
changelog_bullets() {
  awk -v ver="$VERSION" '
    $0 == "## " ver { found = 1; next }
    found && /^## / { exit }
    found && /^- / { sub(/^- /, ""); print }
  ' "$ROOT/CHANGELOG.md"
}

prepare_out() {
  rm -rf "$OUT"
  mkdir -p "$OUT"
}

# One staging root for every package format. The result is a normal /usr tree.
stage_root() {
  dest="$1"
  rm -rf "$dest"
  mkdir -p "$dest/usr/lib" "$dest/usr/bin" \
    "$dest/usr/share/applications" "$dest/usr/share/metainfo" \
    "$dest/usr/share/doc/firegila"
  cp -a "$BUILD" "$dest/usr/lib/firegila"
  rm -f "$dest/usr/lib/firegila/firegila.desktop"
  rm -rf "$dest/usr/lib/firegila/icons"
  ln -s ../lib/firegila/firegila "$dest/usr/bin/firegila"
  cp "$ROOT/assets/firegila.desktop" \
    "$dest/usr/share/applications/firegila.desktop"
  for size in 16 32 48 64 128; do
    icon="$BUILD/browser/chrome/icons/default/default${size}.png"
    if [ -f "$icon" ]; then
      mkdir -p "$dest/usr/share/icons/hicolor/${size}x${size}/apps"
      cp "$icon" "$dest/usr/share/icons/hicolor/${size}x${size}/apps/firegila.png"
    fi
  done
  mkdir -p "$dest/usr/share/icons/hicolor/512x512/apps"
  cp "$ROOT/assets/icons/firegila-512.png" \
    "$dest/usr/share/icons/hicolor/512x512/apps/firegila.png"
  cp "$ROOT/packaging/common/org.firegila.Firegila.metainfo.xml" \
    "$dest/usr/share/metainfo/org.firegila.Firegila.metainfo.xml"
  cp "$ROOT/README.md" "$ROOT/LICENSE" "$ROOT/CHANGELOG.md" \
    "$dest/usr/share/doc/firegila/"
  cp "$ROOT/packaging/common/copyright" \
    "$dest/usr/share/doc/firegila/copyright"
}

write_sums() {
  (
    cd "$OUT"
    find . -maxdepth 1 -type f ! -name SHA256SUMS -printf '%f\n' |
      sort |
      while read -r file; do
        sha256sum "$file"
      done > SHA256SUMS
  )
}
