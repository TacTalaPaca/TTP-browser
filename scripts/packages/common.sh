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
OUT="$ROOT/packages/$VERSION"
ARCH="x86_64"
DEB_ARCH="amd64"

# System libraries used by the bundled libxul. The tarball ships its own NSS,
# NSPR, AV codecs, sqlite and onnxruntime, so those are not listed.
DEB_DEPENDS="libgtk-3-0, libdbus-glib-1-2, libasound2, libpulse0, libx11-6, libx11-xcb1, libxcb1, libxcb-shm0, libxcomposite1, libxdamage1, libxfixes3, libxrandr2, libxt6, libgbm1, libdrm2, libglib2.0-0, libstdc++6, libatomic1, libfontconfig1, libfreetype6, libharfbuzz0b, libsqlite3-0, libxkbcommon0, libpango-1.0-0, libcairo2, libgdk-pixbuf-2.0-0, libatk1.0-0, libatk-bridge2.0-0, libatspi2.0-0, libepoxy0, libseccomp2, libffi8, libexpat1, libbz2-1.0, libbrotli1, libjson-glib-1.0-0, libcloudproviders0"
RPM_DEPENDS="gtk3 dbus-glib alsa-lib pulseaudio-libs libX11 libX11-xcb libxcb libXcomposite libXdamage libXfixes libXrandr libXt mesa-libgbm libdrm glib2 libstdc++ libatomic fontconfig freetype harfbuzz sqlite-libs libxkbcommon pango cairo gdk-pixbuf2 atk at-spi2-core libepoxy libseccomp libffi expat bzip2-libs brotli json-glib libcloudproviders"
ARCH_DEPENDS="gtk3 dbus-glib alsa-lib libpulse libx11 libxcb libxcomposite libxdamage libxfixes libxrandr libxt mesa libdrm glib2 gcc-libs fontconfig freetype2 harfbuzz sqlite libxkbcommon pango cairo gdk-pixbuf2 atk at-spi2-core libepoxy libseccomp libffi expat bzip2 brotli json-glib libcloudproviders"

require_build() {
  [ -x "$BUILD/firegila" ] || {
    echo "package: run customize.sh first" >&2
    exit 1
  }
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
  cp "$ROOT/branding/firegila.desktop" \
    "$dest/usr/share/applications/firegila.desktop"
  for size in 16 32 48 64 128; do
    icon="$BUILD/browser/chrome/icons/default/default${size}.png"
    if [ -f "$icon" ]; then
      mkdir -p "$dest/usr/share/icons/hicolor/${size}x${size}/apps"
      cp "$icon" "$dest/usr/share/icons/hicolor/${size}x${size}/apps/firegila.png"
    fi
  done
  mkdir -p "$dest/usr/share/icons/hicolor/512x512/apps"
  cp "$ROOT/app-icons/firegila-512.png" \
    "$dest/usr/share/icons/hicolor/512x512/apps/firegila.png"
  cp "$ROOT/packaging/common/org.firegila.Firegila.metainfo.xml" \
    "$dest/usr/share/metainfo/org.firegila.Firegila.metainfo.xml"
  cp "$ROOT/README.md" "$ROOT/LICENSE" "$dest/usr/share/doc/firegila/"
}

write_buildinfo() {
  {
    echo "product=$VERSION"
    echo "esr=$ESR"
    echo "revision=$REVISION"
    echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "commit=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo none)"
    echo "host=$(uname -srm)"
  } > "$OUT/BUILDINFO"
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
