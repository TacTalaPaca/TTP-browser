#!/bin/sh
# Arch package. makepkg builds from a generated PKGBUILD that copies the
# staged tree, so no source download is needed.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
. "$ROOT/scripts/packages/common.sh"
stage="$1"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
sed -e "s/@VERSION@/$VERSION/" \
    -e "s/@REVISION@/$REVISION/" \
    -e "s|@DEPENDS@|$ARCH_DEPENDS|" \
    -e "s|@STAGE@|$stage|" \
    "$ROOT/packaging/arch/PKGBUILD.in" > "$work/PKGBUILD"

(
  cd "$work"
  makepkg -f --nodeps --noconfirm
)

cp "$work"/firegila-"${VERSION}"-"${REVISION}"-x86_64.pkg.tar.zst "$OUT/"
echo "arch: firegila-${VERSION}-${REVISION}-x86_64.pkg.tar.zst"
