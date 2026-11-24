#!/bin/sh
# AppImage. Downloads the pinned appimagetool, verifies it, and builds a
# portable image from the same staged tree as the other formats.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
. "$ROOT/scripts/packages/common.sh"

stage="$1"
tool_dir="$ROOT/build/tools"
tool="$tool_dir/appimagetool-x86_64.AppImage"
tool_url="https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-x86_64.AppImage"
tool_sum="$ROOT/packaging/appimage/appimagetool.sha256"

mkdir -p "$tool_dir"
if [ ! -f "$tool" ]; then
  echo "appimage: downloading appimagetool 1.9.1"
  curl -L "$tool_url" -o "$tool"
fi
chmod +x "$tool"
(
  cd "$tool_dir"
  sha256sum -c "$tool_sum"
)

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
appdir="$work/Firegila.AppDir"
mkdir -p "$appdir"
cp -a "$stage"/. "$appdir"/
cp "$ROOT/assets/firegila.desktop" "$appdir/firegila.desktop"
cp "$ROOT/assets/icons/firegila-512.png" "$appdir/firegila.png"
cp "$ROOT/packaging/appimage/AppRun" "$appdir/AppRun"
chmod +x "$appdir/AppRun"
ln -sf firegila.png "$appdir/.DirIcon"

out="$OUT/Firegila-${VERSION}-x86_64.AppImage"
rm -f "$out"
if ! ARCH=x86_64 "$tool" --no-appstream "$appdir" "$out"; then
  echo "appimage: retrying with an extracted appimagetool"
  rm -rf "$tool_dir/squashfs-root"
  (
    cd "$tool_dir"
    "$tool" --appimage-extract >/dev/null
  )
  ARCH=x86_64 "$tool_dir/squashfs-root/AppRun" --no-appstream \
    "$appdir" "$out"
  rm -rf "$tool_dir/squashfs-root"
fi
echo "appimage: $(basename "$out")"
