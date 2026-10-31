#!/bin/sh
# Portable tarball. Contains the app tree, desktop file and 512px icon.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
. "$ROOT/scripts/packages/common.sh"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cp -a "$BUILD" "$tmp/firegila"
cp "$ROOT/branding/firegila.desktop" "$tmp/firegila/firegila.desktop"
mkdir -p "$tmp/firegila/icons"
cp "$ROOT/app-icons/firegila-512.png" "$tmp/firegila/icons/firegila.png"
tar -cJf "$OUT/firegila-${VERSION}-linux-x86_64.tar.xz" -C "$tmp" firegila
echo "tarball: firegila-${VERSION}-linux-x86_64.tar.xz"
