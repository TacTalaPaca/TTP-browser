#!/bin/sh
# Install a packaged tarball into PREFIX, default ~/.local.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="$(tr -d ' \n' < "$ROOT/VERSION")"
TAR="${1:-$ROOT/packages/$VER/firegila-${VER}-linux-x86_64.tar.xz}"
PREFIX="${PREFIX:-$HOME/.local}"

[ -f "$TAR" ] || { echo "install: missing $TAR (run package.sh)"; exit 1; }

mkdir -p "$PREFIX/lib" "$PREFIX/bin" "$PREFIX/share/applications" "$PREFIX/share/icons/hicolor/512x512/apps"
rm -rf "$PREFIX/lib/firegila"
tar -xf "$TAR" -C "$PREFIX/lib"
ln -sf "$PREFIX/lib/firegila/firegila" "$PREFIX/bin/firegila"
cp "$PREFIX/lib/firegila/firegila.desktop" "$PREFIX/share/applications/firegila.desktop"
sed -i "s|^Exec=.*|Exec=$PREFIX/bin/firegila %u|" "$PREFIX/share/applications/firegila.desktop"
cp "$PREFIX/lib/firegila/icons/firegila.png" "$PREFIX/share/icons/hicolor/512x512/apps/firegila.png"
command -v update-desktop-database >/dev/null && update-desktop-database "$PREFIX/share/applications" || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -f -t "$PREFIX/share/icons/hicolor" || true
echo "install: Firegila installed. Run: firegila"
